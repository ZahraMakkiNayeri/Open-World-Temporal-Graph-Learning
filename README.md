# FM-TGN Zero-Day

**Run:** single leave-one-category-out, held-out = `Availability.DoS`
(rarest class). Test set: 10,255 interactions, of which 174 (**1.70%**) are
zero-day. Source: `final_results.pkl` + `interaction_results_zeroday.csv`,
produced by the fixed code (`ultrat.py`).

---

## 1. Headline metrics

| Group | Metric | Value | Verdict |
|---|---|---|---|
| Link (transductive) | AP / AUC | 0.931 / 0.926 | Strong |
| Link (new-node) | AP / MRR | 0.901 / 0.403 | Strong inductive transfer |
| Ranking | MRR / Hits@1 | 0.367 / 0.266 | Modest |
| Classification | Known-cat accuracy | 0.792 | OK overall, fails on minority classes |
| **Zero-day** | **ROC-AUC** | **0.858** | Promising ranking signal |
| Zero-day | PR-AUC | 0.056 | ~3× base rate (0.017) — weak |
| Zero-day | Precision / Recall / F1 | 0.10 / 0.96 / 0.18 | Poor precision |

## 2. The core problem: precision collapses at usable thresholds

To reach 96% recall the detector flags **1,645** interactions to find 167 true
DoS — **1,478 false positives** (FPR 14.7%). Worse, the oracle best-F1 over
*all* thresholds is only **0.187**, so this is **not** a calibration problem:
the score itself cannot separate the rare class at high precision.

Precision at a fixed alert budget (the operationally relevant view):

| Budget | Recall achieved | Precision |
|---|---|---|
| FPR ≤ 0.5% | 0.00 | 0.000 |
| FPR ≤ 1% | 0.00 | 0.000 |
| FPR ≤ 5% | 0.02 | 0.006 |

At low FPR the detector recovers essentially no zero-day events. ROC-AUC 0.858
is inflated by easy negatives; under 1.7% prevalence, PR-AUC and
precision@budget tell the real story.

## 3. Classification imbalance

The confusion matrix shows the known-class head never correctly predicts
`Availability.DDoS` or `Availability.DoS`; minority classes are absorbed into
`Recon.Scanning`/`Anomaly.Traffic`. The 0.792 accuracy is driven by the
dominant Recon class. Address with class weighting or focal loss, and report
macro-F1, not just accuracy.

## 4. What is solid and reportable now

- **ROC-AUC 0.858 for a never-seen category** — a real open-world signal.
- **Strong, inductive link prediction** (new-node AP 0.901).
- **Motif-signature heatmap** — clean qualitative evidence that categories have
  distinct structural fingerprints (DDoS: high repeat-ratio; Recon: high
  fan-in & dst-concentration; Anomaly: high fan-out). This directly supports
  the central thesis that structure, not identity, encodes attack type.

## 5. Is it publishable in TDSC as-is? No — but the idea is viable.

Required before submission:

1. **Full LOCO sweep × seeds.** Hold out each of the 4 categories in turn,
   ≥3 seeds each; report mean ± std. (Notebook Section 16 already does the
   sweep — extend with seeds.)
2. **Baselines** under identical splits: closed-world TGN + max-softmax-prob,
   last-message aggregator, ID-embedding relation encoder, and a one-class /
   anomaly baseline.
3. **Re-frame zero-day reporting.** Make ROC-AUC + PR-AUC + precision@FPR the
   headline; drop F1-at-auto-threshold as the primary number. Be explicit
   about prevalence.
4. **Fix the precision problem** (this is the contribution gap to close):
   - per-known-class score standardization before combining energy/distance;
   - temperature-scaled / Mahalanobis distance instead of cosine-to-prototype;
   - calibrate at a fixed FPR budget rather than max-F1;
   - consider an "alert-ranking / triage" framing (top-k precision) rather than
     binary flagging, which matches the 0.858 ranking strength.
5. **Address class imbalance** in the classifier.

## 6. Files

- `results_tables.tex` — LaTeX tables (link + zero-day) with these exact
  numbers, ready to paste into the paper.
- Drop them into Section "Results" of `TGN_ULTRA_ZeroDay_TDSC.tex` (replace the
  placeholder `tab:main`).
