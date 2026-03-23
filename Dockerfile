FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（编译 scikit-learn / xgboost 等可能需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 先复制 requirements 以利用 Docker layer 缓存
COPY requirements.txt .

# 安装 Python 依赖（国内可替换镜像源加速）
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

# 复制数据文件
COPY Demo/hour.csv /app/data/hour.csv

# 暴露端口
EXPOSE 8200

# Streamlit 配置：禁用遥测，关闭自动开浏览器
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    PYTHONUNBUFFERED=1

# 启动命令
CMD ["streamlit", "run", "app.py", \
     "--server.port=8200", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
