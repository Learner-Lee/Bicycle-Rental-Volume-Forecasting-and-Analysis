# -*- coding: utf-8 -*-
"""
自行车租赁数据挖掘平台
数据来源：UCI Bike Sharing Dataset (hour.csv)
"""

import warnings
warnings.filterwarnings('ignore')

import logging
logging.getLogger("prophet").setLevel(logging.WARNING)
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

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
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# ──────────────────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🚲 自行车租赁 · 数据挖掘平台",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────
# 全局样式
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* 侧边栏 */
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

/* 隐藏 Streamlit 顶部工具栏，避免遮挡页面标题 */
[data-testid="stHeader"] { display: none; }
header[data-testid="stHeader"] { display: none; }

/* 主体 */
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.main { background: #f5f7fa; }

/* KPI卡片 */
.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 22px 20px 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    text-align: center;
    border-top: 5px solid #2196F3;
    margin-bottom: 8px;
}
.kpi-value { font-size: 2.1rem; font-weight: 800; color: #1a237e; line-height: 1.1; }
.kpi-label { font-size: 0.85rem; color: #6b7280; margin-top: 6px; }

/* 洞察文字框 */
.insight {
    background: #e8f4fd;
    border-left: 5px solid #1976d2;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px;
    margin: 8px 0 16px;
    font-size: 0.9rem;
    line-height: 1.7;
    color: #1a237e;
}

/* 算法描述框 */
.algo-desc {
    background: #fafafa;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 18px 22px;
    line-height: 1.8;
    font-size: 0.92rem;
    margin-bottom: 18px;
}

/* 页面大标题 */
.page-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #1a237e;
    margin-bottom: 1.4rem;
    padding-bottom: 0.5rem;
    border-bottom: 3px solid #1976d2;
}

/* 总结评论框 */
.summary-comment {
    background: #fff8e1;
    border: 1px solid #ffd54f;
    border-radius: 12px;
    padding: 20px 24px;
    line-height: 1.9;
    font-size: 0.92rem;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
# 常量
# ──────────────────────────────────────────────────────────
SEASON_MAP   = {1: "春季", 2: "夏季", 3: "秋季", 4: "冬季"}
WEATHER_MAP  = {1: "晴天/少云", 2: "雾天/多云", 3: "小雨/小雪", 4: "大雨/大雪"}
MODEL_NAMES  = ["线性回归", "岭回归", "随机森林", "梯度提升", "XGBoost", "Holt-Winters"]
MODEL_COLORS = ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#F44336", "#607D8B"]
PLOT_CONFIG  = dict(plot_bgcolor="white", paper_bgcolor="white")

# ──────────────────────────────────────────────────────────
# 数据加载 & 预处理（缓存）
# ──────────────────────────────────────────────────────────
@st.cache_data
def load_raw() -> pd.DataFrame:
    df = pd.read_csv("/app/data/hour.csv")
    df["dteday"]        = pd.to_datetime(df["dteday"])
    df["season_label"]  = df["season"].map(SEASON_MAP)
    df["weather_label"] = df["weathersit"].map(WEATHER_MAP)
    return df


@st.cache_data
def prepare_ml_data():
    """特征工程 + 时间序列切分，返回训练/测试集"""
    df = load_raw().copy()

    # 周末标记
    df["is_weekend"] = df["weekday"].isin([0, 6]).astype(int)

    # 周期编码（时间特征循环连续化）
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
        prefix=["season", "weathersit"],
        drop_first=False,
    )
    X = pd.concat([df[base_feats], cat_enc], axis=1).astype(float)
    y = df["cnt"].astype(float)

    # 时间序切分（防泄漏）：最后30天测试，往前60天验证，其余训练
    t_max    = df["dteday"].max()
    cut_test = t_max - pd.Timedelta(days=29)
    cut_val  = cut_test - pd.Timedelta(days=60)

    tr_mask = df["dteday"] < cut_val
    te_mask = df["dteday"] >= cut_test

    return (
        X[tr_mask], y[tr_mask],
        X[te_mask], y[te_mask],
        df.loc[te_mask, "dteday"].values,
    )


# ──────────────────────────────────────────────────────────
# 指标计算
# ──────────────────────────────────────────────────────────
def calc_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE":  float(mean_absolute_error(y_true, y_pred)),
        "R²":   float(r2_score(y_true, y_pred)),
    }


