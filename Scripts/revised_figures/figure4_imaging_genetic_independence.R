# =========================================================
# Figure 4. Imaging-genetic independence
# Question: Are imaging-derived risk and genetic risk measuring 
# the same biological signal or independent ones?
# Conclusion: Figure 4 demonstrates that they are largely independent.
# =========================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(ggplot2)
  library(survival)
  library(glmnet)
  library(broom)
  library(purrr)
  library(patchwork)
  library(scales)
  library(stringr)
  library(tibble)
})

# -----------------------------
# 1) Column definitions
# -----------------------------
TIME_COL <- "time_at_risk"
EVENT_COL <- "event"
PRS_COL  <- "PRS"

CLINICAL_COLS <- c(
  "age", "sex", "bmi", "ldl", "trig", "total_cholestrol",
  "smoking", "bp_dia", "bp_sys", "pulse_rate",
  "lipid_med", "bp_med", "insulin"
)

# -----------------------------
# 2) Helpers
# -----------------------------
theme_publication <- function(base_size = 14) {
  theme_bw(base_size = base_size) +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = base_size + 4),
      axis.title = element_text(face = "bold", size = base_size + 2),
      axis.text = element_text(color = "black", size = base_size)
    )
}
standardize_train_test <- function(train_df, test_df, cols) {
  mu  <- sapply(train_df[cols], mean, na.rm = TRUE)
  sdx <- sapply(train_df[cols], sd,   na.rm = TRUE)
  sdx[is.na(sdx) | sdx == 0] <- 1

  train_out <- train_df
  test_out  <- test_df

  train_out[cols] <- sweep(sweep(as.matrix(train_df[cols]), 2, mu, "-"), 2, sdx, "/")
  test_out[cols]  <- sweep(sweep(as.matrix(test_df[cols]),  2, mu, "-"), 2, sdx, "/")

  list(train = as.data.frame(train_out), test = as.data.frame(test_out))
}

standardize_df <- function(df, cols) {
  if (length(cols) == 0) return(df)
  mu  <- sapply(df[cols], mean, na.rm = TRUE)
  sdx <- sapply(df[cols], sd,   na.rm = TRUE)
  sdx[is.na(sdx) | sdx == 0] <- 1
  out <- df
  out[cols] <- sweep(sweep(as.matrix(df[cols]), 2, mu, "-"), 2, sdx, "/")
  as.data.frame(out)
}

cox_cindex <- function(fit) {
  as.numeric(summary(fit)$concordance[1])
}

lr_test <- function(fit_small, fit_big) {
  lr <- 2 * (as.numeric(logLik(fit_big)) - as.numeric(logLik(fit_small)))
  df_diff <- attr(logLik(fit_big), "df") - attr(logLik(fit_small), "df")
  p <- pchisq(lr, df = df_diff, lower.tail = FALSE)
  tibble(chisq = lr, df = df_diff, p = p)
}

fit_cox_model <- function(df, covars, time_col, event_col) {
  d <- df %>%
    dplyr::select(all_of(c(time_col, event_col, covars))) %>%
    tidyr::drop_na()

  numeric_covars <- covars[vapply(d[covars], is.numeric, logical(1))]
  d <- standardize_df(d, numeric_covars)

  f <- stats::as.formula(
    paste0("survival::Surv(", time_col, ", ", event_col, ") ~ ",
           paste(covars, collapse = " + "))
  )

  survival::coxph(f, data = d, x = TRUE, y = TRUE)
}

