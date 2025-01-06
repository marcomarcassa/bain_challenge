# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install supervisord
RUN apt-get update && apt-get install -y supervisor

# Copy the supervisord.conf file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose the ports the app and dashboard run on
EXPOSE 8000
EXPOSE 8501

# Command to run supervisord
CMD ["supervisord"]