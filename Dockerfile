# Use an official TensorFlow CPU image with Python 3.9 as the base
FROM tensorflow/tensorflow:2.10.0-cpu-python3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's code into the container
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 7860

# Run the Gunicorn web server
# We use --bind 0.0.0.0 to make it accessible from outside the container
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "120", "app:app"]