# ──────────────────────────────────────────────────────────
# 模型训练
# ──────────────────────────────────────────────────────────
def train_holt_winters(df):
    """
    Prophet — Holt-Winters 的多重季节性现代升级版。
    传统 HW 只能建模单一季节周期（如24h），无法同时捕捉日内+周内+年度规律，
    导致工作日/休息日预测偏差严重。Prophet 解决了这一根本缺陷。

    同时建模：
      - 日内季节性（Fourier=8，精细捕捉早晚通勤双峰）
      - 周内季节性（工作日 vs 周末模式差异）
      - 年度季节性（春夏秋冬租赁量变化）
      - 假日效应（利用数据集 holiday 列）
      - 乘法模式（季节振幅随整体增长等比例放大）
    """
    from prophet import Prophet

    t0 = time.time()

    # ── 1. 构造小时级 datetime 时序 ─────────────────────────
    ts = df.sort_values(["dteday", "hr"]).copy()
    ts["ds"] = ts["dteday"] + pd.to_timedelta(ts["hr"], unit="h")
    ts["y"]  = ts["cnt"].astype(float)
    full_df  = ts[["ds", "y"]].reset_index(drop=True)

    # ── 2. 假日列表（利用数据集中已有的 holiday 标记） ────────
    hol_days = ts.loc[ts["holiday"] == 1, "dteday"].dt.floor("D").drop_duplicates()
    holidays_df = (
        pd.DataFrame({
            "holiday":      "public_holiday",
            "ds":           hol_days.values,
            "lower_window": 0,
            "upper_window": 1,
        })
        if len(hol_days) > 0 else None
    )

    # ── 3. 时间序切分（最后30天=720小时，与其他模型一致） ─────
    test_size = 30 * 24
    train_df  = full_df.iloc[:-test_size]
    test_df   = full_df.iloc[-test_size:]

    # ── 4. Prophet 模型配置 ──────────────────────────────────
    m = Prophet(
        # 乘法季节性：峰值振幅随用户增长等比例放大（更符合本数据趋势）
        seasonality_mode="multiplicative",
        # 趋势弯折点灵活度（0.05 = 适中，避免过拟合趋势突变）
        changepoint_prior_scale=0.05,
        # 季节性强度先验（10 = 充分学习季节模式）
        seasonality_prior_scale=10.0,
        holidays_prior_scale=10.0,
        holidays=holidays_df,
        # 手动控制日内季节 Fourier 阶数，关闭自动（默认 order=4 不够精细）
        daily_seasonality=False,
        weekly_seasonality=True,   # 自动建模 7 天周期
        yearly_seasonality=True,   # 自动建模 365 天周期（2年数据足够）
    )
    # 手动添加日内季节性：Fourier order=8（16个参数），精细捕捉早晚双峰
    m.add_seasonality("daily", period=1, fourier_order=8)

    m.fit(train_df)

    # ── 5. 测试集预测 ────────────────────────────────────────
    test_fc = m.predict(test_df[["ds"]])
    y_pred  = np.maximum(test_fc["yhat"].values, 0)
    y_test  = test_df["y"].values

    elapsed = round(time.time() - t0, 2)
    metrics = calc_metrics(y_test, y_pred)
    metrics["训练时长(s)"] = elapsed

    # ── 6. 全序列预测（趋势分解可视化） ─────────────────────
    full_fc = m.predict(full_df[["ds"]])

    # ── 7. 日内/周内季节性曲线（高分辨率，用于教学可视化） ──
    vis_daily  = pd.DataFrame({"ds": pd.date_range("2012-06-11", periods=24 * 4, freq="15min")})
    vis_weekly = pd.DataFrame({"ds": pd.date_range("2012-06-11", periods=7 * 24, freq="h")})
    daily_fc   = m.predict(vis_daily)
    weekly_fc  = m.predict(vis_weekly)

    return {
        "metrics":            metrics,
        "y_pred":             y_pred,
        "y_test":             y_test,
        "feature_importance": None,      # 时序模型不使用外部特征
        # Prophet 专属可视化字段
        "full_ds":            full_df["ds"].values,
        "full_y":             full_df["y"].values,
        "full_trend":         full_fc["trend"].values,
        "test_ds":            test_fc["ds"].values,
        "test_yhat_lower":    np.maximum(test_fc["yhat_lower"].values, 0),
        "test_yhat_upper":    test_fc["yhat_upper"].values,
        "daily_pattern":      daily_fc[["ds", "daily"]].copy(),
        "weekly_pattern":     weekly_fc[["ds", "weekly"]].copy(),
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
        m = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        )
        m.fit(X_tr, y_tr)
        y_pred = m.predict(X_te)
        fi = pd.Series(m.feature_importances_, index=X_tr.columns)

    elif name == "梯度提升":
        m = GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.1, max_depth=5, random_state=42
        )
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

    elapsed  = round(time.time() - t0, 2)
    metrics  = calc_metrics(y_te.values, y_pred)
    metrics["训练时长(s)"] = elapsed
    fi_top10 = fi.sort_values(ascending=False).head(10)

    return {
        "metrics":           metrics,
        "y_pred":            y_pred,
        "y_test":            y_te.values,
        "feature_importance": fi_top10,
    }


# ══════════════════════════════════════════════════════════
# 页面渲染函数
# ══════════════════════════════════════════════════════════

