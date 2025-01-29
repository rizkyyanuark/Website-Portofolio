# Use the appropriate base image
FROM python:3.10-slim

ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

# Set the working directory
WORKDIR $APP_HOME

# Copy the application code into the container
COPY . ./

# Copy the credentials file into the container
COPY GOOGLE_APPLICATION_CREDENTIALS.json /app/GOOGLE_APPLICATION_CREDENTIALS.json

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the environment variable for Google Application Credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/GOOGLE_APPLICATION_CREDENTIALS.json

# Expose the port that the app runs on
EXPOSE 8080
ENV PORT=8080

# Run the application using gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app