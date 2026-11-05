# statistics inventory — 10 cards

These are decision aids, not automatic solvers. Open specific recipe only after choosing task family.

| ID | Trigger | First executable path | Verification |
|---|---|---|---|
| [`classification`](../recipes/classification.md) | Supervised classification | Majority-class baseline and stratified split | Leakage-free split and confusion matrix, PR |
| [`regression`](../recipes/regression.md) | Continuous target prediction | Median/mean baseline | MAE/RMSE on held-out data + residuals |
| [`forecasting`](../recipes/forecasting.md) | Time-series forecasting | Naive and seasonal-naive baseline | Walk-forward backtest, future-leak checks |
| [`hypothesis-test`](../recipes/hypothesis-test.md) | Statistical inference | Specify estimand and sampling unit | Sample unit, CI, effect size, multiple testing |
| [`causal-evaluation`](../recipes/causal-evaluation.md) | Treatment-effect reasoning | Causal diagram and comparison assumptions | Pretrends, confounders, placebo/sensitivity |
| [`anomaly-detection`](../recipes/anomaly-detection.md) | Outlier or anomaly screening | Robust median/MAD with clear threshold | Precision review and false-positive analysis |
| [`clustering`](../recipes/clustering.md) | Unsupervised group discovery | K-means/heuristic baseline with scaled features | Stability, feature scaling, cluster utility |
| [`simulation-montecarlo`](../recipes/simulation-montecarlo.md) | Monte Carlo uncertainty propagation | Seeded Monte Carlo using documented distributions | Convergence, CI, sensitivity to assumptions |
| [`bootstrap-ci`](../recipes/bootstrap-ci.md) | Bootstrap uncertainty interval | IID bootstrap with unit check | Coverage on synthetic known cases |
| [`experiment-design`](../recipes/experiment-design.md) | Experiment design and power | Randomization plan and target effect | Exposure unit, peeking and multiple comparisons |
