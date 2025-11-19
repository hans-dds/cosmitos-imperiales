# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the project definition file and install dependencies
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV STREAMLIT_SERVER_PORT 8501
ENV STREAMLIT_SERVER_ADDRESS 0.0.0.0

# Run app.py when the container launches
CMD ["streamlit", "run", "src/app.py"]
