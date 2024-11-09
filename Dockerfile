# Use Miniconda3 as the base image
FROM continuumio/miniconda3:latest

# Install sudo, git, wget, gcc, g++, and other essential build tools
RUN apt-get update && \
    apt-get install -y sudo git wget build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python 3.11 using Conda
RUN conda install python=3.11

# Upgrade pip and setuptools to avoid deprecation warnings
RUN pip install --upgrade pip setuptools

# Set Python 3.11 as default by creating a symbolic link
RUN ln -sf /opt/conda/bin/python3.11 /opt/conda/bin/python && \
    ln -sf /opt/conda/bin/python3.11 /usr/bin/python

# Verify installations
RUN python --version && \
    gcc --version && \
    g++ --version && \
    pip --version && \
    conda --version

# setup repo
RUN git clone --branch deployment https://github.com/adalat-ai-tech/indic-punct.git
WORKDIR /indic-punct

# install dependencies
RUN bash install.sh
RUN python setup.py bdist_wheel
RUN pip install -e .

# fix runtime bugs
RUN pip install huggingface-hub==0.23.2
RUN pip install transformers==4.40.0
RUN conda install -c conda-forge gcc=12.1.0

# Expose the port the app runs on
EXPOSE 8080

# Define environment variable to prevent Python from buffering stdout/stderr
# and writing byte code to file
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the server with uWSGI, binding to all interfaces on the PORT environment variable
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]