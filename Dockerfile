# Gunakan image Python sebagai dasar
FROM python:3.9

# Set direktori kerja di dalam container
WORKDIR /app

# Copy semua file ke dalam container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 untuk Cloud Run
EXPOSE 8080

# Set environment variable untuk Flask
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Jalankan aplikasi Flask
CMD ["python", "app.py"]
