FROM docker.io/python:3.12-slim

# Set the working directory
WORKDIR /app

# Create a directory for yamelinno
RUN mkdir -p /opt/yamelinno
# Copy the current directory contents into the container at /opt/yamelinno
COPY requirements.txt /opt/yamelinno/
COPY yamelinno.py /opt/yamelinno/
COPY requirements.txt /opt/yamelinno/
# Add entire directories to the container
COPY ./schemas /opt/yamelinno/schemas
COPY ./templates /opt/yamelinno/templates
COPY ./src /opt/yamelinno/src
# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r /opt/yamelinno/requirements.txt

# Set yamelinno as the entrypoint
ENTRYPOINT ["python", "/opt/yamelinno/yamelinno.py"]

# Run yamelinno when the container launches
CMD ["--help"]