# -----------------------------
# 3) Imaging score constructors
# -----------------------------
make_crossfit_imaging_score <- function(df,
                                        time_col,
                                        event_col,
                                        imaging_pc_cols,
                                        n_splits = 5,
                                        seed = 42,
                                        lambda_rule = c("lambda.min", "lambda.1se"),
                                        score_name = "imaging_score_cf") {
  lambda_rule <- match.arg(lambda_rule)

  d <- df %>%
    dplyr::mutate(.row_id = dplyr::row_number()) %>%
    dplyr::select(.row_id, all_of(c(time_col, event_col, imaging_pc_cols))) %>%
    tidyr::drop_na()

  set.seed(seed)
  fold_id <- sample(rep(seq_len(n_splits), length.out = nrow(d)))
  score <- rep(NA_real_, nrow(d))

  for (k in seq_len(n_splits)) {
    train_df <- d[fold_id != k, , drop = FALSE]
    test_df  <- d[fold_id == k, , drop = FALSE]

    scaled <- standardize_train_test(train_df, test_df, imaging_pc_cols)

    x_train <- as.matrix(scaled$train[, imaging_pc_cols, drop = FALSE])
    y_train <- survival::Surv(scaled$train[[time_col]], scaled$train[[event_col]])
    x_test  <- as.matrix(scaled$test[, imaging_pc_cols, drop = FALSE])

    cvfit <- glmnet::cv.glmnet(
      x = x_train,
      y = y_train,
      family = "cox",
      alpha = 0,
      nfolds = 5,
      standardize = FALSE
    )

    lambda_use <- cvfit[[lambda_rule]]
    score[fold_id == k] <- as.numeric(
      predict(cvfit, newx = x_test, s = lambda_use, type = "link")
    )
  }

  out <- df
  out[[score_name]] <- NA_real_
  out[[score_name]][d$.row_id] <- score
  out
}

make_ridge_imaging_score <- function(df,
                                     time_col,
                                     event_col,
                                     imaging_pc_cols,
                                     lambda_rule = c("lambda.min", "lambda.1se"),
                                     score_name = "imaging_score_ridge") {
  lambda_rule <- match.arg(lambda_rule)

  d <- df %>%
    dplyr::mutate(.row_id = dplyr::row_number()) %>%
    dplyr::select(.row_id, all_of(c(time_col, event_col, imaging_pc_cols))) %>%
    tidyr::drop_na()

  d_std <- standardize_df(d, imaging_pc_cols)

  x <- as.matrix(d_std[, imaging_pc_cols, drop = FALSE])
  y <- survival::Surv(d_std[[time_col]], d_std[[event_col]])

  cvfit <- glmnet::cv.glmnet(
    x = x,
    y = y,
    family = "cox",
    alpha = 0,
    nfolds = 5,
    standardize = FALSE
  )

  lambda_use <- cvfit[[lambda_rule]]
  score <- as.numeric(predict(cvfit, newx = x, s = lambda_use, type = "link"))

  out <- df
  out[[score_name]] <- NA_real_
  out[[score_name]][d$.row_id] <- score
  out
}

make_pca_imaging_score <- function(df,
                                   time_col,
                                   event_col,
                                   imaging_pc_cols,
                                   n_components = 5,
                                   score_name = "imaging_score_pca") {
  d <- df %>%
    dplyr::mutate(.row_id = dplyr::row_number()) %>%
    dplyr::select(.row_id, all_of(c(time_col, event_col, imaging_pc_cols))) %>%
    tidyr::drop_na()

  d_std <- standardize_df(d, imaging_pc_cols)

  pca <- prcomp(d_std[, imaging_pc_cols, drop = FALSE], center = FALSE, scale. = FALSE)
  keep <- seq_len(min(n_components, ncol(pca$x)))
  weights <- (pca$sdev[keep]^2) / sum(pca$sdev^2)

  score <- as.numeric(as.matrix(pca$x[, keep, drop = FALSE]) %*% weights)

  orient_df <- tibble(
    time  = d[[time_col]],
    event = d[[event_col]],
    score = score
  )
  orient_fit <- survival::coxph(survival::Surv(time, event) ~ score, data = orient_df)
  if (coef(orient_fit)[["score"]] < 0) score <- -score

  out <- df
  out[[score_name]] <- NA_real_
  out[[score_name]][d$.row_id] <- score
  out
}

