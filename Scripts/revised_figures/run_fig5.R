# Runner script for Figure 5 Redesign with imbalanced dataset
source("/Users/devanshpandey/Downloads/Revsisons/figure5_redesigned.R")

# We need the cross-fitting functions from the other file
source("/Users/devanshpandey/Downloads/Revsisons/figure5_joint_survival_utility.R")

cat("Loading data...\n")
imbalanced_df <- read.csv("/Users/devanshpandey/Downloads/Revsisons/revision_train_imbalanced_true.csv")

# Generate imaging_score_cf for full_df (10-fold CV)
imaging_pc_cols <- grep("^pca_embedding", names(imbalanced_df), value = TRUE)
cat("Found", length(imaging_pc_cols), "imaging PC columns. Generating cross-fitted score for FULL set...\n")

full_df <- make_crossfit_imaging_score(
  df              = imbalanced_df,
  time_col        = TIME_COL,
  event_col       = EVENT_COL,
  imaging_pc_cols = imaging_pc_cols,
  n_splits        = 10
)

# Train/Test Split (70/30)
set.seed(42)
n_total <- nrow(full_df)
train_idx <- sample(seq_len(n_total), size = floor(0.70 * n_total))

train_df <- full_df[train_idx, ]
test_df <- full_df[-train_idx, ]

cat("Generating Figure 5 (Redesigned with Split Data AND Full Data)...\n")
fig5 <- make_figure5_redesigned(
  full_df = full_df,
  train_df = train_df,
  test_df = test_df,
  img_cols = imaging_pc_cols,
  output_prefix = "/Users/devanshpandey/Downloads/Revsisons/figure5_redesigned_imbalanced"
)

cat("Execution complete. Summary metrics:\n")
print(fig5$summary$cindex)

# Save PDF version as well
ggsave(
  filename = "/Users/devanshpandey/Downloads/Revsisons/Figure5_redesigned_imbalanced.pdf",
  plot = fig5$figure,
  width = 13, height = 10, dpi = 300, bg = "white"
)
cat("Saved PDF: /Users/devanshpandey/Downloads/Revsisons/Figure5_redesigned_imbalanced.pdf\n")
