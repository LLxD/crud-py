# Use an official Python runtime as the base image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required packages from requirements.txt
RUN pip install -r requirements.txt

# Expose port 5000 for Flask
EXPOSE 4000

# Run the command to start the Flask server
CMD ["python3", "app.py"]
