# Dockerfile for building the application container.

# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app
ENV PYTHONPATH=/app

# Install pipenv and setuptools
RUN pip install pipenv setuptools

# Copy the Pipfile and Pipfile.lock
COPY Pipfile Pipfile.lock ./

# Install dependencies
RUN pipenv install --deploy --ignore-pipfile

# Copy the current directory contents into the container at /app
COPY . .

# Expose the FastAPI default port
EXPOSE 8000
# EXPOSE 8001

# Command to run the FastAPI server
CMD ["pipenv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# This is for mail service work parallely with iam-service
# Copy and set the startup script as the entrypoint
# COPY start.sh /start.sh
# RUN chmod +x /start.sh

# Set the ENTRYPOINT to start.sh with a default argument of "start"
# ENTRYPOINT ["/start.sh", "start"]