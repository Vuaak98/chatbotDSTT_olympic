# Use an official Python runtime as a parent image
FROM python:3.10-slim
# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Thêm dòng này ngay sau USER app
ENV PATH="/home/app/.local/bin:${PATH}"

# Copy the requirements file into the container at /app
COPY --chown=app:app ./requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code into the container at /app
COPY --chown=app:app ./app /app

# Create upload directory (will be overridden by UPLOAD_DIR from .env)
RUN mkdir -p /tmp/ai-math-chatbot-uploads && chown -R app:app /tmp/ai-math-chatbot-uploads

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run main.py when the container launches
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]