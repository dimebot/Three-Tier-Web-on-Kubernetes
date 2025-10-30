# Use official Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose the port Gunicorn will run on
EXPOSE 5000

# Create logs directory
RUN mkdir -p logs

# Run the app with Gunicorn
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]