# ─────────────── Dashboard ────────────────────────────────
def page_dashboard():
    df = load_raw()
    st.markdown('<div class="page-title">📊 数据总览 — Dashboard</div>', unsafe_allow_html=True)

    # ── KPI 卡片 ──────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    kpi_data = [
        ("#2196F3", "#1a237e", f"{len(df):,}",           "数据总条数（条）"),
        ("#4CAF50", "#1b5e20", f"{int(df['cnt'].sum()):,}","总租赁次数（次）"),
        ("#FF9800", "#e65100", f"{int(df['cnt'].mean())}","小时均租赁量（次/时）"),
        ("#9C27B0", "#4a148c", f"{int(df['cnt'].max())}","单时最高租赁量（次）"),
    ]
    for col, (border, val_color, val, label) in zip([c1, c2, c3, c4], kpi_data):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-top-color:{border}">
              <div class="kpi-value" style="color:{val_color}">{val}</div>
              <div class="kpi-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 1. 每日租赁量趋势 ────────────────────────────────
    st.subheader("📈 每日总租赁量趋势（2011–2012）")
    daily = df.groupby("dteday")["cnt"].sum().reset_index()
    fig1 = px.area(
        daily, x="dteday", y="cnt",
        labels={"dteday": "日期", "cnt": "日租赁总量"},
        color_discrete_sequence=["#2196F3"],
    )
    fig1.update_traces(line_width=1.5, fillcolor="rgba(33,150,243,0.15)")
    fig1.update_layout(**PLOT_CONFIG, height=300, hovermode="x unified",
                       xaxis_title="", yaxis_gridcolor="#f0f0f0", xaxis_showgrid=False)
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("""
    <div class="insight">
    📌 <b>趋势洞察：</b>租赁量整体呈上升趋势，2012年明显高于2011年，说明共享单车平台处于高速增长期。
    每年呈现明显的<b>季节性波动</b>：夏秋（6–9月）租赁量达到峰值，冬季（12–2月）显著下降，
    与气温变化高度吻合。
    </div>""", unsafe_allow_html=True)

    st.divider()

    # ── 2. 小时分布 & 季节分布 ─────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🕐 各小时平均租赁量")
        hourly = df.groupby("hr")["cnt"].mean().reset_index()
        fig2 = px.bar(
            hourly, x="hr", y="cnt",
            labels={"hr": "小时", "cnt": "平均租赁量"},
            color="cnt", color_continuous_scale="Blues",
        )
        fig2.update_layout(**PLOT_CONFIG, height=300, showlegend=False,
                            coloraxis_showscale=False, yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""
        <div class="insight">
        📌 <b>双峰通勤规律：</b>早高峰（8点）和晚高峰（17–18点）租赁量最高，
        体现了典型的上下班出行需求。凌晨（1–5点）几乎无人使用。
        </div>""", unsafe_allow_html=True)

    with col_b:
        st.subheader("🌡️ 各季节租赁量分布")
        fig3 = px.box(
            df, x="season_label", y="cnt",
            labels={"season_label": "季节", "cnt": "租赁量"},
            category_orders={"season_label": ["春季", "夏季", "秋季", "冬季"]},
            color="season_label",
            color_discrete_sequence=["#66BB6A", "#FFA726", "#EF5350", "#42A5F5"],
        )
        fig3.update_layout(**PLOT_CONFIG, height=300, showlegend=False,
                            yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("""
        <div class="insight">
        📌 <b>季节效应：</b>秋季租赁中位数最高，夏季其次。
        春季偏低（天气不稳定），冬季最低（严寒限制出行）。
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── 3. 天气影响 & 工作日 vs 休息日 ────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("☁️ 天气状况对租赁量的影响")
        weather_avg = (
            df.groupby("weather_label")["cnt"]
            .mean()
            .reset_index()
            .sort_values("cnt", ascending=False)
        )
        fig4 = px.bar(
            weather_avg, x="weather_label", y="cnt",
            labels={"weather_label": "天气", "cnt": "平均租赁量"},
            color="cnt", color_continuous_scale="RdYlGn",
        )
        fig4.update_layout(**PLOT_CONFIG, height=300, showlegend=False,
                            coloraxis_showscale=False, yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("""
        <div class="insight">
        📌 <b>天气决定性影响：</b>晴天租赁量约是大雨/大雪天气的 <b>10倍</b>。
        天气是用户出行决策最直接的外部影响因素，在预测模型中权重极高。
        </div>""", unsafe_allow_html=True)

    with col_d:
        st.subheader("📅 工作日 vs 休息日（按小时）")
        hwd = df.groupby(["hr", "workingday"])["cnt"].mean().reset_index()
        hwd["day_type"] = hwd["workingday"].map({0: "🏖 休息日", 1: "💼 工作日"})
        fig5 = px.line(
            hwd, x="hr", y="cnt", color="day_type",
            labels={"hr": "小时", "cnt": "平均租赁量", "day_type": ""},
            color_discrete_sequence=["#FF7043", "#1E88E5"],
        )
        fig5.update_layout(**PLOT_CONFIG, height=300, hovermode="x unified",
                            yaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("""
        <div class="insight">
        📌 <b>出行模式差异：</b>工作日呈 <b>双峰曲线</b>（通勤主导），
        休息日为 <b>单峰平缓曲线</b>（10–15点，休闲主导）。两类用户行为模式截然不同。
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── 4. 相关性热图 ────────────────────────────────────
    st.subheader("🔍 数值特征相关性热图")
    num_cols = ["temp", "atemp", "hum", "windspeed", "casual", "registered", "cnt"]
    corr_vals = df[num_cols].corr().values

    fig6 = go.Figure(go.Heatmap(
        z=corr_vals,
        x=num_cols, y=num_cols,
        colorscale="RdBu", zmid=0,
        text=np.round(corr_vals, 2),
        texttemplate="%{text}",
        textfont={"size": 11},
        hoverongaps=False,
    ))
    fig6.update_layout(**PLOT_CONFIG, height=400)
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown("""
    <div class="insight">
    📌 <b>相关性解读：</b>
    温度（temp/atemp）与租赁量呈<b>正相关</b>（r ≈ 0.40），暖和天气鼓励出行；
    湿度（hum）和风速（windspeed）与租赁量呈<b>负相关</b>，不适宜骑车的天气会抑制需求。
    注册用户（registered）贡献了约 <b>80%</b> 的总租赁量，是平台的核心用户群体。
    </div>""", unsafe_allow_html=True)

    # ── 5. 原始数据预览 ──────────────────────────────────
    with st.expander("📋 原始数据预览（前100行）"):
        st.dataframe(df.head(100), use_container_width=True)


# ─────────────── 机器学习模型 ──────────────────────────────
MODEL_INFO = {
    "线性回归": {
        "icon": "📈",
        "complexity": "⭐",
        "class_name": "LinearRegression",
        "params_str": "fit_intercept=True",
        "desc": """
**线性回归（Linear Regression）** 是机器学习中最基础的监督学习算法，也是理解其他复杂模型的基石。

**核心思想：** 寻找一组权重 *w*，使得 $\\hat{y} = w_0 + w_1x_1 + w_2x_2 + \\cdots + w_nx_n$ 与真实值 *y* 的误差最小（最小二乘法）。

**优点：**
- ✅ 概念简单，结果可直接解释（系数 = 特征对租赁量的影响大小）
- ✅ 训练速度极快（毫秒级）
- ✅ 适合作为基准模型（Baseline），衡量其他算法的提升幅度

**缺点：**
- ❌ 假设特征与目标之间是线性关系，无法捕捉非线性模式（如"气温超过30°C后不再增加租赁"）
- ❌ 对异常值（如某天异常的超高/超低租赁量）敏感
""",
    },
    "岭回归": {
        "icon": "📉",
        "complexity": "⭐⭐",
        "class_name": "Ridge",
        "params_str": "alpha=1.0",
        "desc": """
**岭回归（Ridge Regression）** 是线性回归加上 **L2 正则化** 的改进版本，通过在损失函数中加入权重平方和惩罚项来解决过拟合。

**数学表达：** 最小化 $||y - Xw||^2 + \\alpha ||w||^2$，其中 $\\alpha$ 控制正则化强度。

**优点：**
- ✅ 有效解决**多重共线性**问题（本数据集中 temp 和 atemp 高度相关，岭回归更稳定）
- ✅ 防止过拟合，泛化能力优于普通线性回归
- ✅ 仍然保持线性模型的可解释性

**缺点：**
- ❌ 仍然是线性模型，无法建模非线性关系
- ❌ 需要调整超参数 α（本示例使用默认值 1.0）
""",
    },
    "随机森林": {
        "icon": "🌲",
        "complexity": "⭐⭐⭐",
        "class_name": "RandomForestRegressor",
        "params_str": "n_estimators=100, max_depth=10, random_state=42",
        "desc": """
**随机森林（Random Forest）** 是一种**集成学习**算法，通过构建多棵决策树并对预测结果取平均来提升精度（Bagging 思想）。

**核心思想：** "三个臭皮匠，顶个诸葛亮" — 许多弱学习器（浅决策树）的集成，比单个强学习器更稳健。

每棵树在训练时随机选取样本（Bootstrap）和特征子集，使得各树相互独立、预测误差被平均抵消。

**优点：**
- ✅ 天然处理**非线性关系**，无需特征缩放
- ✅ 对异常值和噪声鲁棒
- ✅ 内置**特征重要性**评估，方便分析哪些因素最关键
- ✅ 可并行训练（`n_jobs=-1`），速度较快

**缺点：**
- ❌ 模型体积较大（100棵树），预测略慢
- ❌ 可解释性不如线性模型（黑盒程度较高）
""",
    },
    "梯度提升": {
        "icon": "🚀",
        "complexity": "⭐⭐⭐⭐",
        "class_name": "GradientBoostingRegressor",
        "params_str": "n_estimators=200, learning_rate=0.1, max_depth=5",
        "desc": """
**梯度提升（Gradient Boosting）** 是另一种强大的集成方法，与随机森林**并行**建树不同，
它以**串行**方式逐步构建树：每棵新树专注于修正前一棵树的**残差**（预测误差）。

**核心思想：** 沿梯度下降方向不断减小残差，每一步让模型"精准补刀"弱点。

类比：就像一组人轮流改稿——第一个人写初稿，第二个人只改第一个人的错误，
第三个人再改第二个人遗漏的错误，最终稿质量远超任何一人单独完成。

**优点：**
- ✅ 通常比随机森林精度更高（Boosting > Bagging）
- ✅ 对混合类型特征处理能力强
- ✅ 内置特征重要性

**缺点：**
- ❌ **串行训练**较慢，无法并行化
- ❌ 超参数较多，更容易过拟合（需要仔细调整 `n_estimators` 和 `learning_rate`）
""",
    },
    "XGBoost": {
        "icon": "⚡",
        "complexity": "⭐⭐⭐⭐⭐",
        "class_name": "XGBRegressor",
        "params_str": "n_estimators=500, learning_rate=0.05, max_depth=6",
        "desc": """
**XGBoost（Extreme Gradient Boosting）** 是梯度提升的**工程优化版**，由陈天奇（Tianqi Chen）于2014年提出，
曾横扫众多机器学习竞赛冠军（Kaggle首选算法）。

**相比传统梯度提升的改进：**
- 🔬 二阶泰勒展开——更精确的梯度近似
- 🛡 内置正则化（L1/L2）——防止过拟合
- 🔀 列采样（colsample_bytree）——进一步防过拟合
- ⚡ 并行化树节点分裂——速度大幅提升
- 🏗 直方图算法（tree_method='hist'）——内存高效
- 🔧 自动处理缺失值

**优点：**
- ✅ 速度快、精度高
- ✅ 综合性能通常是表格数据的天花板
- ✅ 超参数丰富，可精细调优

**缺点：**
- ❌ 超参数众多，调参复杂
- ❌ 可解释性不如线性模型
""",
    },
    "Holt-Winters": {
        "icon": "📅",
        "complexity": "⭐⭐⭐⭐",
        "class_name": "Prophet",
        "params_str": 'seasonality_mode="multiplicative", daily_seasonality=False, weekly_seasonality=True',
        "desc": """
**Holt-Winters → Prophet（多重季节性时间序列模型）**

**为什么要升级？**
传统 Holt-Winters 只能建模**单一季节周期**（如 `period=24`），完全无法区分工作日和周末——
而本数据中两者的租赁曲线截然不同（双峰通勤 vs 单峰休闲），这是导致 HW 效果差的根本原因。

**Prophet** 由 Facebook（Meta）于2017年提出，本质是 Holt-Winters 的现代化泛化：将趋势、
各层级季节性和假日效应统一建模为**广义加法模型（GAM）**，用 L-BFGS 优化所有参数。

**本实现同时捕捉四层规律：**
| 组件 | 描述 | 参数 |
|------|------|------|
| 📈 趋势 | 系统整体增长，自动检测突变点 | `changepoint_prior_scale=0.05` |
| 🕐 日内季节性 | 早晚通勤双峰（手动 Fourier=8） | `period=1 day` |
| 📅 周内季节性 | 工作日 vs 休息日出行模式 | `period=7 days` |
| 🗓 年度季节性 | 春夏秋冬骑行意愿变化 | `period=365 days` |
| 🎌 假日效应 | 利用数据集 `holiday` 列 | `lower/upper_window=0/1` |

**乘法季节性（multiplicative）**：季节振幅随整体增长等比例放大，
符合"系统用户越多，高峰时段峰值也越高"的现实规律。

**优点：**
- ✅ 多重季节性，精度大幅优于传统 HW
- ✅ 输出置信区间（预测不确定性可视化）
- ✅ 可分解展示各季节性分量（可解释性极佳）
- ✅ 自动处理假日，无需手动特征工程

**缺点：**
- ❌ 仍不使用温度/天气等外部特征（纯时序）
- ❌ 训练时间比传统 HW 略长（通常10–30秒）
""",
    },
}


def page_model(name: str):
    info = MODEL_INFO[name]
    st.markdown(
        f'<div class="page-title">{info["icon"]} {name} '
        f'<span style="font-size:1rem;color:#64748b;">复杂度：{info["complexity"]}</span></div>',
        unsafe_allow_html=True,
    )

    # 算法介绍
    with st.expander("📚 算法介绍（点击展开/收起）", expanded=True):
        st.markdown(f'<div class="algo-desc">{info["desc"]}</div>', unsafe_allow_html=True)
        if name == "Holt-Winters":
            st.code(
                "from prophet import Prophet\n\n"
                "m = Prophet(\n"
                '    seasonality_mode="multiplicative",\n'
                "    changepoint_prior_scale=0.05,\n"
                "    weekly_seasonality=True,\n"
                "    yearly_seasonality=True,\n"
                "    holidays=holidays_df,          # 数据集中的假日标记\n"
                ")\n"
                'm.add_seasonality("daily", period=1, fourier_order=8)  # 精细日内曲线\n'
                "m.fit(train_df)                    # ds列=时间戳, y列=租赁量\n"
                "forecast = m.predict(test_df)\n"
                "y_pred = forecast['yhat'].clip(lower=0)",
                language="python",
            )
        else:
            st.code(
                f"from sklearn... import {info['class_name']}\n"
                f"model = {info['class_name']}({info['params_str']})\n"
                f"model.fit(X_train, y_train)\n"
                f"y_pred = model.predict(X_test)",
                language="python",
            )

    # 运行按钮
    key = f"result_{name}"
    btn_col, _ = st.columns([1, 4])
    with btn_col:
        run_clicked = st.button(f"▶ 运行 {name}", type="primary", use_container_width=True)

    if run_clicked:
        with st.spinner(f"⏳ 正在训练 {name}，请稍候..."):
            if name == "Holt-Winters":
                result = train_holt_winters(load_raw())
            else:
                X_tr, y_tr, X_te, y_te, _ = prepare_ml_data()
                result = train_model(name, X_tr, y_tr, X_te, y_te)
            st.session_state[key] = result
        st.success(f"✅ {name} 训练完成！")

    if key not in st.session_state:
        st.info("👆 点击上方「运行」按钮，开始训练模型并查看结果。")
        return

    res     = st.session_state[key]
    metrics = res["metrics"]
    y_pred  = res["y_pred"]
    y_true  = res["y_test"]
    fi      = res.get("feature_importance")   # Holt-Winters 返回 None

    st.divider()

    # ── 指标卡片 ──────────────────────────────────────────
    st.subheader("📊 模型评估指标")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("RMSE（均方根误差）",  f"{metrics['RMSE']:.2f}",  help="越小越好，单位与租赁量相同")
    with m2:
        st.metric("MAE（平均绝对误差）", f"{metrics['MAE']:.2f}",   help="越小越好，直观反映平均误差")
    with m3:
        st.metric("R²（决定系数）",       f"{metrics['R²']:.4f}",    help="越接近1越好；>0.9为优秀")
    with m4:
        st.metric("训练时长",             f"{metrics['训练时长(s)']}s", help="模型拟合所用时间")

    st.divider()

    # ── 可视化：预测对比 + 散点图 ────────────────────────
    col1, col2 = st.columns([3, 2])
    n_show = min(500, len(y_true))

    with col1:
        st.subheader("📉 实际值 vs 预测值（前500个测试点）")
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(
            y=y_true[:n_show], name="实际值",
            line=dict(color="#1E88E5", width=1.5),
        ))
        fig_ts.add_trace(go.Scatter(
            y=y_pred[:n_show], name="预测值",
            line=dict(color="#E53935", width=1.5, dash="dot"),
        ))
        fig_ts.update_layout(
            **PLOT_CONFIG, height=360, hovermode="x unified",
            xaxis_title="样本序号（时间递增）", yaxis_title="租赁量",
            yaxis_gridcolor="#f0f0f0", legend=dict(x=0, y=1),
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    with col2:
        st.subheader("🎯 预测散点图")
        fig_sc = px.scatter(
            x=y_true, y=y_pred,
            labels={"x": "实际值", "y": "预测值"},
            opacity=0.35, color_discrete_sequence=["#7B1FA2"],
        )
        max_v = max(float(y_true.max()), float(y_pred.max())) * 1.05
        fig_sc.add_shape(
            type="line", x0=0, y0=0, x1=max_v, y1=max_v,
            line=dict(color="#E53935", dash="dash", width=1.5),
        )
        fig_sc.add_annotation(
            x=max_v * 0.85, y=max_v * 0.9, text="完美预测线",
            showarrow=False, font=dict(color="#E53935", size=11),
        )
        fig_sc.update_layout(**PLOT_CONFIG, height=360)
        st.plotly_chart(fig_sc, use_container_width=True)

    # ── 特征重要性 ────────────────────────────────────────
    st.subheader("🔑 特征重要性（Top 10）")
    if fi is not None:
        feat_df = fi.reset_index()
        feat_df.columns = ["特征", "重要性"]
        feat_df = feat_df.sort_values("重要性")
        fig_fi = px.bar(
            feat_df, x="重要性", y="特征", orientation="h",
            color="重要性", color_continuous_scale="Blues",
            labels={"重要性": "重要性分数", "特征": "特征名称"},
        )
        fig_fi.update_layout(**PLOT_CONFIG, height=360, showlegend=False,
                              coloraxis_showscale=False, xaxis_gridcolor="#f0f0f0")
        st.plotly_chart(fig_fi, use_container_width=True)
    else:
        st.info("Holt-Winters 是纯时间序列模型，直接对历史序列建模，不使用外部特征，因此无特征重要性。")

    # ── 残差分布 ──────────────────────────────────────────
    st.subheader("📊 残差分布（预测误差直方图）")
    residuals = y_true - y_pred
    fig_res = px.histogram(
        residuals, nbins=60,
        labels={"value": "残差（实际 − 预测）", "count": "频次"},
        color_discrete_sequence=["#43A047"],
    )
    fig_res.add_vline(
        x=0, line_dash="dash", line_color="#E53935",
        annotation_text="零误差", annotation_position="top",
    )
    fig_res.update_layout(**PLOT_CONFIG, height=300, yaxis_gridcolor="#f0f0f0")
    st.plotly_chart(fig_res, use_container_width=True)
    st.markdown("""
    <div class="insight">
    📌 <b>残差解读：</b>理想情况下残差应近似<b>正态分布</b>且以0为中心，说明模型无系统性偏差。
    若残差明显偏斜或出现双峰，则说明模型对某类样本（如高峰时段）存在系统性低估/高估。
    </div>""", unsafe_allow_html=True)

    # ── 预测明细表 ────────────────────────────────────────
    with st.expander("📋 查看预测明细表（前100行）"):
        tbl = pd.DataFrame({
            "实际租赁量":  y_true[:100].astype(int),
            "预测租赁量":  np.round(y_pred[:100]).astype(int),
            "误差":        (y_true[:100] - y_pred[:100]).round(1),
            "绝对误差率(%)": (
                np.abs(y_true[:100] - y_pred[:100])
                / (y_true[:100] + 1) * 100
            ).round(1),
        })
        st.dataframe(tbl, use_container_width=True)

    # ── Prophet 专属分解可视化 ────────────────────────────
    if name == "Holt-Winters" and "full_trend" in res:
        st.divider()
        st.subheader("🔍 Prophet 分解分析 — 各组件独立可视化")

        full_ds    = pd.to_datetime(res["full_ds"])
        full_y     = res["full_y"]
        full_trend = res["full_trend"]
        test_ds    = pd.to_datetime(res["test_ds"])

        # 1. 趋势分量
        st.markdown("**📈 整体趋势（剔除季节性后的系统增长曲线）**")
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=full_ds, y=full_y, name="实际值",
            line=dict(color="#BBDEFB", width=0.8), opacity=0.55,
        ))
        fig_trend.add_trace(go.Scatter(
            x=full_ds, y=full_trend, name="趋势",
            line=dict(color="#1565C0", width=2.5),
        ))
        # 训练/测试分割线
        split_dt = test_ds[0]
        fig_trend.add_vline(
            x=split_dt, line_dash="dash", line_color="#E53935",
            annotation_text="测试集起点", annotation_position="top left",
        )
        fig_trend.update_layout(
            **PLOT_CONFIG, height=300, hovermode="x unified",
            yaxis_gridcolor="#f0f0f0", xaxis_title="", yaxis_title="租赁量",
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown("""
        <div class="insight">
        📌 <b>趋势洞察：</b>Prophet 自动检测趋势突变点（changepoints）。
        可以看到2012年租赁量整体明显高于2011年，增速在年中略有放缓，
        符合共享单车平台从快速扩张转向稳定增长的生命周期规律。
        </div>""", unsafe_allow_html=True)

        st.divider()
        col_d, col_w = st.columns(2)

        with col_d:
            # 2. 日内季节性
            st.markdown("**🕐 日内季节性（典型一天24小时的租赁规律）**")
            dp = res["daily_pattern"].copy()
            dp["hour"] = dp["ds"].dt.hour + dp["ds"].dt.minute / 60
            dp_sorted  = dp.sort_values("hour")
            fig_dp = go.Figure(go.Scatter(
                x=dp_sorted["hour"], y=dp_sorted["daily"],
                mode="lines", line=dict(color="#E53935", width=2.5),
                fill="tozeroy", fillcolor="rgba(229,57,53,0.08)",
            ))
            fig_dp.update_layout(
                **PLOT_CONFIG, height=300,
                xaxis=dict(tickmode="linear", tick0=0, dtick=4,
                           title="小时（0–24）"),
                yaxis=dict(title="季节性乘数", gridcolor="#f0f0f0"),
            )
            st.plotly_chart(fig_dp, use_container_width=True)
            st.markdown("""
            <div class="insight">
            📌 <b>双峰规律：</b>早高峰（~8点）和晚高峰（~17–18点）季节性乘数最高，
            凌晨（1–5点）接近零。Prophet 用8阶 Fourier 级数精细拟合了这条双峰曲线。
            </div>""", unsafe_allow_html=True)

        with col_w:
            # 3. 周内季节性（按天聚合均值）
            st.markdown("**📅 周内季节性（各星期的相对出行强度）**")
            wp = res["weekly_pattern"].copy()
            wp["dow"]   = wp["ds"].dt.dayofweek   # 0=Monday
            day_labels  = ["周一","周二","周三","周四","周五","周六","周日"]
            wp_agg      = wp.groupby("dow")["weekly"].mean().reset_index()
            wp_agg["星期"] = wp_agg["dow"].map(lambda x: day_labels[x])
            colors_week = [
                "#1E88E5","#1E88E5","#1E88E5","#1E88E5","#1E88E5",
                "#E53935","#E53935",
            ]
            fig_wp = go.Figure(go.Bar(
                x=wp_agg["星期"], y=wp_agg["weekly"],
                marker_color=colors_week,
                text=[f"{v:.3f}" for v in wp_agg["weekly"]],
                textposition="outside",
            ))
            fig_wp.update_layout(
                **PLOT_CONFIG, height=300,
                yaxis=dict(title="季节性乘数", gridcolor="#f0f0f0"),
                xaxis_title="",
            )
            st.plotly_chart(fig_wp, use_container_width=True)
            st.markdown("""
            <div class="insight">
            📌 <b>工作日 vs 休息日：</b>蓝色=工作日，红色=周末。
            若工作日乘数 > 周末，说明通勤用户是主力；
            反之则休闲用户更活跃。Prophet 完整捕捉到了这一差异。
            </div>""", unsafe_allow_html=True)

        st.divider()

        # 4. 测试集预测 + 置信区间
        st.markdown("**🎯 测试集预测与 80% 置信区间**")
        fig_ci = go.Figure()
        # 置信带
        fig_ci.add_trace(go.Scatter(
            x=np.concatenate([test_ds, test_ds[::-1]]),
            y=np.concatenate([res["test_yhat_upper"], res["test_yhat_lower"][::-1]]),
            fill="toself", fillcolor="rgba(33,150,243,0.12)",
            line=dict(color="rgba(0,0,0,0)"), name="80% 置信区间", showlegend=True,
        ))
        fig_ci.add_trace(go.Scatter(
            x=test_ds, y=y_true, name="实际值",
            line=dict(color="#1E88E5", width=1.5),
        ))
        fig_ci.add_trace(go.Scatter(
            x=test_ds, y=y_pred, name="预测值",
            line=dict(color="#E53935", width=1.5, dash="dot"),
        ))
        fig_ci.update_layout(
            **PLOT_CONFIG, height=320, hovermode="x unified",
            yaxis_gridcolor="#f0f0f0", xaxis_title="", yaxis_title="租赁量",
        )
        st.plotly_chart(fig_ci, use_container_width=True)
        st.markdown("""
        <div class="insight">
        📌 <b>置信区间：</b>阴影部分表示 80% 预测区间。若实际值大多落在区间内，说明模型不确定性估计合理。
        相较于传统机器学习模型，Prophet 的独特优势在于能输出<b>可量化的预测不确定性</b>，
        这在实际业务决策（如运力调度）中极有价值。
        </div>""", unsafe_allow_html=True)


# ─────────────── 总结页 ────────────────────────────────────
def page_summary():
    st.markdown('<div class="page-title">📋 模型总结报告 — Summary</div>', unsafe_allow_html=True)

    # 收集已运行的模型结果
    rows = []
    for name in MODEL_NAMES:
        key = f"result_{name}"
        if key in st.session_state:
            m = st.session_state[key]["metrics"]
            rows.append({
                "模型":         name,
                "RMSE":         round(m["RMSE"], 2),
                "MAE":          round(m["MAE"], 2),
                "R²":           round(m["R²"], 4),
                "训练时长(s)":  m["训练时长(s)"],
            })

    if not rows:
        st.warning("⚠️ 尚未运行任何模型，请先前往「机器学习」页面运行模型。")
        st.info("建议运行顺序：线性回归 → 岭回归 → 随机森林 → 梯度提升 → XGBoost")
        return

    df_sum = pd.DataFrame(rows)
    best_r2   = df_sum.loc[df_sum["R²"].idxmax(), "模型"]
    best_rmse = df_sum.loc[df_sum["RMSE"].idxmin(), "模型"]
    n_done    = len(rows)

    st.markdown(f"""
    <div class="insight">
    🏆 已完成 <b>{n_done}/{len(MODEL_NAMES)}</b> 个模型训练 &nbsp;|&nbsp;
    最高 R² 模型：<b>{best_r2}</b> &nbsp;|&nbsp;
    最低 RMSE 模型：<b>{best_rmse}</b>
    </div>""", unsafe_allow_html=True)

    # ── 对比表 ───────────────────────────────────────────
    st.subheader("📊 模型性能对比表")
    display_df = df_sum.copy()
    st.dataframe(
        display_df.style
        .highlight_max(subset=["R²"], color="#c8e6c9")
        .highlight_min(subset=["RMSE", "MAE", "训练时长(s)"], color="#c8e6c9")
        .format({"R²": "{:.4f}", "RMSE": "{:.2f}", "MAE": "{:.2f}"}),
        use_container_width=True, height=220,
    )

    colors_used = [MODEL_COLORS[MODEL_NAMES.index(n)] for n in df_sum["模型"]]
    models      = df_sum["模型"].tolist()

    st.divider()

    # ── 可视化对比 ───────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 R² 对比（越高越好）")
        fig_r2 = go.Figure(go.Bar(
            x=models, y=df_sum["R²"],
            marker_color=colors_used,
            text=[f"{v:.4f}" for v in df_sum["R²"]],
            textposition="outside",
        ))
        fig_r2.add_hline(
            y=0.9, line_dash="dot", line_color="#4CAF50",
            annotation_text="优秀阈值 0.90",
            annotation_position="top right",
        )
        fig_r2.update_layout(
            **PLOT_CONFIG, height=340,
            yaxis_range=[0, 1.08], yaxis_gridcolor="#f0f0f0",
            yaxis_title="R²",
        )
        st.plotly_chart(fig_r2, use_container_width=True)

    with col2:
        st.subheader("📉 RMSE 对比（越低越好）")
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
        st.subheader("⏱️ 训练时长对比")
        fig_t = go.Figure(go.Bar(
            x=models, y=df_sum["训练时长(s)"],
            marker_color=colors_used,
            text=[f"{v}s" for v in df_sum["训练时长(s)"]],
            textposition="outside",
        ))
        fig_t.update_layout(
            **PLOT_CONFIG, height=320,
            yaxis_gridcolor="#f0f0f0", yaxis_title="训练时长（秒）",
        )
        st.plotly_chart(fig_t, use_container_width=True)

    with col4:
        st.subheader("🕸️ 综合雷达对比图")
        if len(rows) >= 2:
            r2_n    = df_sum["R²"]
            rmse_n  = 1 - (df_sum["RMSE"] - df_sum["RMSE"].min()) / (df_sum["RMSE"].max() - df_sum["RMSE"].min() + 1e-9)
            mae_n   = 1 - (df_sum["MAE"]  - df_sum["MAE"].min())  / (df_sum["MAE"].max()  - df_sum["MAE"].min()  + 1e-9)
            spd_n   = 1 - (df_sum["训练时长(s)"] - df_sum["训练时长(s)"].min()) / (df_sum["训练时长(s)"].max() - df_sum["训练时长(s)"].min() + 1e-9)
            cats    = ["R²精度", "RMSE(低好)", "MAE(低好)", "训练速度"]
            fig_rad = go.Figure()
            for i, row in df_sum.iterrows():
                vals = [r2_n[i], rmse_n[i], mae_n[i], spd_n[i]]
                vals += [vals[0]]
                fig_rad.add_trace(go.Scatterpolar(
                    r=vals, theta=cats + [cats[0]],
                    fill="toself", name=row["模型"],
                    line_color=colors_used[list(df_sum.index).index(i)],
                    opacity=0.65,
                ))
            fig_rad.update_layout(
                height=320,
                polar=dict(radialaxis=dict(range=[0, 1], showticklabels=False)),
                showlegend=True,
                legend=dict(x=1.05, y=0.5),
            )
            st.plotly_chart(fig_rad, use_container_width=True)
        else:
            st.info("运行 2 个以上模型后显示雷达图。")

    st.divider()

    # ── 文字评论 ─────────────────────────────────────────
    st.subheader("💬 综合分析与学习建议")

    comment = f"""
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
    st.markdown(f'<div class="summary-comment">{comment}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# 主入口：侧边栏 + 路由
# ══════════════════════════════════════════════════════════
def main():
    # 初始化 session state
    if "nav_main" not in st.session_state:
        st.session_state.nav_main  = "📊 Dashboard"
    if "nav_model" not in st.session_state:
        st.session_state.nav_model = MODEL_NAMES[0]

    with st.sidebar:
        st.markdown("## 🚲 数据挖掘平台")
        st.markdown(
            "<span style='font-size:0.8rem;color:#90caf9;'>自行车租赁量预测分析</span>",
            unsafe_allow_html=True,
        )
        st.divider()

        nav = st.radio(
            "主导航",
            ["📊 Dashboard", "🤖 机器学习", "📋 总结报告"],
            label_visibility="collapsed",
        )

        model_choice = None
        if nav == "🤖 机器学习":
            st.markdown(
                "<span style='font-size:0.85rem;color:#bbdefb;'>选择算法：</span>",
                unsafe_allow_html=True,
            )
            model_choice = st.radio(
                "算法选择",
                MODEL_NAMES,
                label_visibility="collapsed",
            )

        st.divider()
        st.markdown(
            "<span style='font-size:0.78rem;color:#90caf9;'>"
            "📦 数据集：UCI Bike Sharing<br>"
            "📊 记录数：17,379 条<br>"
            "📅 时间跨度：2011–2012"
            "</span>",
            unsafe_allow_html=True,
        )

        # 显示已完成模型
        done = [n for n in MODEL_NAMES if f"result_{n}" in st.session_state]
        if done:
            st.divider()
            st.markdown(
                "<span style='font-size:0.82rem;color:#a5d6a7;'>✅ 已完成模型：</span>",
                unsafe_allow_html=True,
            )
            for n in done:
                r2 = st.session_state[f"result_{n}"]["metrics"]["R²"]
                st.markdown(
                    f"<span style='font-size:0.8rem;color:#c8e6c9;'>  {n} — R²={r2:.3f}</span>",
                    unsafe_allow_html=True,
                )

    # 路由
    if nav == "📊 Dashboard":
        page_dashboard()
    elif nav == "🤖 机器学习" and model_choice:
        page_model(model_choice)
    elif nav == "📋 总结报告":
        page_summary()


if __name__ == "__main__":
    main()
