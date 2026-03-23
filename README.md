<div align="center">

# 🚲 自行车租赁数据挖掘平台

**Bike Sharing · Data Mining Platform**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.1-006400?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Port](https://img.shields.io/badge/Port-8200-FFA500?style=for-the-badge)

> 面向中学生的交互式数据挖掘教学平台
> 基于 UCI 自行车共享数据集，一键运行 5 种机器学习算法，实时对比结果

</div>

---

## ✨ 功能亮点

| 模块 | 内容 |
|------|------|
| 📊 **Dashboard** | 6 张可交互图表：时序趋势、小时分布、季节箱图、天气影响、通勤模式、相关性热图，每图配有中文洞察批注 |
| 🤖 **机器学习** | 5 种算法一键运行，实时展示 RMSE / MAE / R² 指标、预测对比折线图、散点图、特征重要性、残差分布 |
| 📋 **总结报告** | 所有模型横向对比表、R²/RMSE 柱状图、综合雷达图、文字分析建议 |

---

## 🖥️ 快速启动

### 前置条件

- [Docker](https://docs.docker.com/get-docker/) ≥ 20.10
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.0

### 一键启动

```bash
# 克隆或进入项目目录
cd /storage/Project/Data_Mining_Group

# 构建镜像并启动（首次约 3–5 分钟）
docker compose up -d --build

# 查看启动状态
docker ps | grep bike_mining_app
```

浏览器打开 **[http://localhost:8200](http://localhost:8200)** 即可访问 🎉

### 常用命令

```bash
# 查看实时日志
docker logs -f bike_mining_app

# 停止服务
docker compose down

# 重启服务（代码更新后需重新 build）
docker compose up -d --build
```

---

## 📖 使用指南

### 第一步：探索数据（Dashboard）

点击左侧导航栏 **📊 Dashboard**，查看数据集全貌：

- **每日趋势图**：了解 2011–2012 年租赁量的整体增长与季节性规律
- **小时分布图**：发现早高峰（8点）和晚高峰（17–18点）的通勤规律
- **天气/季节影响**：量化天气好坏对租赁需求的显著影响
- **相关性热图**：了解温度、湿度、风速与租赁量的相关关系

### 第二步：训练机器学习模型

点击 **🤖 机器学习**，从侧边栏选择算法，点击 **▶ 运行** 按钮：

```
线性回归  →  岭回归  →  随机森林  →  梯度提升  →  XGBoost
  ⭐           ⭐⭐         ⭐⭐⭐        ⭐⭐⭐⭐       ⭐⭐⭐⭐⭐
（从简单到复杂，建议按顺序逐一体验）
```

每个模型运行后将展示：

- 📊 **评估指标**：RMSE（均方根误差）、MAE（平均绝对误差）、R²（决定系数）、训练时长
- 📉 **时序对比图**：实际值 vs 预测值，直观查看拟合效果
- 🎯 **散点图**：越靠近对角线说明预测越准确
- 🔑 **特征重要性 Top 10**：哪些因素最影响租赁量
- 📊 **残差分布**：预测误差是否符合正态分布

### 第三步：查看总结报告

所有模型运行完成后，点击 **📋 总结报告**，查看：

- 全模型对比表（绿色高亮最优值）
- R²、RMSE、训练时长柱状图
- 综合性能雷达图
- 算法选择建议文字报告

---

## 🤖 模型说明

| 算法 | 类型 | 复杂度 | 适合场景 |
|------|------|--------|---------|
| **线性回归** | 线性模型 | ⭐ | 入门学习、建立基准 |
| **岭回归** | 正则化线性 | ⭐⭐ | 特征共线性场景 |
| **随机森林** | 集成 (Bagging) | ⭐⭐⭐ | 重视可解释性、稳定预测 |
| **梯度提升** | 集成 (Boosting) | ⭐⭐⭐⭐ | 追求高精度、数据量充足 |
| **XGBoost** | 集成 (优化Boosting) | ⭐⭐⭐⭐⭐ | 生产环境首选、竞赛级别 |

---

## 📦 数据集

**UCI Bike Sharing Dataset** — 华盛顿特区共享单车系统（2011–2012）

| 属性 | 值 |
|------|----|
| 数据量 | 17,379 条（小时级） |
| 时间跨度 | 2011-01-01 ~ 2012-12-31 |
| 目标变量 | `cnt`（每小时总租赁量） |
| 特征数量 | 14 个原始特征 + 周期编码 + One-Hot |

**主要特征：**

```
时间特征：yr（年份）、mnth（月份）、hr（小时）、weekday（周几）、holiday（假日）
天气特征：temp（温度）、atemp（体感温度）、hum（湿度）、windspeed（风速）、weathersit（天气状况）
分类特征：season（季节，One-Hot编码）
```

**数据切分策略（时间序防泄漏）：**

```
2011-01-01 ─────────────────────────────── 2012-12-31
│<────────── 训练集 ──────────>│<─ 验证集(60天) ─>│<─ 测试集(30天) ─>│
```

---

## 🏗️ 项目结构

```
Data_Mining_Group/
├── 📄 app.py                 # Streamlit 主应用（全部逻辑）
├── 📋 requirements.txt       # Python 依赖（版本锁定）
├── 🐳 Dockerfile             # 容器构建配置
├── 🐳 docker-compose.yml     # 服务编排配置
├── 📖 README.md              # 本文档
└── Demo/
    ├── 📊 hour.csv           # 原始数据集
    ├── 🐍 1.py               # 原始 XGBoost 实验脚本
    ├── models/               # 预训练模型文件
    ├── figs/                 # 生成的图表
    └── reports/              # 预测报告 CSV
```

---

## 🛠️ 技术栈

```
前端/UI      Streamlit 1.41    交互式 Python Web 框架
可视化       Plotly 5.24       交互式图表库
机器学习     scikit-learn 1.5  传统 ML 算法
             XGBoost 2.1       梯度提升框架
数据处理     Pandas 2.2        数据分析
             NumPy 1.26        数值计算
容器化       Docker            环境隔离，一键部署
```

---

## 🔑 关键学习要点

> 通过本平台，你将掌握：

1. **特征工程**：周期编码（sin/cos）让时间特征更合理地表达循环性
2. **时序切分**：正确的训练/测试集划分方式，避免数据泄漏
3. **模型评估**：RMSE、MAE、R² 三个指标的含义与区别
4. **集成学习**：Bagging（随机森林）vs Boosting（梯度提升/XGBoost）的本质差异
5. **No Free Lunch**：没有万能模型，精度 vs 速度 vs 可解释性需要权衡

---

## 📄 数据来源

Fanaee-T, H., & Gama, J. (2014). *Event labeling combining ensemble detectors and background knowledge*. Progress in Artificial Intelligence.

数据集来源：[UCI Machine Learning Repository - Bike Sharing Dataset](https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset)

---

<div align="center">

Made with ❤️ for Data Mining Education

</div>
