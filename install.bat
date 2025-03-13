@echo off
echo Đang thiết lập môi trường ảo...
python -m venv venv
call venv\Scripts\activate

echo Cài đặt các gói phụ thuộc...
pip install -r requirements.txt

echo Chạy ứng dụng Flask...
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

pause
