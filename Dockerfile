# Use an official TensorFlow image aligned with local development
FROM tensorflow/tensorflow:2.20.0

ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# TensorFlow base image ships an older distutils-installed blinker.
# Install a wheel version first without uninstalling the system package.
RUN pip install --no-cache-dir --ignore-installed blinker==1.9.0 && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 7860

# Run the Gunicorn web server
# Use Render's dynamic PORT when available, with a local/HF fallback.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-7860} --timeout 120 app:app"]