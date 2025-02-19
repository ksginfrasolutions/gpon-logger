ARG ARCH=amd64

FROM --platform=linux/${ARCH} python:3.9-slim-buster as base

WORKDIR /app

# Copy the Python script and requirements file
COPY logger.py .
COPY requirements.txt .

# Install dependencies (if any; remove if your script doesn't need any)
RUN pip install --no-cache-dir -r requirements.txt

# Create log directory and file with correct permissions
RUN mkdir -p /var/log && touch /var/log/all_logs.log && chmod 666 /var/log/all_logs.log

# Set environment variables (if needed)
# ENV VAR1=value1 VAR2=value2

# Command to run the script
CMD ["python", "logger.py"]

# Expose ports
EXPOSE 514/udp
EXPOSE 514/tcp