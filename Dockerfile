FROM python:3.9-slim

# อัปเดต apt-get และติดตั้ง dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y build-essential libpq-dev

# ตั้ง working directory
WORKDIR /app

# คัดลอกไฟล์ requirements.txt
COPY requirements.txt .

# ติดตั้ง dependencies ทีละตัว
RUN pip install --no-cache-dir fastapi
RUN pip install --no-cache-dir uvicorn[gunicorn]
RUN pip install --no-cache-dir SQLAlchemy
RUN pip install --no-cache-dir pandas
RUN pip install --no-cache-dir pandas
RUN pip install --no-cache-dir mysql-connector
RUN pip install --no-cache-dir dotenv
RUN pip install --no-cache-dir openpyxl
RUN pip install --no-cache-dir bs4

# คัดลอกโค้ดทั้งหมด
COPY . .

# เปิด port ที่ FastAPI ใช้งาน
EXPOSE 8000

# รันแอป FastAPI
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]



