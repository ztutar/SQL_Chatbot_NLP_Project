# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt ./
COPY chat_app.py ./


# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8501 for Streamlit
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "chat_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
