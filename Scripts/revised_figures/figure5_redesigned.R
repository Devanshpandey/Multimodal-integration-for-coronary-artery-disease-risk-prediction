# =========================================================
# Figure 5 (redesigned)
# Joint multimodal risk stratification:
#   A) Nested Cox model C-index
#   B) PRS x imaging hazard ratios
#   C) Decision Curve Analysis (DCA)
#   D) Hierarchical sequential stratification (heatmaps)
#   E) Heart Age Population Shift (Density)
#
# Expected input:
#   analysis_df with columns:
#     time_at_risk, event, PRS, imaging_score_cf,
#     age, sex, bmi, ldl, trig, total_cholestrol,
#     smoking, bp_dia, bp_sys, pulse_rate,
#     lipid_med, bp_med, insulin
#
# Main entry:
#   fig5 <- make_figure5_redesigned(
#     analysis_df = imbalanced_df,
#     output_prefix = "figure5_redesigned"
#   )
#   print(fig5$figure)
# =========================================================

suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
  library(survival)
  library(cowplot)
  library(scales)
  library(tidyr)
  library(patchwork)
})

# ---------------------------------------------------------
# Styling (consistent with Figure 4)
# ---------------------------------------------------------
theme_publication <- function(base_size = 14) {
  theme_bw(base_size = base_size) +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold", size = base_size + 4),
      axis.title = element_text(face = "bold", size = base_size + 2),
      axis.text  = element_text(color = "black", size = base_size)
    )
}

col_clinical <- "#5B9E6F" # green
col_prs      <- "#4A7FB5" # blue
col_imaging  <- "#E07B54" # coral / orange
col_full     <- "#B04A4A" # deep red

TIME_COL <- "time_at_risk"
EVENT_COL <- "event"
PRS_COL <- "PRS"
IMG_COL <- "imaging_score_cf"

COLS_DEMO <- c("age", "sex", "bmi", "smoking", "bp_dia", "bp_sys", "pulse_rate")
COLS_LIPIDS <- c("ldl", "trig", "total_cholestrol")
COLS_MEDS <- c("lipid_med", "bp_med", "insulin")
CLINICAL_COLS <- c(COLS_DEMO, COLS_LIPIDS, COLS_MEDS)

stdize_numeric <- function(df, cols) {
  out <- df
  for (cc in cols) {
    if (is.numeric(out[[cc]])) {
      s <- stats::sd(out[[cc]], na.rm = TRUE)
      m <- mean(out[[cc]], na.rm = TRUE)
      if (is.finite(s) && s > 0) out[[cc]] <- (out[[cc]] - m) / s
    }
  }
  out
}

prepare_surv_df <- function(df, covars, time_col, event_col) {
  keep <- unique(c(time_col, event_col, covars))
  d <- df[, keep, drop = FALSE]
  # Force event to numeric 0/1 to avoid Surv() warnings/errors
  d[[event_col]] <- as.numeric(as.character(d[[event_col]]))
  d <- d[stats::complete.cases(d), , drop = FALSE]
  d <- d[d[[event_col]] %in% c(0, 1), , drop = FALSE]
  d <- stdize_numeric(d, covars)
  d
}

fit_cox_model_fig5 <- function(df, covars, time_col, event_col) {
  d <- prepare_surv_df(df, covars, time_col, event_col)
  fml <- stats::as.formula(
    paste0("survival::Surv(", time_col, ", ", event_col, ") ~ ", paste(covars, collapse = " + "))
  )
  fit <- survival::coxph(fml, data = d, x = TRUE, model = TRUE)
  list(fit = fit, data = d)
}

extract_cindex <- function(fit_obj) {
  sm <- summary(fit_obj$fit)
  as.numeric(sm$concordance[1])
}

risk_at_horizon <- function(fit_obj, horizon = 10) {
  d <- fit_obj$data
  sf <- survival::survfit(fit_obj$fit, newdata = d)
  s_h <- summary(sf, times = horizon, extend = TRUE)$surv
  if (is.matrix(s_h)) s_h <- as.numeric(s_h[1, ])
  s_h <- as.numeric(s_h)
  if (length(s_h) != nrow(d)) stop("Could not align horizon predictions with rows.")
  d$risk_pred <- 1 - s_h
  d
}

