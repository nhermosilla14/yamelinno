FROM docker.io/alpine:3.20 as compiler

# Install python and pip
RUN apk add --no-cache python3 py3-pip
RUN apk add --no-cache upx binutils gcc

# Create a temporary directory for yamelinno
RUN mkdir -p /tmp/yamelinno
# Create an output directory for the compiled binary
RUN mkdir -p /opt/yamelinno
# Copy the current directory contents into the container at /tmp/yamelinno
COPY requirements.txt /tmp/yamelinno/
COPY yamelinno.py /tmp/yamelinno/
COPY requirements.txt /opt/yamelinno/
COPY ./src /tmp/yamelinno/src
# Add assets directories to the container at /opt/yamelinno
COPY ./schemas /opt/yamelinno/schemas
COPY ./templates /opt/yamelinno/templates
# Prepare the virtual environment
RUN python3 -m venv /tmp/yamelinno/venv
# Can't use source .../bin/activate in Dockerfile
ENV PATH /tmp/yamelinno/venv/bin/:$PATH
# Install the dependencies
RUN python3 -m pip install --no-cache-dir -r /tmp/yamelinno/requirements.txt
RUN python3 -m pip install --no-cache-dir pyinstaller
RUN pyinstaller --onefile --clean --distpath /tmp/yamelino /tmp/yamelinno/yamelinno.py

# Now we build the final image
FROM docker.io/alpine:3.20 as base
# Set the working directory in the container
WORKDIR /app
# Copy the compiled binary from the compiler stage
COPY --from=compiler /tmp/yamelino/yamelinno /opt/yamelinno/yamelinno
COPY --from=compiler /opt/yamelinno/schemas /opt/yamelinno/schemas
COPY --from=compiler /opt/yamelinno/templates /opt/yamelinno/templates
# If YAMELLINO_SCHEMAS is set, yamelinno will look for schemas in that directory
ENV YAMELINNO_SCHEMAS=/opt/yamelinno/schemas:$YAMELLINO_SCHEMAS
# If YAMELLINO_TEMPLATES is set, yamelinno will look for templates in that directory
ENV YAMELINNO_TEMPLATES=/opt/yamelinno/templates:$YAMELLINO_TEMPLATES
# Set yamelinno as the entrypoint
ENTRYPOINT ["/opt/yamelinno/yamelinno"]
# Run yamelinno when the container launches
CMD ["--help"]


