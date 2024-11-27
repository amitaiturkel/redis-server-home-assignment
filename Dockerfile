## this is a dockerfile templete

# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that your app will run on (adjust if necessary)
EXPOSE 8000

# Define the command to run your app (adjust to your needs)
CMD ["python", "app.py"] 
