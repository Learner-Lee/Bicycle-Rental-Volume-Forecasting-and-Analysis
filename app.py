# -*- coding: utf-8 -*-
"""
自行车租赁数据挖掘平台 / Bike Sharing Data Mining Platform
数据来源：UCI Bike Sharing Dataset (hour.csv)
"""

import warnings
warnings.filterwarnings('ignore')

import time
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

# ──────────────────────────────────────────────────────────
# 页面配置 / Page Config
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🚲 Bike Sharing · Data Mining",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# 全局样式 / Global Styles
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a237e 0%, #283593 60%, #1565c0 100%);
}
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #e8edf5 !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2); }
[data-testid="stHeader"] { display: none; }
header[data-testid="stHeader"] { display: none; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.main { background: #f5f7fa; }
.kpi-card {
    background: white; border-radius: 14px; padding: 22px 20px 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07); text-align: center;
    border-top: 5px solid #2196F3; margin-bottom: 8px;
}
.kpi-value { font-size: 2.1rem; font-weight: 800; color: #1a237e; line-height: 1.1; }
.kpi-label { font-size: 0.85rem; color: #6b7280; margin-top: 6px; }
.insight {
    background: #e8f4fd; border-left: 5px solid #1976d2;
    border-radius: 0 10px 10px 0; padding: 12px 16px; margin: 8px 0 16px;
    font-size: 0.9rem; line-height: 1.7; color: #1a237e;
}
.algo-desc {
    background: #fafafa; border: 1px solid #e5e7eb; border-radius: 12px;
    padding: 18px 22px; line-height: 1.8; font-size: 0.92rem; margin-bottom: 18px;
}
.page-title {
    font-size: 1.75rem; font-weight: 800; color: #1a237e;
    margin-bottom: 1.4rem; padding-bottom: 0.5rem; border-bottom: 3px solid #1976d2;
}
.summary-comment {
    background: #fff8e1; border: 1px solid #ffd54f; border-radius: 12px;
    padding: 20px 24px; line-height: 1.9; font-size: 0.92rem;
}
.lang-btn {
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    font-size: 0.82rem; font-weight: 600; cursor: pointer; margin: 2px 3px;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# 语言初始化 / Language Init
# ──────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "zh"

def t(key: str, **kwargs) -> str:
    """Return translated string for current language."""
    val = TEXTS.get(key, {}).get(st.session_state.lang, key)
    return val.format(**kwargs) if kwargs else val

# ──────────────────────────────────────────────────────────
# 双语文本表 / Bilingual Text Table
# ──────────────────────────────────────────────────────────
TEXTS = {
    # ── Sidebar ──
    "app_title":          {"zh": "🚲 数据挖掘平台",           "en": "🚲 Data Mining Platform"},
    "app_subtitle":       {"zh": "自行车租赁量预测分析",       "en": "Bike Sharing Prediction"},
    "choose_algo":        {"zh": "选择算法：",                  "en": "Choose Algorithm:"},
    "dataset_info":       {
        "zh": "📦 数据集：UCI Bike Sharing<br>📊 记录数：17,379 条<br>📅 时间跨度：2011–2012",
        "en": "📦 Dataset: UCI Bike Sharing<br>📊 Records: 17,379<br>📅 Period: 2011–2012",
    },
    "done_label":         {"zh": "✅ 已完成模型：",             "en": "✅ Completed Models:"},
    "nav_dashboard":      {"zh": "📊 Dashboard",               "en": "📊 Dashboard"},
    "nav_ml":             {"zh": "🤖 机器学习",                 "en": "🤖 Machine Learning"},
    "nav_summary":        {"zh": "📋 总结报告",                 "en": "📋 Summary"},

    # ── Dashboard page ──
    "dash_title":         {"zh": "📊 数据总览 — Dashboard",    "en": "📊 Data Overview — Dashboard"},
    "kpi_rows":           {"zh": "数据总条数（条）",             "en": "Total Records"},
    "kpi_total":          {"zh": "总租赁次数（次）",             "en": "Total Rentals"},
    "kpi_avg":            {"zh": "小时均租赁量（次/时）",        "en": "Avg Hourly Rentals"},
    "kpi_max":            {"zh": "单时最高租赁量（次）",         "en": "Peak Hourly Rentals"},
    "chart_daily":        {"zh": "📈 每日总租赁量趋势（2011–2012）", "en": "📈 Daily Total Rentals Trend (2011–2012)"},
    "label_date":         {"zh": "日期",                        "en": "Date"},
    "label_daily_cnt":    {"zh": "日租赁总量",                  "en": "Daily Total"},
    "insight_daily": {
        "zh": "📌 <b>趋势洞察：</b>租赁量整体呈上升趋势，2012年明显高于2011年，说明共享单车平台处于高速增长期。每年呈现明显的<b>季节性波动</b>：夏秋（6–9月）租赁量达到峰值，冬季（12–2月）显著下降，与气温变化高度吻合。",
        "en": "📌 <b>Trend Insight:</b> Rentals show a clear upward trend — 2012 significantly higher than 2011, indicating rapid platform growth. Strong <b>seasonal cycles</b>: peak in summer/autumn (Jun–Sep), sharp decline in winter (Dec–Feb), closely tracking temperature.",
    },
    "chart_hourly":       {"zh": "🕐 各小时平均租赁量",         "en": "🕐 Average Rentals by Hour"},
    "label_hour":         {"zh": "小时",                        "en": "Hour"},
    "label_avg_cnt":      {"zh": "平均租赁量",                  "en": "Avg Rentals"},
    "insight_hourly": {
        "zh": "📌 <b>双峰通勤规律：</b>早高峰（8点）和晚高峰（17–18点）租赁量最高，体现了典型的上下班出行需求。凌晨（1–5点）几乎无人使用。",
        "en": "📌 <b>Bimodal Commute Pattern:</b> Morning peak (8am) and evening peak (5–6pm) show highest demand — classic commuter behavior. Near-zero usage from 1–5am.",
    },
    "chart_season":       {"zh": "🌡️ 各季节租赁量分布",        "en": "🌡️ Rental Distribution by Season"},
    "label_season":       {"zh": "季节",                        "en": "Season"},
    "label_cnt":          {"zh": "租赁量",                      "en": "Rentals"},
    "insight_season": {
        "zh": "📌 <b>季节效应：</b>秋季租赁中位数最高，夏季其次。春季偏低（天气不稳定），冬季最低（严寒限制出行）。",
        "en": "📌 <b>Seasonal Effect:</b> Autumn has the highest median rentals, followed by summer. Spring is lower (unstable weather), winter is lowest (cold restricts cycling).",
    },
    "chart_weather":      {"zh": "☁️ 天气状况对租赁量的影响",   "en": "☁️ Impact of Weather on Rentals"},
    "label_weather":      {"zh": "天气",                        "en": "Weather"},
    "insight_weather": {
        "zh": "📌 <b>天气决定性影响：</b>晴天租赁量约是大雨/大雪天气的 <b>10倍</b>。天气是用户出行决策最直接的外部影响因素，在预测模型中权重极高。",
        "en": "📌 <b>Weather is Decisive:</b> Clear weather generates ~<b>10×</b> more rentals than heavy rain/snow. Weather is the most direct external factor driving rental demand.",
    },
    "chart_workday":      {"zh": "📅 工作日 vs 休息日（按小时）", "en": "📅 Workday vs Weekend (by Hour)"},
    "label_day_type":     {"zh": "",                             "en": ""},
    "workday_label":      {"zh": "💼 工作日",                   "en": "💼 Workday"},
    "weekend_label":      {"zh": "🏖 休息日",                   "en": "🏖 Weekend"},
    "insight_workday": {
        "zh": "📌 <b>出行模式差异：</b>工作日呈 <b>双峰曲线</b>（通勤主导），休息日为 <b>单峰平缓曲线</b>（10–15点，休闲主导）。两类用户行为模式截然不同。",
        "en": "📌 <b>Different Patterns:</b> Workdays show a <b>bimodal curve</b> (commuter-driven), while weekends show a <b>single broad peak</b> (10am–3pm, leisure-driven). Distinct user behavior.",
    },
    "chart_heatmap":      {"zh": "🔍 数值特征相关性热图",        "en": "🔍 Numerical Feature Correlation Heatmap"},
    "insight_heatmap": {
        "zh": "📌 <b>相关性解读：</b>温度（temp/atemp）与租赁量呈<b>正相关</b>（r ≈ 0.40），暖和天气鼓励出行；湿度（hum）和风速（windspeed）与租赁量呈<b>负相关</b>，不适宜骑车的天气会抑制需求。注册用户（registered）贡献了约 <b>80%</b> 的总租赁量，是平台的核心用户群体。",
        "en": "📌 <b>Correlation Insights:</b> Temperature (temp/atemp) is <b>positively correlated</b> with rentals (r ≈ 0.40) — warm weather encourages cycling. Humidity and wind speed are <b>negatively correlated</b>. Registered users account for ~<b>80%</b> of total rentals.",
    },
    "raw_data_expander":  {"zh": "📋 原始数据预览（前100行）",   "en": "📋 Raw Data Preview (first 100 rows)"},

    # ── Model page ──
    "complexity":         {"zh": "复杂度：",                    "en": "Complexity:"},
    "algo_intro":         {"zh": "📚 算法介绍（点击展开/收起）", "en": "📚 Algorithm Introduction (click to expand)"},
    "run_btn":            {"zh": "▶ 运行 {name}",               "en": "▶ Run {name}"},
    "spinner":            {"zh": "⏳ 正在训练 {name}，请稍候...", "en": "⏳ Training {name}, please wait..."},
    "success":            {"zh": "✅ {name} 训练完成！",         "en": "✅ {name} training complete!"},
    "run_hint":           {"zh": "👆 点击上方「运行」按钮，开始训练模型并查看结果。", "en": "👆 Click the Run button above to train the model and view results."},
    "metrics_title":      {"zh": "📊 模型评估指标",              "en": "📊 Model Evaluation Metrics"},
    "metric_rmse":        {"zh": "RMSE（均方根误差）",           "en": "RMSE"},
    "metric_rmse_help":   {"zh": "越小越好，单位与租赁量相同",   "en": "Lower is better; same unit as rentals"},
    "metric_mae":         {"zh": "MAE（平均绝对误差）",          "en": "MAE"},
    "metric_mae_help":    {"zh": "越小越好，直观反映平均误差",   "en": "Lower is better; average absolute error"},
    "metric_r2":          {"zh": "R²（决定系数）",               "en": "R² Score"},
    "metric_r2_help":     {"zh": "越接近1越好；>0.9为优秀",      "en": "Closer to 1 is better; >0.9 is excellent"},
    "metric_time":        {"zh": "训练时长",                     "en": "Train Time"},
    "metric_time_help":   {"zh": "模型拟合所用时间",             "en": "Time to fit the model"},
    "chart_ts":           {"zh": "📉 实际值 vs 预测值（前500个测试点）", "en": "📉 Actual vs Predicted (first 500 test points)"},
    "label_sample_idx":   {"zh": "样本序号（时间递增）",         "en": "Sample Index (time-ordered)"},
    "label_rental":       {"zh": "租赁量",                      "en": "Rentals"},
    "legend_actual":      {"zh": "实际值",                      "en": "Actual"},
    "legend_pred":        {"zh": "预测值",                      "en": "Predicted"},
    "chart_scatter":      {"zh": "🎯 预测散点图",                "en": "🎯 Prediction Scatter Plot"},
    "label_actual":       {"zh": "实际值",                      "en": "Actual"},
    "label_predicted":    {"zh": "预测值",                      "en": "Predicted"},
    "perfect_line":       {"zh": "完美预测线",                   "en": "Perfect Prediction"},
    "chart_fi":           {"zh": "🔑 特征重要性（Top 10）",      "en": "🔑 Feature Importance (Top 10)"},
    "label_importance":   {"zh": "重要性分数",                   "en": "Importance Score"},
    "label_feat_name":    {"zh": "特征名称",                     "en": "Feature Name"},
    "chart_residual":     {"zh": "📊 残差分布（预测误差直方图）", "en": "📊 Residual Distribution (Error Histogram)"},
    "label_residual":     {"zh": "残差（实际 − 预测）",          "en": "Residual (Actual − Predicted)"},
    "label_freq":         {"zh": "频次",                        "en": "Count"},
    "zero_error":         {"zh": "零误差",                      "en": "Zero Error"},
    "insight_residual": {
        "zh": "📌 <b>残差解读：</b>理想情况下残差应近似<b>正态分布</b>且以0为中心，说明模型无系统性偏差。若残差明显偏斜或出现双峰，则说明模型对某类样本（如高峰时段）存在系统性低估/高估。",
        "en": "📌 <b>Residual Insight:</b> Ideally residuals should follow a <b>normal distribution</b> centered at 0, indicating no systematic bias. Skewed or bimodal residuals suggest the model under/over-estimates certain samples (e.g., peak hours).",
    },
    "detail_expander":    {"zh": "📋 查看预测明细表（前100行）",  "en": "📋 View Prediction Details (first 100 rows)"},
    "col_actual":         {"zh": "实际租赁量",                   "en": "Actual"},
    "col_pred":           {"zh": "预测租赁量",                   "en": "Predicted"},
    "col_err":            {"zh": "误差",                        "en": "Error"},
    "col_err_pct":        {"zh": "绝对误差率(%)",                "en": "Abs Error (%)"},

    # ── Summary page ──
    "sum_title":          {"zh": "📋 模型总结报告 — Summary",    "en": "📋 Model Summary Report"},
    "sum_no_model": {
        "zh": "⚠️ 尚未运行任何模型，请先前往「机器学习」页面运行模型。",
        "en": "⚠️ No models have been run yet. Please go to the Machine Learning page first.",
    },
    "sum_hint": {
        "zh": "建议运行顺序：线性回归 → 岭回归 → 随机森林 → 梯度提升 → XGBoost",
        "en": "Suggested order: Linear → Ridge → Random Forest → Gradient Boosting → XGBoost",
    },
    "sum_banner": {
        "zh": "🏆 已完成 <b>{n}/{total}</b> 个模型训练 &nbsp;|&nbsp; 最高 R² 模型：<b>{best_r2}</b> &nbsp;|&nbsp; 最低 RMSE 模型：<b>{best_rmse}</b>",
        "en": "🏆 Completed <b>{n}/{total}</b> models &nbsp;|&nbsp; Best R²: <b>{best_r2}</b> &nbsp;|&nbsp; Lowest RMSE: <b>{best_rmse}</b>",
    },
    "sum_table_title":    {"zh": "📊 模型性能对比表",             "en": "📊 Model Performance Comparison"},
    "col_model":          {"zh": "模型",                        "en": "Model"},
    "col_train_time":     {"zh": "训练时长(s)",                  "en": "Train Time(s)"},
    "chart_r2_bar":       {"zh": "📈 R² 对比（越高越好）",       "en": "📈 R² Comparison (higher is better)"},
    "chart_rmse_bar":     {"zh": "📉 RMSE 对比（越低越好）",     "en": "📉 RMSE Comparison (lower is better)"},
    "chart_time_bar":     {"zh": "⏱️ 训练时长对比",              "en": "⏱️ Training Time Comparison"},
    "yaxis_time":         {"zh": "训练时长（秒）",               "en": "Training Time (s)"},
    "chart_radar":        {"zh": "🕸️ 综合雷达对比图",            "en": "🕸️ Comprehensive Radar Chart"},
    "radar_hint":         {"zh": "运行 2 个以上模型后显示雷达图。", "en": "Run 2+ models to display the radar chart."},
    "radar_r2":           {"zh": "R²精度",                      "en": "R² Score"},
    "radar_rmse":         {"zh": "RMSE(低好)",                  "en": "RMSE(↓)"},
    "radar_mae":          {"zh": "MAE(低好)",                   "en": "MAE(↓)"},
    "radar_spd":          {"zh": "训练速度",                     "en": "Train Speed"},
    "excellent_threshold":{"zh": "优秀阈值 0.90",                "en": "Excellent 0.90"},
    "sum_analysis_title": {"zh": "💬 综合分析与学习建议",         "en": "💬 Analysis & Learning Suggestions"},
}

# ──────────────────────────────────────────────────────────
# 常量 / Constants
# ──────────────────────────────────────────────────────────
SEASON_MAP_ZH  = {1: "春季", 2: "夏季", 3: "秋季", 4: "冬季"}
SEASON_MAP_EN  = {1: "Spring", 2: "Summer", 3: "Autumn", 4: "Winter"}
WEATHER_MAP_ZH = {1: "晴天/少云", 2: "雾天/多云", 3: "小雨/小雪", 4: "大雨/大雪"}
WEATHER_MAP_EN = {1: "Clear/Partly Cloudy", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}

SEASON_ORDER_ZH  = ["春季", "夏季", "秋季", "冬季"]
SEASON_ORDER_EN  = ["Spring", "Summer", "Autumn", "Winter"]

MODEL_KEYS   = ["线性回归", "岭回归", "随机森林", "梯度提升", "XGBoost"]
MODEL_NAMES_EN = {
    "线性回归": "Linear Regression",
    "岭回归":   "Ridge Regression",
    "随机森林": "Random Forest",
    "梯度提升": "Gradient Boosting",
    "XGBoost":  "XGBoost",
}
MODEL_COLORS = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#F44336"]
PLOT_CONFIG  = dict(plot_bgcolor="white", paper_bgcolor="white")


def mname(key: str) -> str:
    """Return model display name in current language."""
    if st.session_state.lang == "en":
        return MODEL_NAMES_EN.get(key, key)
    return key


# ──────────────────────────────────────────────────────────
# 数据加载 & 预处理
# ──────────────────────────────────────────────────────────
@st.cache_data
def load_raw() -> pd.DataFrame:
    df = pd.read_csv("/app/data/hour.csv")
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df


@st.cache_data
def prepare_ml_data():
    df = load_raw().copy()
    df["is_weekend"] = df["weekday"].isin([0, 6]).astype(int)
    for col, period in {"hr": 24, "weekday": 7, "mnth": 12}.items():
        a = 2 * np.pi * df[col] / period
        df[f"{col}_sin"] = np.sin(a)
        df[f"{col}_cos"] = np.cos(a)
    base_feats = [
        "temp", "atemp", "hum", "windspeed",
        "hr_sin", "hr_cos", "weekday_sin", "weekday_cos",
        "mnth_sin", "mnth_cos",
        "is_weekend", "workingday", "holiday", "yr",
    ]
    cat_enc = pd.get_dummies(
        df[["season", "weathersit"]].astype("category"),
        prefix=["season", "weathersit"], drop_first=False,
    )
    X = pd.concat([df[base_feats], cat_enc], axis=1).astype(float)
    y = df["cnt"].astype(float)
    t_max    = df["dteday"].max()
    cut_test = t_max - pd.Timedelta(days=29)
    cut_val  = cut_test - pd.Timedelta(days=60)
    tr_mask  = df["dteday"] < cut_val
    te_mask  = df["dteday"] >= cut_test
    return (
        X[tr_mask], y[tr_mask],
        X[te_mask], y[te_mask],
        df.loc[te_mask, "dteday"].values,
    )


def calc_metrics(y_true, y_pred) -> dict:
    return {
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE":  float(mean_absolute_error(y_true, y_pred)),
        "R²":   float(r2_score(y_true, y_pred)),
    }


def train_model(name: str, X_tr, y_tr, X_te, y_te) -> dict:
    t0 = time.time()
    if name == "线性回归":
        m = LinearRegression()
        m.fit(X_tr, y_tr)
        y_pred = np.maximum(m.predict(X_te), 0)
        fi = pd.Series(np.abs(m.coef_), index=X_tr.columns)
    elif name == "岭回归":
        m = Ridge(alpha=1.0)
        m.fit(X_tr, y_tr)
        y_pred = np.maximum(m.predict(X_te), 0)
        fi = pd.Series(np.abs(m.coef_), index=X_tr.columns)
    elif name == "随机森林":
        m = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        fi = pd.Series(m.feature_importances_, index=X_tr.columns)
    elif name == "梯度提升":
        m = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42)
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        fi = pd.Series(m.feature_importances_, index=X_tr.columns)
    elif name == "XGBoost":
        m = xgb.XGBRegressor(
            n_estimators=500, learning_rate=0.05, max_depth=6,
            subsample=0.8, colsample_bytree=0.8,
            random_state=42, n_jobs=-1, tree_method="hist",
        )
        m.fit(X_tr, y_tr, verbose=False)
        y_pred = m.predict(X_te)
        fi = pd.Series(m.feature_importances_, index=X_tr.columns)
    elapsed = round(time.time() - t0, 2)
    metrics = calc_metrics(y_te.values, y_pred)
    metrics["训练时长(s)"] = elapsed
    fi_top10 = fi.sort_values(ascending=False).head(10)
    return {"metrics": metrics, "y_pred": y_pred, "y_test": y_te.values, "feature_importance": fi_top10}


# ══════════════════════════════════════════════════════════
# 模型算法介绍（双语）
# ══════════════════════════════════════════════════════════
MODEL_INFO = {
    "线性回归": {
        "icon": "📈", "complexity": "⭐",
        "class_name": "LinearRegression", "params_str": "fit_intercept=True",
        "desc_zh": """
**线性回归（Linear Regression）** 是机器学习中最基础的监督学习算法，也是理解其他复杂模型的基石。

**核心思想：** 寻找一组权重 *w*，使得 $\\hat{y} = w_0 + w_1x_1 + \\cdots + w_nx_n$ 与真实值 *y* 的误差最小（最小二乘法）。

**优点：**
- ✅ 概念简单，结果可直接解释（系数 = 特征对租赁量的影响大小）
- ✅ 训练速度极快（毫秒级）
- ✅ 适合作为基准模型（Baseline），衡量其他算法的提升幅度

**缺点：**
- ❌ 假设特征与目标之间是线性关系，无法捕捉非线性模式
- ❌ 对异常值敏感
""",
        "desc_en": """
**Linear Regression** is the most fundamental supervised learning algorithm — the foundation for understanding more complex models.

**Core Idea:** Find weights *w* that minimize the difference between $\\hat{y} = w_0 + w_1x_1 + \\cdots + w_nx_n$ and the true value *y* (Ordinary Least Squares).

**Pros:**
- ✅ Simple and interpretable (coefficient = feature's influence on rentals)
- ✅ Extremely fast to train (milliseconds)
- ✅ Great baseline model to measure improvement from other algorithms

**Cons:**
- ❌ Assumes linear relationship — cannot capture nonlinear patterns
- ❌ Sensitive to outliers
""",
    },
    "岭回归": {
        "icon": "📉", "complexity": "⭐⭐",
        "class_name": "Ridge", "params_str": "alpha=1.0",
        "desc_zh": """
**岭回归（Ridge Regression）** 是线性回归加上 **L2 正则化** 的改进版本，通过在损失函数中加入权重平方和惩罚项来解决过拟合。

**数学表达：** 最小化 $||y - Xw||^2 + \\alpha ||w||^2$，其中 $\\alpha$ 控制正则化强度。

**优点：**
- ✅ 有效解决**多重共线性**问题（本数据集中 temp 和 atemp 高度相关）
- ✅ 防止过拟合，泛化能力优于普通线性回归
- ✅ 仍然保持线性模型的可解释性

**缺点：**
- ❌ 仍然是线性模型，无法建模非线性关系
- ❌ 需要调整超参数 α
""",
        "desc_en": """
**Ridge Regression** improves on Linear Regression by adding **L2 regularization**, adding a penalty to the loss function to prevent overfitting.

**Math:** Minimize $||y - Xw||^2 + \\alpha ||w||^2$, where $\\alpha$ controls regularization strength.

**Pros:**
- ✅ Handles **multicollinearity** (temp and atemp are highly correlated in this dataset)
- ✅ Better generalization than plain linear regression
- ✅ Still interpretable as a linear model

**Cons:**
- ❌ Still a linear model — cannot model nonlinear relationships
- ❌ Requires tuning hyperparameter α
""",
    },
    "随机森林": {
        "icon": "🌲", "complexity": "⭐⭐⭐",
        "class_name": "RandomForestRegressor",
        "params_str": "n_estimators=100, max_depth=10, random_state=42",
        "desc_zh": """
**随机森林（Random Forest）** 是一种**集成学习**算法，通过构建多棵决策树并对预测结果取平均来提升精度（Bagging 思想）。

**核心思想：** "三个臭皮匠，顶个诸葛亮" — 许多弱学习器（浅决策树）的集成，比单个强学习器更稳健。

**优点：**
- ✅ 天然处理**非线性关系**，无需特征缩放
- ✅ 对异常值和噪声鲁棒
- ✅ 内置**特征重要性**评估
- ✅ 可并行训练（`n_jobs=-1`），速度较快

**缺点：**
- ❌ 模型体积较大（100棵树），预测略慢
- ❌ 可解释性不如线性模型
""",
        "desc_en": """
**Random Forest** is an **ensemble learning** algorithm that builds multiple decision trees and averages their predictions (Bagging).

**Core Idea:** "Wisdom of the crowd" — many weak learners (shallow trees) combined are more robust than a single strong learner.

**Pros:**
- ✅ Naturally handles **nonlinear relationships**, no feature scaling needed
- ✅ Robust to outliers and noise
- ✅ Built-in **feature importance** ranking
- ✅ Parallel training (`n_jobs=-1`) — fast

**Cons:**
- ❌ Large model size (100 trees), slower predictions
- ❌ Less interpretable than linear models
""",
    },
    "梯度提升": {
        "icon": "🚀", "complexity": "⭐⭐⭐⭐",
        "class_name": "GradientBoostingRegressor",
        "params_str": "n_estimators=200, learning_rate=0.1, max_depth=5",
        "desc_zh": """
**梯度提升（Gradient Boosting）** 是另一种强大的集成方法，以**串行**方式逐步构建树：每棵新树专注于修正前一棵树的**残差**（预测误差）。

**核心思想：** 沿梯度下降方向不断减小残差，每一步让模型"精准补刀"弱点。

**优点：**
- ✅ 通常比随机森林精度更高（Boosting > Bagging）
- ✅ 对混合类型特征处理能力强
- ✅ 内置特征重要性

**缺点：**
- ❌ **串行训练**较慢，无法并行化
- ❌ 超参数较多，更容易过拟合
""",
        "desc_en": """
**Gradient Boosting** builds trees **sequentially**: each new tree focuses on correcting the **residuals** (errors) of the previous tree.

**Core Idea:** Gradually reduce residuals along the gradient descent direction — each step precisely targets the model's weaknesses.

**Pros:**
- ✅ Generally higher accuracy than Random Forest (Boosting > Bagging)
- ✅ Handles mixed feature types well
- ✅ Built-in feature importance

**Cons:**
- ❌ **Sequential training** — cannot be parallelized, slower
- ❌ More hyperparameters — prone to overfitting without careful tuning
""",
    },
    "XGBoost": {
        "icon": "⚡", "complexity": "⭐⭐⭐⭐⭐",
        "class_name": "XGBRegressor",
        "params_str": "n_estimators=500, learning_rate=0.05, max_depth=6",
        "desc_zh": """
**XGBoost（Extreme Gradient Boosting）** 是梯度提升的**工程优化版**，由陈天奇于2014年提出，曾横扫众多机器学习竞赛冠军（Kaggle首选算法）。

**相比传统梯度提升的改进：**
- 🔬 二阶泰勒展开——更精确的梯度近似
- 🛡 内置正则化（L1/L2）——防止过拟合
- ⚡ 并行化树节点分裂——速度大幅提升
- 🏗 直方图算法（`tree_method='hist'`）——内存高效

**优点：**
- ✅ 速度快、精度高
- ✅ 综合性能通常是表格数据的天花板
- ✅ 超参数丰富，可精细调优

**缺点：**
- ❌ 超参数众多，调参复杂
- ❌ 可解释性不如线性模型
""",
        "desc_en": """
**XGBoost (Extreme Gradient Boosting)** is an engineered optimization of Gradient Boosting, introduced by Tianqi Chen in 2014 — a dominant algorithm in Kaggle competitions.

**Key Improvements over Gradient Boosting:**
- 🔬 Second-order Taylor expansion — more accurate gradient approximation
- 🛡 Built-in L1/L2 regularization — prevents overfitting
- ⚡ Parallelized node splitting — much faster training
- 🏗 Histogram algorithm (`tree_method='hist'`) — memory efficient

**Pros:**
- ✅ Fast and highly accurate
- ✅ State-of-the-art performance on tabular data
- ✅ Rich hyperparameters for fine-tuning

**Cons:**
- ❌ Many hyperparameters — complex to tune
- ❌ Less interpretable than linear models
""",
    },
}

SUMMARY_COMMENT_ZH = """
### 📝 模型分析报告

#### 1. 线性模型（线性回归 & 岭回归）
线性模型训练速度极快（通常 < 0.1秒），是学习机器学习的最佳起点。
但自行车租赁量受**时间（小时）、天气、季节**的非线性影响，线性假设本身存在局限，
因此在精度上不如集成模型。岭回归通过 L2 正则化解决了 `temp` 与 `atemp`
高度相关（多重共线性）的问题，表现略优于普通线性回归。

#### 2. 集成树模型（随机森林、梯度提升、XGBoost）
三种基于决策树的集成算法均能捕捉特征间的**非线性关系**，R² 显著更高，
预测误差更小。其中：
- **随机森林** 通过并行 Bagging 降低方差，训练较快且稳定
- **梯度提升** 串行 Boosting，偏差更低但训练较慢
- **XGBoost** 兼顾精度与速度，综合表现最佳

#### 3. 模型选择建议

| 场景 | 推荐模型 | 理由 |
|------|----------|------|
| 初学入门、概念教学 | **线性回归** | 公式直观，系数可解释 |
| 生产部署 | **XGBoost** | 精度最高，支持大规模数据 |
| 重视可解释性 | **随机森林** | 特征重要性清晰，树结构可视化 |

#### 4. 最重要的特征
综合各模型的特征重要性分析，影响自行车租赁量最关键的因素是：
1. **`hr`（小时）** — 通勤规律决定了一天内的租赁峰谷
2. **`temp/atemp`（温度）** — 天气舒适度是核心驱动
3. **`yr`（年份）** — 反映平台用户增长趋势
4. **`workingday`（工作日）** — 决定出行模式类型

> 💡 **No Free Lunch 定理：** 没有任何模型在所有问题上都最优。
> 在实际应用中，选择模型需综合考虑**精度、速度、可解释性**与**数据规模**。
"""

SUMMARY_COMMENT_EN = """
### 📝 Model Analysis Report

#### 1. Linear Models (Linear Regression & Ridge Regression)
Linear models train extremely fast (usually < 0.1s) and are the best starting point for learning ML.
However, bike rental demand is influenced by **nonlinear** interactions between time (hour), weather, and season,
so linear assumptions are inherently limited. Ridge Regression, with L2 regularization, handles the high
correlation between `temp` and `atemp` (multicollinearity) better than plain Linear Regression.

#### 2. Ensemble Tree Models (Random Forest, Gradient Boosting, XGBoost)
All three tree-based ensembles capture **nonlinear feature interactions**, achieving significantly higher R²
and lower prediction error. Specifically:
- **Random Forest** uses parallel Bagging to reduce variance — fast and stable
- **Gradient Boosting** uses sequential Boosting for lower bias — slower but more accurate
- **XGBoost** balances accuracy and speed — best overall performance

#### 3. Model Selection Guide

| Scenario | Recommended | Reason |
|----------|-------------|--------|
| Learning / teaching | **Linear Regression** | Intuitive formula, interpretable coefficients |
| Production deployment | **XGBoost** | Highest accuracy, scalable to large datasets |
| Interpretability focus | **Random Forest** | Clear feature importance, visualizable trees |

#### 4. Most Important Features
Across all models, the key factors driving bike rental demand are:
1. **`hr` (Hour)** — commuter patterns drive intra-day peaks and valleys
2. **`temp/atemp` (Temperature)** — weather comfort is the core driver
3. **`yr` (Year)** — reflects platform user growth trend
4. **`workingday`** — determines commuting vs. leisure travel mode

> 💡 **No Free Lunch Theorem:** No single model is best for all problems.
> In practice, model selection must balance **accuracy, speed, interpretability**, and **data scale**.
"""


# ══════════════════════════════════════════════════════════
# 页面渲染函数 / Page Functions
# ══════════════════════════════════════════════════════════

def page_dashboard():
    df = load_raw().copy()
    lang = st.session_state.lang
    season_map  = SEASON_MAP_EN  if lang == "en" else SEASON_MAP_ZH
    weather_map = WEATHER_MAP_EN if lang == "en" else WEATHER_MAP_ZH
    season_order = SEASON_ORDER_EN if lang == "en" else SEASON_ORDER_ZH
    df["season_label"]  = df["season"].map(season_map)
    df["weather_label"] = df["weathersit"].map(weather_map)

    st.markdown(f'<div class="page-title">{t("dash_title")}</div>', unsafe_allow_html=True)

    # KPI 卡片
    c1, c2, c3, c4 = st.columns(4)
    kpi_data = [
        ("#2196F3", "#1a237e", f"{len(df):,}",             t("kpi_rows")),
        ("#4CAF50", "#1b5e20", f"{int(df['cnt'].sum()):,}", t("kpi_total")),
        ("#FF9800", "#e65100", f"{int(df['cnt'].mean())}",  t("kpi_avg")),
        ("#9C27B0", "#4a148c", f"{int(df['cnt'].max())}",   t("kpi_max")),
    ]
    for col, (border, val_color, val, label) in zip([c1, c2, c3, c4], kpi_data):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{border}">
              <div class="kpi-value" style="color:{val_color}">{val}</div>
              <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 1. 每日趋势
    st.subheader(t("chart_daily"))
    daily = df.groupby("dteday")["cnt"].sum().reset_index()
    fig1 = px.area(
        daily, x="dteday", y="cnt",
        labels={"dteday": t("label_date"), "cnt": t("label_daily_cnt")},
        color_discrete_sequence=["#2196F3"],
    )
    fig1.update_traces(line_width=1.5, fillcolor="rgba(33,150,243,0.15)")
    fig1.update_layout(**PLOT_CONFIG, height=300, hovermode="x unified",
                       xaxis_title="", yaxis_gridcolor="#f0f0f0", xaxis_showgrid=False)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown(f'<div class="insight">{t("insight_daily")}</div>', unsafe_allow_html=True)
    st.divider()

    # 2. 小时分布 & 季节分布
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(t("chart_hourly"))
        hourly = df.groupby("hr")["cnt"].mean().reset_index()
        fig2 = px.bar(
            hourly, x="hr", y="cnt",
            labels={"hr": t("label_hour"), "cnt": t("label_avg_cnt")},
            color="cnt", color_continuous_scale="Blues",
        )
        fig2.update_layout(**PLOT_CONFIG, height=300, showlegend=False,
                           coloraxis_showscale=False, yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(f'<div class="insight">{t("insight_hourly")}</div>', unsafe_allow_html=True)

    with col_b:
        st.subheader(t("chart_season"))
        fig3 = px.box(
            df, x="season_label", y="cnt",
            labels={"season_label": t("label_season"), "cnt": t("label_cnt")},
            category_orders={"season_label": season_order},
            color="season_label",
            color_discrete_sequence=["#66BB6A", "#FFA726", "#EF5350", "#42A5F5"],
        )
        fig3.update_layout(**PLOT_CONFIG, height=300, showlegend=False,
                           yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown(f'<div class="insight">{t("insight_season")}</div>', unsafe_allow_html=True)

    st.divider()

    # 3. 天气 & 工作日
    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader(t("chart_weather"))
        weather_avg = (
            df.groupby("weather_label")["cnt"].mean()
            .reset_index().sort_values("cnt", ascending=False)
        )
        fig4 = px.bar(
            weather_avg, x="weather_label", y="cnt",
            labels={"weather_label": t("label_weather"), "cnt": t("label_avg_cnt")},
            color="cnt", color_continuous_scale="RdYlGn",
        )
        fig4.update_layout(**PLOT_CONFIG, height=300, showlegend=False,
                           coloraxis_showscale=False, yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown(f'<div class="insight">{t("insight_weather")}</div>', unsafe_allow_html=True)

    with col_d:
        st.subheader(t("chart_workday"))
        hwd = df.groupby(["hr", "workingday"])["cnt"].mean().reset_index()
        hwd["day_type"] = hwd["workingday"].map({0: t("weekend_label"), 1: t("workday_label")})
        fig5 = px.line(
            hwd, x="hr", y="cnt", color="day_type",
            labels={"hr": t("label_hour"), "cnt": t("label_avg_cnt"), "day_type": ""},
            color_discrete_sequence=["#FF7043", "#1E88E5"],
        )
        fig5.update_layout(**PLOT_CONFIG, height=300, hovermode="x unified",
                           yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown(f'<div class="insight">{t("insight_workday")}</div>', unsafe_allow_html=True)

    st.divider()

    # 4. 相关性热图
    st.subheader(t("chart_heatmap"))
    num_cols = ["temp", "atemp", "hum", "windspeed", "casual", "registered", "cnt"]
    corr_vals = df[num_cols].corr().values
    fig6 = go.Figure(go.Heatmap(
        z=corr_vals, x=num_cols, y=num_cols,
        colorscale="RdBu", zmid=0,
        text=np.round(corr_vals, 2), texttemplate="%{text}",
        textfont={"size": 11}, hoverongaps=False,
    ))
    fig6.update_layout(**PLOT_CONFIG, height=400)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown(f'<div class="insight">{t("insight_heatmap")}</div>', unsafe_allow_html=True)

    # 5. 原始数据预览
    with st.expander(t("raw_data_expander")):
        st.dataframe(df.head(100), use_container_width=True)


def page_model(name: str):
    info = MODEL_INFO[name]
    display = mname(name)
    desc = info["desc_en"] if st.session_state.lang == "en" else info["desc_zh"]

    st.markdown(
        f'<div class="page-title">{info["icon"]} {display} '
        f'<span style="font-size:1rem;color:#64748b;">{t("complexity")}{info["complexity"]}</span></div>',
        unsafe_allow_html=True,
    )

    with st.expander(t("algo_intro"), expanded=True):
        st.markdown(f'<div class="algo-desc">{desc}</div>', unsafe_allow_html=True)
        st.code(
            f"from sklearn... import {info['class_name']}\n"
            f"model = {info['class_name']}({info['params_str']})\n"
            f"model.fit(X_train, y_train)\n"
            f"y_pred = model.predict(X_test)",
            language="python",
        )

    key = f"result_{name}"
    btn_col, _ = st.columns([1, 4])
    with btn_col:
        run_clicked = st.button(
            t("run_btn", name=display), type="primary", use_container_width=True
        )

    if run_clicked:
        X_tr, y_tr, X_te, y_te, _ = prepare_ml_data()
        with st.spinner(t("spinner", name=display)):
            result = train_model(name, X_tr, y_tr, X_te, y_te)
            st.session_state[key] = result
        st.success(t("success", name=display))

    if key not in st.session_state:
        st.info(t("run_hint"))
        return

    res     = st.session_state[key]
    metrics = res["metrics"]
    y_pred  = res["y_pred"]
    y_true  = res["y_test"]
    fi      = res["feature_importance"]

    st.divider()

    # 指标卡片
    st.subheader(t("metrics_title"))
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(t("metric_rmse"),  f"{metrics['RMSE']:.2f}",        help=t("metric_rmse_help"))
    with m2:
        st.metric(t("metric_mae"),   f"{metrics['MAE']:.2f}",         help=t("metric_mae_help"))
    with m3:
        st.metric(t("metric_r2"),    f"{metrics['R²']:.4f}",          help=t("metric_r2_help"))
    with m4:
        st.metric(t("metric_time"),  f"{metrics['训练时长(s)']}s",     help=t("metric_time_help"))

    st.divider()

    # 预测对比 + 散点图
    col1, col2 = st.columns([3, 2])
    n_show = min(500, len(y_true))

    with col1:
        st.subheader(t("chart_ts"))
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(
            y=y_true[:n_show], name=t("legend_actual"),
            line=dict(color="#1E88E5", width=1.5),
        ))
        fig_ts.add_trace(go.Scatter(
            y=y_pred[:n_show], name=t("legend_pred"),
            line=dict(color="#E53935", width=1.5, dash="dot"),
        ))
        fig_ts.update_layout(
            **PLOT_CONFIG, height=360, hovermode="x unified",
            xaxis_title=t("label_sample_idx"), yaxis_title=t("label_rental"),
            yaxis_gridcolor="#f0f0f0", legend=dict(x=0, y=1),
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    with col2:
        st.subheader(t("chart_scatter"))
        fig_sc = px.scatter(
            x=y_true, y=y_pred,
            labels={"x": t("label_actual"), "y": t("label_predicted")},
            opacity=0.35, color_discrete_sequence=["#7B1FA2"],
        )
        max_v = max(float(y_true.max()), float(y_pred.max())) * 1.05
        fig_sc.add_shape(
            type="line", x0=0, y0=0, x1=max_v, y1=max_v,
            line=dict(color="#E53935", dash="dash", width=1.5),
        )
        fig_sc.add_annotation(
            x=max_v * 0.85, y=max_v * 0.9, text=t("perfect_line"),
            showarrow=False, font=dict(color="#E53935", size=11),
        )
        fig_sc.update_layout(**PLOT_CONFIG, height=360)
        st.plotly_chart(fig_sc, use_container_width=True)

    # 特征重要性
    st.subheader(t("chart_fi"))
    feat_df = fi.reset_index()
    feat_df.columns = [t("label_feat_name"), t("label_importance")]
    feat_df = feat_df.sort_values(t("label_importance"))
    fig_fi = px.bar(
        feat_df, x=t("label_importance"), y=t("label_feat_name"), orientation="h",
        color=t("label_importance"), color_continuous_scale="Blues",
        labels={t("label_importance"): t("label_importance"), t("label_feat_name"): t("label_feat_name")},
    )
    fig_fi.update_layout(**PLOT_CONFIG, height=360, showlegend=False,
                         coloraxis_showscale=False, xaxis_gridcolor="#f0f0f0")
    st.plotly_chart(fig_fi, use_container_width=True)

    # 残差分布
    st.subheader(t("chart_residual"))
    residuals = y_true - y_pred
    fig_res = px.histogram(
        residuals, nbins=60,
        labels={"value": t("label_residual"), "count": t("label_freq")},
        color_discrete_sequence=["#43A047"],
    )
    fig_res.add_vline(
        x=0, line_dash="dash", line_color="#E53935",
        annotation_text=t("zero_error"), annotation_position="top",
    )
    fig_res.update_layout(**PLOT_CONFIG, height=300, yaxis_gridcolor="#f0f0f0")
    st.plotly_chart(fig_res, use_container_width=True)
    st.markdown(f'<div class="insight">{t("insight_residual")}</div>', unsafe_allow_html=True)

    # 预测明细表
    with st.expander(t("detail_expander")):
        tbl = pd.DataFrame({
            t("col_actual"):  y_true[:100].astype(int),
            t("col_pred"):    np.round(y_pred[:100]).astype(int),
            t("col_err"):     (y_true[:100] - y_pred[:100]).round(1),
            t("col_err_pct"): (
                np.abs(y_true[:100] - y_pred[:100]) / (y_true[:100] + 1) * 100
            ).round(1),
        })
        st.dataframe(tbl, use_container_width=True)


def page_summary():
    st.markdown(f'<div class="page-title">{t("sum_title")}</div>', unsafe_allow_html=True)

    rows = []
    for name in MODEL_KEYS:
        key = f"result_{name}"
        if key in st.session_state:
            m = st.session_state[key]["metrics"]
            rows.append({
                t("col_model"):      mname(name),
                "RMSE":              round(m["RMSE"], 2),
                "MAE":               round(m["MAE"], 2),
                "R²":                round(m["R²"], 4),
                t("col_train_time"): m["训练时长(s)"],
            })

    if not rows:
        st.warning(t("sum_no_model"))
        st.info(t("sum_hint"))
        return

    df_sum    = pd.DataFrame(rows)
    col_model = t("col_model")
    col_time  = t("col_train_time")
    best_r2   = df_sum.loc[df_sum["R²"].idxmax(),   col_model]
    best_rmse = df_sum.loc[df_sum["RMSE"].idxmin(), col_model]
    n_done    = len(rows)

    st.markdown(
        f'<div class="insight">{t("sum_banner", n=n_done, total=len(MODEL_KEYS), best_r2=best_r2, best_rmse=best_rmse)}</div>',
        unsafe_allow_html=True,
    )

    # 对比表
    st.subheader(t("sum_table_title"))
    st.dataframe(
        df_sum.style
        .highlight_max(subset=["R²"], color="#c8e6c9")
        .highlight_min(subset=["RMSE", "MAE", col_time], color="#c8e6c9")
        .format({"R²": "{:.4f}", "RMSE": "{:.2f}", "MAE": "{:.2f}"}),
        use_container_width=True, height=220,
    )

    # Derive colors from original MODEL_KEYS order
    model_key_map = {mname(k): k for k in MODEL_KEYS}
    colors_used = []
    models = df_sum[col_model].tolist()
    for m in models:
        orig_key = model_key_map.get(m, m)
        idx = MODEL_KEYS.index(orig_key) if orig_key in MODEL_KEYS else 0
        colors_used.append(MODEL_COLORS[idx])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("chart_r2_bar"))
        fig_r2 = go.Figure(go.Bar(
            x=models, y=df_sum["R²"],
            marker_color=colors_used,
            text=[f"{v:.4f}" for v in df_sum["R²"]],
            textposition="outside",
        ))
        fig_r2.add_hline(
            y=0.9, line_dash="dot", line_color="#4CAF50",
            annotation_text=t("excellent_threshold"),
            annotation_position="top right",
        )
        fig_r2.update_layout(
            **PLOT_CONFIG, height=340,
            yaxis_range=[0, 1.08], yaxis_gridcolor="#f0f0f0", yaxis_title="R²",
        )
        st.plotly_chart(fig_r2, use_container_width=True)

    with col2:
        st.subheader(t("chart_rmse_bar"))
        fig_rmse = go.Figure(go.Bar(
            x=models, y=df_sum["RMSE"],
            marker_color=colors_used,
            text=[f"{v:.1f}" for v in df_sum["RMSE"]],
            textposition="outside",
        ))
        fig_rmse.update_layout(
            **PLOT_CONFIG, height=340,
            yaxis_gridcolor="#f0f0f0", yaxis_title="RMSE",
        )
        st.plotly_chart(fig_rmse, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader(t("chart_time_bar"))
        fig_t = go.Figure(go.Bar(
            x=models, y=df_sum[col_time],
            marker_color=colors_used,
            text=[f"{v}s" for v in df_sum[col_time]],
            textposition="outside",
        ))
        fig_t.update_layout(
            **PLOT_CONFIG, height=320,
            yaxis_gridcolor="#f0f0f0", yaxis_title=t("yaxis_time"),
        )
        st.plotly_chart(fig_t, use_container_width=True)

    with col4:
        st.subheader(t("chart_radar"))
        if len(rows) >= 2:
            r2_n   = df_sum["R²"]
            rmse_n = 1 - (df_sum["RMSE"] - df_sum["RMSE"].min()) / (df_sum["RMSE"].max() - df_sum["RMSE"].min() + 1e-9)
            mae_n  = 1 - (df_sum["MAE"]  - df_sum["MAE"].min())  / (df_sum["MAE"].max()  - df_sum["MAE"].min()  + 1e-9)
            spd_n  = 1 - (df_sum[col_time] - df_sum[col_time].min()) / (df_sum[col_time].max() - df_sum[col_time].min() + 1e-9)
            cats   = [t("radar_r2"), t("radar_rmse"), t("radar_mae"), t("radar_spd")]
            fig_rad = go.Figure()
            for i, row in df_sum.iterrows():
                vals = [r2_n[i], rmse_n[i], mae_n[i], spd_n[i]]
                vals += [vals[0]]
                fig_rad.add_trace(go.Scatterpolar(
                    r=vals, theta=cats + [cats[0]],
                    fill="toself", name=row[col_model],
                    line_color=colors_used[list(df_sum.index).index(i)],
                    opacity=0.65,
                ))
            fig_rad.update_layout(
                height=320,
                polar=dict(radialaxis=dict(range=[0, 1], showticklabels=False)),
                showlegend=True, legend=dict(x=1.05, y=0.5),
            )
            st.plotly_chart(fig_rad, use_container_width=True)
        else:
            st.info(t("radar_hint"))

    st.divider()

    # 综合分析
    st.subheader(t("sum_analysis_title"))
    comment = SUMMARY_COMMENT_EN if st.session_state.lang == "en" else SUMMARY_COMMENT_ZH
    st.markdown(f'<div class="summary-comment">{comment}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 主入口 / Main Entry
# ══════════════════════════════════════════════════════════
def main():
    if "nav_idx" not in st.session_state:
        st.session_state.nav_idx = 0
    if "model_idx" not in st.session_state:
        st.session_state.model_idx = 0

    with st.sidebar:
        # ── 语言切换 / Language Toggle ──
        lang_col1, lang_col2 = st.columns(2)
        with lang_col1:
            zh_style = "background:#1565c0;color:white;" if st.session_state.lang == "zh" else "background:rgba(255,255,255,0.15);color:#cce;"
            if st.button("🇨🇳 中文", use_container_width=True, key="btn_zh"):
                st.session_state.lang = "zh"
                st.rerun()
        with lang_col2:
            en_style = "background:#1565c0;color:white;" if st.session_state.lang == "en" else "background:rgba(255,255,255,0.15);color:#cce;"
            if st.button("🇬🇧 English", use_container_width=True, key="btn_en"):
                st.session_state.lang = "en"
                st.rerun()

        st.markdown("---")
        st.markdown(f"## {t('app_title')}")
        st.markdown(
            f"<span style='font-size:0.8rem;color:#90caf9;'>{t('app_subtitle')}</span>",
            unsafe_allow_html=True,
        )
        st.divider()

        nav_options = [t("nav_dashboard"), t("nav_ml"), t("nav_summary")]
        nav = st.radio(
            "nav",
            nav_options,
            index=st.session_state.nav_idx,
            label_visibility="collapsed",
        )
        st.session_state.nav_idx = nav_options.index(nav)

        model_choice = None
        if st.session_state.nav_idx == 1:
            st.markdown(
                f"<span style='font-size:0.85rem;color:#bbdefb;'>{t('choose_algo')}</span>",
                unsafe_allow_html=True,
            )
            model_display_names = [mname(k) for k in MODEL_KEYS]
            model_sel = st.radio(
                "model",
                model_display_names,
                index=st.session_state.model_idx,
                label_visibility="collapsed",
            )
            st.session_state.model_idx = model_display_names.index(model_sel)
            model_choice = MODEL_KEYS[st.session_state.model_idx]

        st.divider()
        st.markdown(
            f"<span style='font-size:0.78rem;color:#90caf9;'>{t('dataset_info')}</span>",
            unsafe_allow_html=True,
        )

        done = [n for n in MODEL_KEYS if f"result_{n}" in st.session_state]
        if done:
            st.divider()
            st.markdown(
                f"<span style='font-size:0.82rem;color:#a5d6a7;'>{t('done_label')}</span>",
                unsafe_allow_html=True,
            )
            for n in done:
                r2 = st.session_state[f"result_{n}"]["metrics"]["R²"]
                st.markdown(
                    f"<span style='font-size:0.8rem;color:#c8e6c9;'>  {mname(n)} — R²={r2:.3f}</span>",
                    unsafe_allow_html=True,
                )

    # 路由
    idx = st.session_state.nav_idx
    if idx == 0:
        page_dashboard()
    elif idx == 1 and model_choice:
        page_model(model_choice)
    elif idx == 2:
        page_summary()


if __name__ == "__main__":
    main()
