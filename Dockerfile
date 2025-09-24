# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy your app code
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port Fly expects
EXPOSE 8080

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "jokes_app.main:app", "--host", "0.0.0.0", "--port", "8080"]