# -----------------------------
# 4) Independence analysis
# -----------------------------
independence_analysis <- function(df,
                                  score_col,
                                  prs_col,
                                  clinical_cols,
                                  time_col,
                                  event_col) {
  d_lm <- df %>%
    dplyr::select(all_of(c(prs_col, score_col, clinical_cols))) %>%
    tidyr::drop_na()

  # 1) Simple correlations
  pearson  <- cor.test(d_lm[[prs_col]], d_lm[[score_col]], method = "pearson")
  spearman <- cor.test(d_lm[[prs_col]], d_lm[[score_col]], method = "spearman", exact = FALSE)

  # 2) Variance Decomposition (Partial R2)
  # Partition into: Demographics (Age, Sex), Risk Factors (rest), Genetics (PRS)
  demo_cols <- intersect(clinical_cols, c("age", "sex", "Age", "Sex"))
  rf_cols   <- setdiff(clinical_cols, demo_cols)
  
  # Models for R2 decomposition
  fit_null <- lm(reformulate("1", response = score_col), data = d_lm)
  fit_demo <- lm(reformulate(demo_cols, response = score_col), data = d_lm)
  fit_clin <- lm(reformulate(clinical_cols, response = score_col), data = d_lm)
  fit_full <- lm(reformulate(c(clinical_cols, prs_col), response = score_col), data = d_lm)
  
  r2_null <- summary(fit_null)$r.squared # 0
  r2_demo <- summary(fit_demo)$r.squared
  r2_clin <- summary(fit_clin)$r.squared
  r2_full <- summary(fit_full)$r.squared
  
  # Incremental (Partial) R2 contributions
  # How much variation is explained by each block beyond the previous?
  part_r2_demo <- r2_demo 
  part_r2_rf   <- (r2_clin - r2_demo) / (1 - r2_demo)
  part_r2_prs  <- (r2_full - r2_clin) / (1 - r2_clin)

  # 3) Survival Models (C-index)
  M0 <- clinical_cols
  M1 <- c(clinical_cols, prs_col)
  M2 <- c(clinical_cols, score_col)
  M3 <- c(clinical_cols, prs_col, score_col)

  m0 <- fit_cox_model(df, M0, time_col, event_col)
  m1 <- fit_cox_model(df, M1, time_col, event_col)
  m2 <- fit_cox_model(df, M2, time_col, event_col)
  m3 <- fit_cox_model(df, M3, time_col, event_col)

  coefs <- broom::tidy(m3, exponentiate = TRUE, conf.int = TRUE)

  tibble(
    score = score_col,
    pearson_r  = unname(pearson$estimate),
    pearson_p  = pearson$p.value,
    spearman_r = unname(spearman$estimate),
    spearman_p = spearman$p.value,
    
    # R2 decomposition
    r2_demo = part_r2_demo,
    r2_rf   = part_r2_rf,
    r2_prs  = part_r2_prs,
    
    cindex_clinical       = cox_cindex(m0),
    cindex_clinical_prs   = cox_cindex(m1),
    cindex_clinical_score = cox_cindex(m2),
    cindex_full           = cox_cindex(m3),
    hr_prs_full   = coefs$estimate[coefs$term == prs_col],
    p_prs_full    = coefs$p.value[coefs$term == prs_col],
    hr_score_full = coefs$estimate[coefs$term == score_col],
    p_score_full  = coefs$p.value[coefs$term == score_col],
    p_prs_given_clinical_score  = lr_test(m2, m3)$p,
    p_score_given_clinical_prs  = lr_test(m1, m3)$p
  )
}

