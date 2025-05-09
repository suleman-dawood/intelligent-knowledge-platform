FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create non-root user for security
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose the API port
EXPOSE 8000

# Run the coordinator
CMD ["python", "-m", "coordinator.main"] 