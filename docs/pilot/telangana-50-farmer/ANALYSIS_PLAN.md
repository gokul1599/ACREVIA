# ACREVIA 30-Day Pilot Statistical Analysis Plan
## Quantitative Methodologies, Statistical Tests & Pre-Registered Hypotheses
**Target Stage:** Stage 08 Remediation (`TASK-S08-01` / Evaluation Framework)  
**Sample Size:** $N = 50$ Smallholder Farmers ($n \ge 400$ Field Observations)  
**Reporting Standards:** Pre-registered methodology distinguishing correlation from causation  

---

## 1. Analysis Architecture & Statistical Principles

To ensure scientific integrity and prevent p-hacking or confirmation bias:
1. **Pre-Registered Analysis Protocol:** All analytical models, statistical tests, binning strategies, and significance thresholds are frozen prior to pilot commencement.
2. **Confidence Intervals:** All primary proportions (accuracy, concordance, sync rates) will be reported with **95% Wilson Score Confidence Intervals**:
   $$\text{CI}_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}} \quad (z = 1.96)$$
3. **Causality Bounds:** The study measures **perceived agronomic utility, diagnostic concordance, and system usability**. It does **NOT** assert definitive causal yield increases, which require multi-season randomized controlled trials (RCTs).

---

## 2. Machine Learning & Pathology Diagnostic Analysis

### 2.1 Multi-Class Confusion Matrix & Concordance
- A $28 \times 28$ confusion matrix will be constructed comparing the AI Top-1 predictions against the KVK blinded ground-truth diagnoses.
- Metrics computed per crop (Cotton, Rice, Chilli):
  - Sensitivity / Recall: $\text{TPR} = \frac{\text{TP}}{\text{TP} + \text{FN}}$
  - Specificity: $\text{TNR} = \frac{\text{TN}}{\text{TN} + \text{FP}}$
  - Precision / Positive Predictive Value: $\text{PPV} = \frac{\text{TP}}{\text{TP} + \text{FP}}$
  - Overall Concordance:
    $$\text{Concordance}_1 = \frac{\sum_{c=1}^{C} \text{TP}_c}{N_{\text{ground\_truth}}}, \quad \text{Concordance}_3 = \frac{\sum_{i=1}^{N} \mathbb{I}(y_i^* \in \text{Top3}(\hat{y}_i))}{N_{\text{ground\_truth}}}$$

### 2.2 Model Calibration & Reliability Diagrams
- Softmax output probabilities will be binned into $M = 10$ uniform intervals: $B_m = (\frac{m-1}{M}, \frac{m}{M}]$.
- For each bin, empirical accuracy $\text{acc}(B_m)$ and average confidence $\text{conf}(B_m)$ will be computed and plotted on a reliability diagram.
- **Expected Calibration Error (ECE)** will be tested against the pre-registered threshold ($\text{ECE} \le 0.12$):
  $$\text{ECE} = \sum_{m=1}^{10} \frac{|B_m|}{N} \left| \text{acc}(B_m) - \text{conf}(B_m) \right|$$

### 2.3 Out-of-Distribution (OOD) Quality Gate Assessment
- Compute Receiver Operating Characteristic (ROC) curve and Area Under ROC (AUROC) for the image quality filter separating valid crop leaves from unidentifiable images (blur, dirt, fingers, weeds).
- Pre-registered acceptance: $\text{AUROC} \ge 0.92$, False Rejection Rate $< 8.0\%$.

---

## 3. Systems Performance & Offline Sync Reliability Analysis

### 3.1 Synchronization Latency & Success Curves
- Empirical Cumulative Distribution Functions (ECDF) will be plotted for:
  - Time-to-sync from network reconnection ($t_{\text{reconnect}} \to t_{\text{synced}}$).
  - Number of retry attempts per record.
- Non-parametric Kaplan-Meier survival curves will evaluate sync completion under intermittent 2G/3G connectivity.
- Pre-registered hypothesis: $H_0: \text{SSR} < 99.0\%$ vs $H_1: \text{SSR} \ge 99.0\%$ tested via one-sample binomial test ($\alpha = 0.05$).

---

## 4. KrishiBrain RAG & Agronomic Advice Evaluation

### 4.1 PJTSAU Package of Practices Compliance
- Blinded evaluation by 2 independent KVK agronomists of 50 sampled advice responses.
- Inter-rater reliability evaluated using **Cohen's Kappa ($\kappa$)** or Intraclass Correlation Coefficient (ICC).
- Pre-registered acceptance: Mean Alignment Score $\ge 4.5 / 5.0$, with $\kappa \ge 0.75$ (substantial agreement).

### 4.2 Chemical Safety Audit
- Deterministic verification across 100% of generated responses that zero banned chemicals (e.g. Monocrotophos, Endosulfan) or unapproved off-label tank mixes were recommended without human specialist authorization.

---

## 5. Human Usability & Survey Statistics

### 5.1 System Usability Scale (SUS) Score
- The standardized 10-item Likert scale will be scored according to Brooke (1996):
  $$\text{SUS Score} = 2.5 \times \left[ \sum_{i \in \{1,3,5,7,9\}} (R_i - 1) + \sum_{j \in \{2,4,6,8,10\}} (5 - R_j) \right]$$
- Mean, median, standard deviation, and interquartile range (IQR) will be reported.
- One-sample t-test benchmarked against the industry standard usability threshold ($H_0: \mu_{\text{SUS}} \le 68.0$ vs $H_1: \mu_{\text{SUS}} > 68.0$).
- Target: $\mu_{\text{SUS}} \ge 75.0$ ($p < 0.01$).

### 5.2 Voice Adoption & Demographic Subgroup Analysis
- Subgroup analysis comparing usability scores and voice adoption across:
  - Age cohorts ($< 35$, $35–50$, $> 50$ years).
  - Literacy levels (Literate vs Semi-literate with family assistance).
  - Farm size ($1.0–2.5$ acres vs $2.6–5.0$ acres).
  - Tested using Mann-Whitney U test or Kruskal-Wallis test for non-normal distributions.
