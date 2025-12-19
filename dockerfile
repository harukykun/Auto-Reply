# Sử dụng Python 3.10 bản nhẹ
FROM python:3.10-slim

# Cập nhật và cài đặt thư viện hệ thống (quan trọng: sqlite3)
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào
COPY . .

# Lệnh chạy bot
CMD ["python", "main.py"]