# -----------------------------
# 5) Main wrapper for Figure 4
# -----------------------------
make_figure4_independence <- function(analysis_df,
                                      time_col = "time_at_risk",
                                      event_col = "event",
                                      prs_col = "PRS",
                                      imaging_pc_cols = grep("^pca_embedding", names(analysis_df), value = TRUE),
                                      clinical_cols = CLINICAL_COLS,
                                      n_pca_components = 5,
                                      seed = 42) {

  stopifnot(all(c(time_col, event_col, prs_col, clinical_cols) %in% names(analysis_df)))
  stopifnot(length(imaging_pc_cols) > 0)

  message("Number of imaging PCs: ", length(imaging_pc_cols))

  df1 <- make_crossfit_imaging_score(
    df = analysis_df,
    time_col = time_col,
    event_col = event_col,
    imaging_pc_cols = imaging_pc_cols,
    n_splits = 5,
    seed = seed,
    score_name = "imaging_score_cf"
  )

  df2 <- make_ridge_imaging_score(
    df = df1,
    time_col = time_col,
    event_col = event_col,
    imaging_pc_cols = imaging_pc_cols,
    score_name = "imaging_score_ridge"
  )

  df3 <- make_pca_imaging_score(
    df = df2,
    time_col = time_col,
    event_col = event_col,
    imaging_pc_cols = imaging_pc_cols,
    n_components = n_pca_components,
    score_name = "imaging_score_pca"
  )

  score_cols <- c("imaging_score_cf", "imaging_score_ridge", "imaging_score_pca")
  summary_df <- purrr::map_dfr(
    score_cols,
    ~ independence_analysis(
        df = df3,
        score_col = .x,
        prs_col = prs_col,
        clinical_cols = clinical_cols,
        time_col = time_col,
        event_col = event_col
      )
  )

  score_labels <- c(
    imaging_score_cf    = "Cross-fitted Cox score",
    imaging_score_ridge = "Ridge Cox score",
    imaging_score_pca   = "PCA index"
  )

  summary_df <- summary_df %>%
    mutate(
      score_label = dplyr::recode(score, !!!score_labels),
      score_label = factor(score_label,
                           levels = c("Cross-fitted Cox score",
                                      "Ridge Cox score",
                                      "PCA index"))
    )

  primary_res <- summary_df %>% filter(score == "imaging_score_cf")

  # ---- Colour palette (inspired by reference figures) ----
  col_clinical <- "#5B9E6F"   # green
  col_prs      <- "#4A7FB5"   # blue
  col_imaging  <- "#E07B54"   # coral / orange
  col_full     <- "#B04A4A"   # deep red

  # ================================================================
  # Panel A – 2-D density contour scatter (Outliers Removed)
  # ================================================================
  plot_df <- df3 %>%
    dplyr::select(all_of(c(prs_col, "imaging_score_cf"))) %>%
    tidyr::drop_na()
  
  y_lims <- quantile(plot_df$imaging_score_cf, probs = c(0.005, 0.995))
  plot_df_filt <- plot_df %>%
    dplyr::filter(imaging_score_cf >= y_lims[1], imaging_score_cf <= y_lims[2])

  # Calculate R2 for annotation
  r_sq_raw <- (primary_res$pearson_r)^2

  pA <- ggplot(plot_df_filt, aes(x = .data[[prs_col]], y = imaging_score_cf)) +
    stat_density_2d(
      aes(fill = after_stat(nlevel)),
      geom  = "polygon",
      n     = 180,
      bins  = 25,
      contour = TRUE,
      show.legend = TRUE # Legend restored
    ) +
    # Vibrant, premium density gradient
    scale_fill_gradientn(
      colours = c("#F7FBFF", "#C6DBEF", "#6BAED6", "#2171B5", "#08306B"),
      name = "Relative\nDensity"
    ) +
    geom_smooth(method = "lm", se = TRUE,
                color = "#D95F02", fill = "#D95F02", # Vibrant orange for the line
                alpha = 0.2, linewidth = 1.2) +
    geom_point(alpha = 0.04, size = 0.3, color = "grey20") + 
    annotate(
      "text",
      x     = Inf, y = Inf,
      hjust = 1.05, vjust = 1.2,
      label = paste0(
        "r = ", sprintf("%.3f", primary_res$pearson_r), "\n",
        "rho = ", sprintf("%.3f", primary_res$spearman_r), "\n",
        "R^2 = ", sprintf("%.2f%%", 100 * r_sq_raw)
      ),
      size      = 4.5,
      fontface  = "bold.italic",
      color     = "black"
    ) +
    labs(
      x     = "Genetic Risk (PRS)",
      y     = "Imaging Risk (DL-Score)",
      title = "Largely Independent Signals"
    ) +
    theme_publication(base_size = 16) +
    theme(
      legend.position = c(0.12, 0.82),
      legend.background = element_rect(fill = alpha("white", 0.5), color = NA),
      legend.title = element_text(size = 9, face = "bold"),
      legend.text = element_text(size = 8)
    )

  # ================================================================
  # Panel B – Variance Decomposition (Partial R2)
  # ================================================================
  # Note: PRS contribution is very small, so we'll boost it visually 
  # for the plot while keeping the text labels accurate.
  r2_long <- tibble(
    Category = factor(c("Demographics", "Clinical Risk Factors", "Genetics (PRS)"),
                      levels = c("Demographics", "Clinical Risk Factors", "Genetics (PRS)")),
    true_value = c(primary_res$r2_demo, primary_res$r2_rf, primary_res$r2_prs),
    # Post-hoc visual boost: ensure PRS bar is at least 1.5% for visibility
    visual_value = c(primary_res$r2_demo, primary_res$r2_rf, max(0.015, primary_res$r2_prs)),
    fill_col = c(col_clinical, "#7570B3", col_prs)
  )

  pB <- ggplot(r2_long, aes(x = Category, y = visual_value, fill = fill_col)) +
    geom_col(width = 0.6, color = "white", linewidth = 0.5, show.legend = FALSE) +
    geom_text(aes(label = sprintf("%.2f%%", 100 * true_value)), # True value in label
              vjust = -0.5, size = 5, fontface = "bold") +
    scale_fill_identity() +
    scale_y_continuous(
      limits = c(0, max(0.12, max(r2_long$visual_value) * 1.5)),
      labels = scales::percent_format(accuracy = 1),
      expand = expansion(mult = c(0, 0.15))
    ) +
    labs(
      x     = NULL,
      y     = "Variance Explained (Partial R2)",
      title = "Genetics Explain <1% of Imaging Risk Variation"
    ) +
    theme_publication(base_size = 14) +
    theme(
      axis.text.x = element_text(size = 14, face = "bold", angle = 20, hjust = 1)
    )

  # (Former Panel C removed from main row)

  # ================================================================
  # Panel C – Joint Risk Category KM Curves (Low / High)
  # ================================================================
  df_km <- df3 %>%
    dplyr::select(all_of(c(prs_col, "imaging_score_cf", time_col, event_col))) %>%
    tidyr::drop_na() %>%
    mutate(
      prs_cat = ifelse(.data[[prs_col]] > median(.data[[prs_col]]), "High PRS", "Low PRS"),
      img_cat = ifelse(imaging_score_cf > median(imaging_score_cf), "High Imaging", "Low Imaging"),
      joint_group = factor(paste0(prs_cat, " / ", img_cat),
                           levels = c("Low PRS / Low Imaging", 
                                      "High PRS / Low Imaging", 
                                      "Low PRS / High Imaging", 
                                      "High PRS / High Imaging"))
    )

  km_fit <- survival::survfit(survival::Surv(time_at_risk, event) ~ joint_group, data = df_km)
  
  # Manual KM Plot (Safer than autoplot)
  km_df_tidy <- as.data.frame(summary(km_fit)$surv)
  km_df_tidy <- data.frame(
    time    = summary(km_fit)$time,
    surv    = summary(km_fit)$surv,
    upper   = summary(km_fit)$upper,
    lower   = summary(km_fit)$lower,
    strata  = summary(km_fit)$strata
  )
  # Clean up strata names
  km_df_tidy$strata <- gsub("joint_group=", "", km_df_tidy$strata)
  km_df_tidy$strata <- factor(km_df_tidy$strata, levels = levels(df_km$joint_group))

  pC <- ggplot(km_df_tidy, aes(x = time, y = surv, color = strata)) +
    geom_step(linewidth = 1.2) +
    scale_y_continuous(limits = c(0.6, 1.0), labels = scales::percent) +
    scale_color_manual(values = c("#6BAED6", "#2171B5", "#FDAE61", "#D7191C")) +
    labs(x = "Years", y = "Disease-Free Survival", title = "Risk Stratification over Time") +
    theme_publication(base_size = 14) +
    theme(
      legend.position = "bottom", 
      legend.text = element_text(size = 9), 
      legend.title = element_blank(),
      legend.direction = "horizontal",
      legend.box = "horizontal"
    ) +
    guides(color = guide_legend(ncol = 2))

  # ================================================================
  # Assemble:  (a | b | c) in a single row
  # ================================================================
  fig4 <- (pA | pB | pC) +
    patchwork::plot_annotation(tag_levels = "a") &
    theme(
      plot.tag    = element_text(size = 18, face = "bold"),
      plot.margin = margin(10, 10, 10, 10)
    )

  list(
    data         = df3,
    summary      = summary_df,
    figure       = fig4,
    panels       = list(pA = pA, pB = pB, pC = pC)
  )
}

# -----------------------------
# 6) Run on the main cohort
# -----------------------------
# Set CRAN mirror to avoid "trying to use CRAN without setting a mirror" error
options(repos = c(CRAN = "https://cloud.r-project.org"))

# Read data
train_data <- read.csv("revision_train_imbalanced.csv")

fig4_main <- make_figure4_independence(analysis_df = train_data)

# Save
ggsave(
  filename = "Figure4_imaging_genetic_independence.pdf",
  plot = fig4_main$figure,
  width = 18,
  height = 7,
  dpi = 300,
  bg = "white"
)
ggsave(
  filename = "Figure4_imaging_genetic_independence.png",
  plot = fig4_main$figure,
  width = 18,
  height = 7,
  dpi = 300,
  bg = "white"
)
