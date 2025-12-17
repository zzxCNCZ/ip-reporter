FROM python:3.12-slim

LABEL maintainer="Banksy"
LABEL description="IP Reporter"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# 设置 uv 使用国内镜像源（清华镜像）
ENV UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 增加超时时间（NVIDIA CUDA 包很大，需要更长时间）
ENV UV_HTTP_TIMEOUT=300

# Copy requirements first to leverage cache
COPY requirements.txt ./
# Install dependencies
RUN uv pip install --system -r requirements.txt

# Copy project files
COPY server ./server
COPY client ./client
#COPY .env ./.env

# Expose port
EXPOSE 8000

# Health check (updated to use correct endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Start command (updated to use correct module path)
CMD ["uv", "run", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
