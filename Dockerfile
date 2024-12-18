
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port the app will run on
EXPOSE 8080

# Set environment variable for Streamlit
ENV STREAMLIT_SERVER_PORT=8080

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.enableCORS", "false"]
