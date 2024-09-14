# Stage 1: Builder
FROM python:3.11-alpine AS builder

# Install build dependencies and required libraries


# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies into a virtual environment
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Final minimal image
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Expose port 8000 for Django
EXPOSE 8000

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

# Start the Django development server
CMD ["python", "manage.py", "runserver"]
