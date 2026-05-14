---
inclusion: always
---

# Python 分析程式碼模板

## CausalImpact（時間序列因果推斷）

```python
import pandas as pd
from causalimpact import CausalImpact

# data: DataFrame with columns [date, y, x1, x2...]
# y = outcome variable, x1/x2 = control series
# pre_period: 活動前的時間範圍
# post_period: 活動後的時間範圍

pre_period = ['2026-01-01', '2026-01-14']
post_period = ['2026-01-15', '2026-01-28']

ci = CausalImpact(data, pre_period, post_period)
print(ci.summary())
print(ci.summary(output='report'))
ci.plot()
```

## Difference-in-Differences (DID)

```python
import statsmodels.formula.api as smf

# data columns: outcome, treated (0/1), post (0/1), treated_post (interaction)
data['treated_post'] = data['treated'] * data['post']

model = smf.ols('outcome ~ treated + post + treated_post', data=data).fit()
print(model.summary())

# treated_post coefficient = DID estimate (causal effect)
did_effect = model.params['treated_post']
ci_low, ci_high = model.conf_int().loc['treated_post']
print(f"DID Effect: {did_effect:.4f} (95% CI: [{ci_low:.4f}, {ci_high:.4f}])")
```

## Propensity Score Matching (PSM)

```python
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
import numpy as np

# X = confounders, treatment = 0/1
lr = LogisticRegression(max_iter=1000)
lr.fit(X, treatment)
pscore = lr.predict_proba(X)[:, 1]

# Match treated to control using nearest neighbor
treated_idx = np.where(treatment == 1)[0]
control_idx = np.where(treatment == 0)[0]

nn = NearestNeighbors(n_neighbors=1, metric='euclidean')
nn.fit(pscore[control_idx].reshape(-1, 1))
distances, indices = nn.kneighbors(pscore[treated_idx].reshape(-1, 1))

matched_control_idx = control_idx[indices.flatten()]

# ATT (Average Treatment Effect on Treated)
att = outcome[treated_idx].mean() - outcome[matched_control_idx].mean()
print(f"ATT: {att:.4f}")
```

## EconML - Causal Forest (HTE)

```python
from econml.dml import CausalForestDML
import numpy as np

# Y = outcome, T = treatment (0/1), X = features for HTE, W = confounders
cf = CausalForestDML(
    model_y='auto',
    model_t='auto',
    n_estimators=200,
    random_state=42
)
cf.fit(Y, T, X=X, W=W)

# Average treatment effect
ate = cf.ate(X)
ate_ci = cf.ate_interval(X, alpha=0.05)
print(f"ATE: {ate:.4f} (95% CI: [{ate_ci[0]:.4f}, {ate_ci[1]:.4f}])")

# Heterogeneous effects by subgroup
cate = cf.effect(X)  # Individual treatment effects
```

## DoWhy（因果推論框架）

```python
import dowhy
from dowhy import CausalModel

# Define causal model
model = CausalModel(
    data=df,
    treatment='bp_purchased',
    outcome='revenue_post',
    common_causes=['vip_level', 'active_days_pre', 'revenue_pre'],
)

# Identify causal effect
identified = model.identify_effect()

# Estimate
estimate = model.estimate_effect(
    identified,
    method_name="backdoor.propensity_score_matching"
)
print(f"Causal Effect: {estimate.value:.4f}")

# Refutation (sensitivity analysis)
refute = model.refute_estimate(
    identified, estimate,
    method_name="random_common_cause"
)
print(refute)
```

## 結果報告模板

```python
def format_result(method, effect, ci_low, ci_high, p_value, n_treated, n_control):
    return f"""
📊 因果推論結果

🎯 方法：{method}
📈 處理效應：{effect:+.2f} ({effect/baseline*100:+.1f}%)
📐 95% 信賴區間：[{ci_low:.2f}, {ci_high:.2f}]
📊 統計顯著性：p = {p_value:.4f} {'✅ 顯著' if p_value < 0.05 else '❌ 不顯著'}
👥 樣本：Treatment={n_treated}, Control={n_control}
"""
```
