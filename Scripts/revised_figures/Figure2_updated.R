# Load required libraries directly
library(ggplot2)
library(dplyr)
library(readr)
library(patchwork)
library(tidyr)
library(forcats)
library(scales)
library(gridExtra)
library(cowplot)

###############################################
# Nature Medicine-style theme and colors
###############################################
# Using a different set of colors from the palette for better distinction
cbPalette <- c("#0072B2", "#009E73", "#D55E00", "#CC79A7") # blue, green, orange

# Adjusted theme for better spacing and readability
theme_nm <- theme_bw(base_size = 14, base_family = "Helvetica") +
  theme(
    panel.border       = element_rect(color = "black", fill = NA, linewidth = 0.7),
    panel.grid.major   = element_line(color = "grey90", linewidth = 0.2),
    panel.grid.minor   = element_blank(),
    axis.line          = element_line(color = "black"),
    axis.ticks         = element_line(color = "black"),
    axis.text          = element_text(color = "black", size = 12),
    axis.title         = element_text(face = "bold", size = 13),
    # Reduced margin for the Y-axis title to bring it closer to the plot
    axis.title.y       = element_text(margin = margin(t = 0, r = 5, b = 0, l = 0)),
    plot.title         = element_text(face = "bold", size = 14, hjust = 0.5),
    plot.tag           = element_text(face = "bold", size = 18),
    strip.text         = element_text(face = "bold", size = 12),
    strip.background   = element_blank(),
    legend.position    = "right"
  )

###############################################
# Load and process data
###############################################
# Reverted to using read_csv to load your local files.
train_results <- read_csv("pca_xgboost_cv_results.csv")
auc_data <- read_csv("cv_auc_scores_per_fold.csv")
lrt <- read_csv("likelihood_ratio_tests_extended.csv")
cca_df <- read_csv("cca_idp_loadings_by_view.csv")

# Map the Num_PCs values to the requested labels for plotting
train_results <- train_results %>%
  mutate(Num_PCs = case_when(
    Num_PCs == "1" ~ "1",
    Num_PCs == "2" ~ "2",
    Num_PCs == "3" ~ "3",
    Num_PCs == "4" ~ "4",
    Num_PCs == "5" ~ "5",
    Num_PCs == "10" ~ "10",
    Num_PCs == "Full Embedding" ~ "Full\nEmbedding",
    TRUE ~ Num_PCs
  ))

# Set factor levels to ensure correct plotting order
train_results$Num_PCs <- factor(train_results$Num_PCs,
                                levels = c("1", "2", "3", "4", "5", "10", "Full\nEmbedding"))




train_long <- train_results %>%
  pivot_longer(c(AUC, Accuracy), names_to = "Metric", values_to = "Value") %>%
  mutate(Metric = factor(Metric, levels = c("AUC", "Accuracy")))

train_sum <- train_long %>%
  group_by(Num_PCs, Metric) %>%
  summarise(Mean = mean(Value), SD = sd(Value), .groups = "drop")

auc_data$Model <- factor(auc_data$Model, levels = c("A (IDPs)", "B (PCA)", "C (IDPs + PCA)"))

auc_sum <- auc_data %>%
  group_by(Model) %>%
  summarise(Mean = mean(AUC), SD = sd(AUC), .groups = "drop")

###############################################
# Plot A: Accuracy & AUC vs PCs
###############################################
plot_a <- ggplot(train_sum, aes(x = Num_PCs, y = Mean, fill = Metric)) +
  geom_bar(stat = "identity", position = position_dodge(0.8), width = 0.7, color = "black") +
  geom_errorbar(aes(ymin = Mean - SD, ymax = Mean + SD),
                position = position_dodge(0.8), width = 0.25) +
  # Using blue and green for AUC and Accuracy
  scale_fill_manual(values = cbPalette[1:2]) +
  # Set y-axis limit to 0.70 as requested
  scale_y_continuous(expand = c(0, 0), limits = c(0, 0.80)) +
  labs(
    tag = "a", title = "Impact of Dimensionality on Model Performance",
    x = "Number of Principal Components", y = "Metric Value"
  ) +
  theme_nm +
  theme(
    legend.title = element_blank(),
    # FIX: Explicitly adjust the margin of the y-axis title for this specific plot
    # to counteract the spacing issue caused by the legend.
    axis.title.y = element_text(margin = margin(t = 0, r = 3, b = 0, l = 0))
  )

###############################################
# Plot B: AUC comparison w/ LRT
###############################################
label1 <- sprintf("LR = %.1f\np = %s", lrt$`LR-Stat`[1], formatC(lrt$`P-Value`[1], format = "e", digits = 1))
label2 <- sprintf("LR = %.1f\np = %s", lrt$`LR-Stat`[3], formatC(lrt$`P-Value`[3], format = "e", digits = 1))

