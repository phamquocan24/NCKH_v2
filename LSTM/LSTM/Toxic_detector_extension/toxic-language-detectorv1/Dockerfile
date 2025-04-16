# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run convert script
RUN python convert_model.py

# Expose port
EXPOSE 7860

# Run app
CMD ["python", "app.py"]

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7680"]