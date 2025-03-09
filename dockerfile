# Sử dụng image Python chính thức
FROM python:3.9

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Expose cổng 5000
EXPOSE 5000

# Chạy ứng dụng
CMD ["python", "app.py"]