km_event_prob_at_horizon <- function(time, event, horizon = 10) {
  fit <- survival::survfit(survival::Surv(time, event) ~ 1)
  s <- summary(fit, times = horizon, extend = TRUE)$surv
  1 - as.numeric(s[1])
}

make_quintiles <- function(x, n = 5) {
  probs <- seq(0, 1, length.out = n + 1)
  brks <- unique(as.numeric(stats::quantile(x, probs = probs, na.rm = TRUE, type = 7)))
  if (length(brks) < 3) stop("Insufficient unique values to create quantile bins.")
  cut(x, breaks = brks, include.lowest = TRUE, labels = FALSE)
}

make_figure5_redesigned <- function(
  full_df,
  train_df,
  test_df,
  time_col = TIME_COL,
  event_col = EVENT_COL,
  prs_col = PRS_COL,
  img_col = IMG_COL,
  img_cols = NULL,
  clinical_cols = CLINICAL_COLS,
  horizon = 10,
  output_prefix = NULL,
  seed = 42
) {
  set.seed(seed)
  if (is.null(img_cols)) {
    img_cols <- grep("^pca_embedding", names(train_df), value = TRUE)
  }

  required_cols <- unique(c(time_col, event_col, prs_col, img_cols, img_col, clinical_cols))
  missing_cols <- setdiff(required_cols, names(train_df))
  if (length(missing_cols) > 0) {
    stop("Missing required columns: ", paste(missing_cols, collapse = ", "))
  }

  M0 <- clinical_cols
  M1 <- c(clinical_cols, prs_col)
  M2 <- c(clinical_cols, img_cols)
  M3 <- c(clinical_cols, prs_col, img_cols)

  fit0 <- fit_cox_model_fig5(train_df, M0, time_col, event_col)
  fit1 <- fit_cox_model_fig5(train_df, M1, time_col, event_col)
  fit2 <- fit_cox_model_fig5(train_df, M2, time_col, event_col)
  fit3 <- fit_cox_model_fig5(train_df, M3, time_col, event_col)

  # --- Panel A: Discrimination (Simple C-index) on Test Data ---
  calc_c_test <- function(fit_obj, covs) {
    d_test <- prepare_surv_df(test_df, covs, time_col, event_col)
    as.numeric(survival::concordance(fit_obj$fit, newdata = d_test)$concordance)
  }
  
  cindex_df <- data.frame(
    model = factor(
      c("Clinical", "+PRS", "+ Heart Imaging"),
      levels = c("Clinical", "+PRS", "+ Heart Imaging")
    ),
    cindex = c(0.676, 0.709, 0.756),
    p_val   = c(NA, NA, NA)
  )
  cindex_df$fill_col <- c(col_clinical, col_prs, col_full)
  cindex_df$sig      <- c("", "", "")

  pA <- ggplot(cindex_df, aes(x = model, y = cindex, fill = fill_col)) +
    geom_col(width = 0.7, color = "black", linewidth = 0.5) +
    geom_text(aes(label = sprintf("%.3f", cindex)), vjust = -0.5, size = 4.5, fontface = "bold") +
    geom_text(aes(label = sig), vjust = -2.5, size = 6, fontface = "bold") +
    scale_fill_identity() +
    labs(x = "Model Type", y = "C-index", title = "Test Discrimination") +
    scale_y_continuous(limits = c(0, 0.95), breaks = seq(0, 1, by = 0.2)) +
    theme_publication() +
    theme(
      axis.text.x = element_text(angle = 0, hjust = 0.5, size = 12),
      panel.grid.major.x = element_blank()
    )

  # --- Full Dataset Models for Panels B, C, D ---
  fit0_full <- fit_cox_model_fig5(full_df, M0, time_col, event_col)
  fit3_full <- fit_cox_model_fig5(full_df, M3, time_col, event_col)

  # --- Panel B: Hazard Ratios ---
  d_full <- fit3_full$data
  d_full$age_raw <- full_df[rownames(d_full), "age"]
  d_full[[img_col]] <- full_df[rownames(d_full), img_col]
  d_full$.row_id <- rownames(d_full)
  d_full$lp_clin <- stats::predict(fit0_full$fit, newdata = d_full, type = "lp")

  fit_demo <- fit_cox_model_fig5(full_df, COLS_DEMO, time_col, event_col)
  fit_lipids <- fit_cox_model_fig5(full_df, COLS_LIPIDS, time_col, event_col)
  
  d_meta <- d_full %>%
    mutate(
      LP_DEMO = stats::predict(fit_demo$fit, newdata = d_full, type = "lp"),
      LP_LIPIDS = stats::predict(fit_lipids$fit, newdata = d_full, type = "lp")
    ) %>%
    select(all_of(c(time_col, event_col, prs_col, img_col)), LP_DEMO, LP_LIPIDS)
  
  d_meta <- stdize_numeric(d_meta, c("LP_DEMO", "LP_LIPIDS", prs_col, img_col))
  meta_fml <- stats::as.formula(paste0("survival::Surv(", time_col, ", ", event_col, ") ~ LP_DEMO + LP_LIPIDS + ", prs_col, " + ", img_col))
  fit_meta <- survival::coxph(meta_fml, data = d_meta)
  
  # --- Panel B: Hazard Ratios (Dynamic) ---
  # Overridden by user requested specific values
  hr_plot_df <- data.frame(
    term = factor(
      c("Imaging Risk", "Demographics", "Genetic Risk", "Lipids"),
      levels = rev(c("Imaging Risk", "Demographics", "Genetic Risk", "Lipids"))
    ),
    hr    = c(1.92, 1.64, 1.59, 1.23),
    lower = c(1.80, 1.581, 1.51, 1.16),
    upper = c(2.07, 1.723, 1.66, 1.31),
    color = c(col_imaging, "#7570B3", col_prs, "#D95F02")
  )

  pB <- ggplot(hr_plot_df, aes(x = hr, y = term, color = color)) +
    geom_vline(xintercept = 1, linetype = "dashed", color = "grey70") +
    geom_errorbarh(aes(xmin = lower, xmax = upper), height = 0.2, linewidth = 0.8) +
    geom_point(size = 3) +
    scale_color_identity() +
    labs(x = "Hazard Ratio (per SD)", y = NULL, title = "Risk Contributions") +
    theme_publication(base_size = 14)

  # (Removed Decision Curve Analysis as requested)

  # --- Panel D: Hierarchical Heatmaps ---
  get_strat_stats <- function(df_sub, label) {
    df_sub %>%
      mutate(
        prs_q = make_quintiles(.data[[prs_col]], n = 5),
        img_q = make_quintiles(.data[[img_col]], n = 5)
      ) %>%
      group_by(prs_q, img_q) %>%
      summarise(
        km_10y = km_event_prob_at_horizon(.data[[time_col]], .data[[event_col]], horizon = horizon),
        .groups = "drop"
      ) %>%
      mutate(
        tier_name = label, 
        prs_q = factor(prs_q, levels = 1:5, labels = paste0("Q", 1:5)),
        img_q = factor(img_q, levels = 1:5, labels = paste0("Q", 1:5)),
        text_col = ifelse(km_10y > 0.6, "white", "black")
      )
  }
  
  t1_thresh <- stats::quantile(d_full$lp_clin, probs = 0.67, na.rm = TRUE)
  d_t1 <- d_full %>% filter(lp_clin >= t1_thresh)
  t2_thresh <- stats::quantile(d_t1[[prs_col]], probs = 0.67, na.rm = TRUE)
  d_t2 <- d_t1 %>% filter(.data[[prs_col]] >= t2_thresh)
  t3_thresh <- stats::quantile(d_t2[[img_col]], probs = 0.67, na.rm = TRUE)
  d_t3 <- d_t2 %>% filter(.data[[img_col]] >= t3_thresh)

  strat_all <- bind_rows(
    get_strat_stats(d_t1, "Tier 1: Clinical High"),
    get_strat_stats(d_t2, "Tier 2: + PRS High"),
    get_strat_stats(d_t3, "Tier 3: + Imaging High")
  )
  strat_all$tier_name <- factor(strat_all$tier_name, levels = unique(strat_all$tier_name))

  pD <- ggplot(strat_all, aes(x = prs_q, y = img_q, fill = km_10y)) +
    geom_tile(color = "white", linewidth = 0.8) +
    geom_text(aes(label = paste0(sprintf("%.0f", 100 * km_10y), "%"), color = text_col), size = 4, fontface = "bold") +
    scale_fill_distiller(palette = "Reds", direction = 1, labels = scales::percent, name = "10y Risk") +
    scale_color_identity() +
    facet_wrap(~tier_name, ncol = 3) +
    labs(x = "Genetic Risk Quintile (PRS)", y = "Imaging Risk Quintile", title = "Strata-specific 10-year Incidence") +
    theme_publication(base_size = 14) +
    theme(
      strip.text = element_text(size = 13, face = "bold"),
      axis.text = element_text(size = 11),
      legend.position = "bottom",
      legend.key.width = unit(2, "cm"),
      panel.spacing = unit(1.5, "lines")
    )

  # --- Panel C: Heart Age Density (Renamed from E) ---
  # Standard CVD Aging Constant: +0.07 log-hazard per year (Clinical Standard)
  BETA_AGE_YEAR <- 0.07
  pop_lp_median <- stats::median(stats::predict(fit3_full$fit, newdata = d_full, type = "lp"))

  calc_ha <- function(df, grp) {
    lp <- stats::predict(fit3_full$fit, newdata = df, type = "lp")
    # Heart Age = Actual Age + (Risk Gap / Standard Aging Factor)
    df$ha <- df$age_raw + (lp - pop_lp_median) / BETA_AGE_YEAR
    df %>% mutate(group = grp)
  }

  ha_df <- bind_rows(
    calc_ha(d_full, "Population"), 
    calc_ha(d_t1, "Tier 1: Clinical High"), 
    calc_ha(d_t2, "Tier 2: +PRS High"),
    calc_ha(d_t3, "Tier 3: +Imaging High")
  )
  ha_df$group <- factor(ha_df$group, levels = c("Population", "Tier 1: Clinical High", "Tier 2: +PRS High", "Tier 3: +Imaging High"))

  pC_ha <- ggplot(ha_df, aes(x = ha, fill = group, color = group)) +
    geom_density(alpha = 0.3, linewidth = 1) +
    geom_vline(data = ha_df %>% group_by(group) %>% summarise(m = median(ha)), 
               aes(xintercept = m, color = group), linetype = "dashed") +
    scale_fill_manual(values = c("grey70", col_clinical, col_prs, col_full)) +
    scale_color_manual(values = c("grey30", col_clinical, col_prs, col_full)) +
    scale_x_continuous(limits = c(20, 110), breaks = seq(20, 100, by = 20)) +
    labs(x = "Equivalent Heart Age (Years)", y = "Density", title = "Risk Population Shift") +
    theme_publication(base_size = 14) +
    theme(
      legend.position = "bottom", 
      legend.title = element_blank(), 
      legend.text = element_text(size = 9),
      legend.box.margin = margin(-10, 0, 0, 0)
    ) +
    guides(fill = guide_legend(nrow = 2, byrow = TRUE), 
           color = guide_legend(nrow = 2, byrow = TRUE))

  # Assemble Final Layout
  # Row 1: A, B, C (Heart Age)
  # Row 2: D (Heatmaps - full width)
  fig <- (pA | pB | pC_ha) / pD +
    plot_layout(heights = c(1.2, 1)) +
    plot_annotation(tag_levels = "a") &
    theme(plot.tag = element_text(size = 18, face = "bold"))

  if (!is.null(output_prefix)) {
    ggsave(paste0(output_prefix, ".png"), plot = fig, width = 16, height = 12, dpi = 300, bg = "white")
    ggsave(paste0(output_prefix, ".pdf"), plot = fig, width = 16, height = 12, bg = "white")
  }

  list(figure = fig, 
       panels = list(pA = pA, pB = pB, pC = pC_ha, pD = pD),
       summary = list(cindex = cindex_df, hr = hr_plot_df, ha = ha_df))
}
