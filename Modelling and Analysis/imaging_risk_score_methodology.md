# Methodology: Construction of the Imaging Risk Score (IRS)

This document provides a technical description of the construction, implementation, and clinical application of the Imaging Risk Score (IRS) for predicting 10-year coronary event risk.

## 1. Executive Summary
The Imaging Risk Score (IRS) is a multimodal, deep-learning-derived phenotypic risk marker designed to quantify subclinical coronary artery disease (CAD) risk. By integrating high-dimensional imaging features from various anatomical regions (Heart, Liver, Pancreas, etc.), the IRS captures distinct biological signals that are orthogonal to traditional clinical risk factors and polygenic risk scores (PRS).

---

## 2. Study Population and Data Statistics
The model was developed and evaluated using data from the UK Biobank, specifically focusing on individuals with available longitudinal follow-up and multimodal imaging.

- **Source File**: `revision_train_imbalanced_true.csv`
- **Total Sample Size (N)**: 29,075 individuals.
- **Incidence of Coronary Events (10-year)**:
    - **Cases**: 2,511 individuals (8.6%).
    - **Controls**: 26,564 individuals (91.4%).

The population reflects a realistic clinical scenario with imbalanced event distribution, necessitating robust statistical handling for risk estimation.

---

## 3. Input Features (Imaging-Derived Phenotypes)
The IRS is constructed from deep-learning-derived primary component analysis (PCA) embeddings. These features represent a compressed representation of raw medical images from several sources:
- **Heart MRI**: Left Atrium (LA), Aortic Diameter (AD), and Basin Fraction (BF).
- **Abdominal MRI**: Liver and Pancreatic fat/volume features.
- **Dual-Energy X-ray Absorptiometry (DXA)**: Body composition and fat distribution.

Each modality contributes unique phenotypic information, which is encoded into a set of 10 PCA dimensions per view (e.g., `pca_embedding0_1` to `pca_embedding2_10`).

---

## 4. Statistical Framework: Regularized Cox Survival Model
To predict the 10-year hazard of coronary events, we employ a **Cox Proportional Hazards (PH) model** with internal regularization.

### 4.1 Hazard Function
The hazard at time $t$ for an individual with imaging features $X$ is modeled as:
$$h(t | X) = h_0(t) \exp\left( \sum_{i=1}^{p} \beta_i X_i \right)$$
where $h_0(t)$ is the baseline hazard and $\beta_i$ are the regression coefficients for the imaging features.

### 4.2 Ridge Regularization ($L_2$ Penalty)
Given the high dimensionality and multi-collinearity of imaging-derived features, we apply **Ridge Regression** to stabilize coefficient estimates. The objective function minimizes the negative log-partial likelihood with an additional penalty term:
$$\mathcal{L}_{penalty} = -\ell(\beta) + \lambda \sum_{i=1}^{p} \beta_i^2$$
The $L_2$ penalty (Ridge) was chosen over $L_1$ (Lasso) to retain information from all imaging dimensions while shrinking them towards zero to prevent overfitting.

---

## 5. Implementation Details: Cross-Fitting and Scaling
To ensure the IRS is generated for the entire study population without "fishing" or overfitting, we implement a **5-fold cross-fitting** procedure.

### 5.1 Cross-Fitting Workflow
1. **Partitioning**: The dataset is divided into 5 independent folds.
2. **Iterative training**: For each fold $k \in \{1, \dots, 5\}$:
    - Fold $k$ is reserved as the "test" set.
    - Folds $\{1, \dots, 5\} \setminus \{k\}$ are used as the "training" set.
    - A Cox Ridge model is trained solely on the training set.
    - **Predicting**: The trained model generates the Risk Score for individuals in the test fold $k$.
3. **Score Assembly**: Once all 5 iterations are complete, every individual in the study has an "unbiased" imaging risk score generated from a model that never saw their specific data during training.

### 5.2 Standardization and Scaling
- **Feature Scaling**: Within each training fold, imaging features are Z-score standardized (mean = 0, SD = 1). The same mean and SD are then applied to the test fold to maintain strict data independence.
- **Final IRS Normalization**: The resulting linear predictors from all folds are pooled and standardized to a standard normal distribution. This allows for the interpretation of Hazard Ratios (HR) **per standard deviation (SD)** increase in IRS.

### 5.3 Hyperparameter Tuning
The regularization parameter $\lambda$ is selected via internal **5-fold cross-validation** within each training fold, optimizing for the maximum concordance index (C-index) or partial likelihood.

---

## 6. Calculation of the Risk Score
For any individual $j$, the Imaging Risk Score is the linear predictor ($\text{link}$):
$$\text{IRS}_j = \sum_{i=1}^{p} \hat{\beta}_i X_{i,j}$$
This value representing the relative log-hazard of an individual compared to the population average.

---

## 7. Clinical Performance Summary
External validation and utility analyses show:
- **Discrimination**: The IRS significantly improves the C-index over clinical-only models (e.g., moving from 0.709 to 0.756).
- **Hazard Ratio**: The IRS remains a potent independent predictor (HR $\approx 1.76-1.92$ per SD) even after adjusting for polygenic risk and clinical markers.
- **Independence**: The correlation between IRS and PRS is negligible ($r \approx 0.05$), confirming that the imaging phenotype captures an orthogonal dimension of disease risk.