plot_b <- ggplot() +
  geom_jitter(data = auc_data, aes(x = Model, y = AUC),
              shape = 21, size = 2.5, stroke = 0.3, width = 0.15, color = "gray30", fill = "white") +
  geom_errorbar(data = auc_sum, aes(x = Model, ymin = Mean - SD, ymax = Mean + SD),
                width = 0.15, color = "black", linewidth = 0.7) +
  geom_point(data = auc_sum, aes(x = Model, y = Mean, fill = cbPalette[4]),
             shape = 21, size = 4.5, color = "black") +
  # Using all three colors for the three models
  scale_fill_manual(values = cbPalette[4]) +
  annotate("segment", x = 1, xend = 2, y = 0.84, yend = 0.84, linewidth = 0.6) +
  annotate("text", x = 1.5, y = 0.85, label = label1, size = 4, vjust = 0) +
  annotate("segment", x = 2, xend = 3, y = 0.88, yend = 0.88, linewidth = 0.6) +
  annotate("text", x = 2.5, y = 0.89, label = label2, size = 4, vjust = 0) +
  coord_cartesian(ylim = c(0.63, 0.92), clip = "off") +
  labs(
    tag = "b", title = "Model Discrimination Performance Across Feature Sets", x = "Model", y = "AUC"
  ) +
  theme_nm +
  theme(legend.position = "none")

###############################################
# Plot C: Canonical loadings
###############################################
cca_df$Clean_IDP <- recode(cca_df$idp,
  "lv_stroke_vol" = "LV Stroke Volume",
  "lv_ejection_fraction" = "LV Ejection Fraction",
  "lv_end_diastolic_vol" = "LV End Diastolic Volume",
  "lv_end_systolic_vol" = "LV End Systolic Volume",
  "lv_myocardial_mass" = "LV Myocardial Mass",
  "lv_mean_wall_thick_global" = "LV Mean Wall Thickness",
  "lv_circ_strain_global" = "LV Circumferential Strain",
  "lv_rad_strain_global" = "LV Radial Strain",
  "lv_long_strain_global" = "LV Longitudinal Strain",
  "asc_aorta_dist" = "Ascending Aorta Distensibility",
  "desc_aorta_dist" = "Descending Aorta Distensibility"
)

cca_df$embedding_view <- factor(cca_df$embedding_view, levels = c("2CH View", "3CH View", "4CH View", "Aortic View"))

# FIX: Define a custom order for the y-axis labels
idp_order <- c(
    # Volume
    "LV Stroke Volume", "LV End Diastolic Volume", "LV End Systolic Volume", "LV Ejection Fraction",
    # Mass
    "LV Myocardial Mass", "LV Mean Wall Thickness",
    # Strain
    "LV Circumferential Strain", "LV Radial Strain", "LV Longitudinal Strain",
    # Distensibility
    "Ascending Aorta Distensibility", "Descending Aorta Distensibility"
)

# FIX: Apply the custom order to the 'Clean_IDP' column as a factor.
# We reverse the order because ggplot plots factors from bottom to top.
cca_df$Clean_IDP <- factor(cca_df$Clean_IDP, levels = rev(idp_order))

# FIX: Removed fct_reorder and now use the manually ordered factor 'Clean_IDP'
plot_c <- ggplot(cca_df, aes(x = weight, y = Clean_IDP)) +
  # Using a single color for all bars
  geom_col(fill = cbPalette[3], width = 0.7) + # Using the orange color
  geom_vline(xintercept = 0, linetype = "dashed", color = "gray30", linewidth = 0.5) +
  facet_wrap(~embedding_view, nrow = 1) +
  scale_x_continuous(breaks = pretty_breaks(n = 3)) +
  labs(
    tag = "c", title = "Contributions of IDPs to Canonical Variable 1 from Raw Embeddings by View",
    x = "Weight", y = "Image Derived Phenotype (IDP)"
  ) +
  theme_nm +
  theme(
    axis.text.y = element_text(size = 10),
    strip.text = element_text(size = 12, face = "bold"),
    panel.spacing = unit(1.5, "lines")
  )

###############################################
# Final layout and PDF export
###############################################
# Layout remains the same to keep top row heights equal
top_row <- grid.arrange(
  plot_a,
  plot_b,
  ncol= 2,
  widths = c(1.2, 1)
)
final_figure <- grid.arrange(
  top_row,
  plot_c,
  nrow = 2,
  heights = c(1, 1.2)
)

ggsave("Figure2_final_revised.pdf", final_figure, width = 14, height = 11, dpi = 600)