# Utility functions for Figure 5
# Extracted from figure4_imaging_genetic_independence.R

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
