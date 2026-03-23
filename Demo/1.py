
# -*- coding: utf-8 -*-
"""
Bike Sharing (hour.csv) - 使用 XGBoost 预测小时级租赁量 cnt
兼容：
- XGBoost 3.x：使用 callbacks.EarlyStopping() 实现早停
- 旧版 scikit-learn：RMSE 用 np.sqrt(mean_squared_error(...))
输出：
- models/: xgb_bike_model.json（模型），model_meta.json（元数据）
- figs/: 特征重要性、测试集实际vs预测图
- reports/: 测试集逐小时预测明细CSV
"""

import os
import json
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# =========================
# 1) 读取数据
# =========================
fp = 'hour.csv'
df = pd.read_csv(fp)

# =========================
# 2) 基础预处理 & 特征工程
# =========================
# 日期
df['dteday'] = pd.to_datetime(df['dteday'])

# 是否周末（weekday: 0=周日, 6=周六）
df['is_weekend'] = df['weekday'].isin([0, 6]).astype(int)


# 1. 对时间特征做周期编码 (sin / cos)
# 小时、星期、月份都是周期性数据
# 例如：23点和0点其实很接近，所以用sin/cos表示更合理

time_columns = {
    'hr': 24,        # 一天24小时
    'weekday': 7,    # 一周7天
    'mnth': 12       # 一年12个月
}

for col, period in time_columns.items():
    angle = 2 * np.pi * df[col] / period
    df[col + '_sin'] = np.sin(angle)
    df[col + '_cos'] = np.cos(angle)


# 2. 数值特征 + 二值特征
base_features = [
    'temp',        # 温度
    'atemp',       # 体感温度
    'hum',         # 湿度
    'windspeed',   # 风速

    # 周期编码后的时间特征
    'hr_sin', 'hr_cos',
    'weekday_sin', 'weekday_cos',
    'mnth_sin', 'mnth_cos',

    # 二值特征
    'is_weekend',
    'workingday',
    'holiday',
    'yr'
]


# 3. 类别特征 (需要 One-Hot 编码)
cat_features = ['season', 'weathersit']

# 将类别变量转换成 one-hot
cat_encoded = pd.get_dummies(
    df[cat_features].astype('category'),
    prefix=cat_features,
    drop_first=False
)


# 4. 合并所有特征
X = pd.concat([
    df[base_features],
    cat_encoded
], axis=1)


# 5. 目标变量
y = df['cnt'].astype(float)

# =========================
# 3) 时间序切分（防泄漏）
#    - 最后 30 天做测试
#    - 往前 60 天做验证
#    - 其余做训练
# =========================
cut_test_start = df['dteday'].max() - pd.Timedelta(days=29)
cut_valid_start = cut_test_start - pd.Timedelta(days=60)

train_idx = df['dteday'] < cut_valid_start
valid_idx = (df['dteday'] >= cut_valid_start) & (df['dteday'] < cut_test_start)
test_idx  = df['dteday'] >= cut_test_start

X_train, y_train = X.loc[train_idx], y.loc[train_idx]
X_valid, y_valid = X.loc[valid_idx], y.loc[valid_idx]
X_test,  y_test  = X.loc[test_idx],  y.loc[test_idx]

# =========================
# 4) 训练 XGBoost（3.x 用 callbacks.EarlyStopping）
# =========================
import xgboost as xgb

model = xgb.XGBRegressor(
    n_estimators=2000,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    reg_alpha=0.0,
    random_state=42,
    n_jobs=-1,
    tree_method='hist',
    eval_metric='rmse'   # 评估指标
)

model.fit(
    X_train, y_train,
    eval_set=[(X_valid, y_valid)],
    verbose=False
)

# =========================
# 5) 评估（兼容旧版 sklearn）
# =========================
y_pred = model.predict(X_test)

# 旧版 sklearn 没有 squared=False，所以用开方的方式计算 RMSE
rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
mae  = float(mean_absolute_error(y_test, y_pred))
r2   = float(r2_score(y_test, y_pred))
print({'model_type': 'xgboost', 'rmse': rmse, 'mae': mae, 'r2': r2})

# =========================
# 6) 导出：模型、元数据、图表、预测CSV
# =========================
os.makedirs('models', exist_ok=True)
os.makedirs('figs', exist_ok=True)
os.makedirs('reports', exist_ok=True)

# 6.1 保存模型与元数据
feature_list = X.columns.tolist()
meta = {
    'model_type': 'xgboost',
    'features': feature_list,
    'cut_valid_start': str(cut_valid_start.date()),
    'cut_test_start': str(cut_test_start.date()),
    'metrics': {'rmse': rmse, 'mae': mae, 'r2': r2}
}

# XGBoost 原生模型（JSON）
model.save_model('models/xgb_bike_model.json')

with open('models/model_meta.json', 'w', encoding='utf-8') as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

# 6.2 特征重要性（Top 15）
importances = model.feature_importances_
imp_series = pd.Series(importances, index=feature_list).sort_values(ascending=False).head(15)

plt.figure(figsize=(8, 6))
imp_series[::-1].plot(kind='barh')
plt.title('Feature Importance (Top 15)')
plt.xlabel('Importance Score')
plt.tight_layout()
plt.savefig('figs/feature_importance_top15.png', dpi=150)
plt.close()

# 6.3 测试集：实际 vs 预测
plt.figure(figsize=(10, 4))
plt.plot(y_test.values, label='Actual', linewidth=1.2)
plt.plot(y_pred, label='Predicted', linewidth=1.2)
plt.legend()
plt.title('Test Set: Actual vs Predicted')
plt.ylabel('Rental Count (cnt)')
plt.xlabel('Sample Order (Time Increasing)')
plt.tight_layout()
plt.savefig('figs/test_actual_vs_pred.png', dpi=150)
plt.close()

# 6.4 导出测试集预测明细
out = pd.DataFrame({
    'dteday': df.loc[test_idx, 'dteday'].values,
    'hr': df.loc[test_idx, 'hr'].values,
    'actual_cnt': y_test.values,
    'pred_cnt': y_pred
})
out.to_csv('reports/test_predictions.csv', index=False)

print('✅ 训练完成，模型与图表已保存到 ./models, ./figs, ./reports')
