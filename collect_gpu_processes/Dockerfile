FROM nvidia/cuda:10.0-base
RUN apt update -y && \
    apt install -y python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install --no-cache-dir psutil prometheus_client
RUN mkdir /app
COPY collect_gpu_processes.py /app/collect_gpu_processes.py
WORKDIR /app
CMD ["python3", "/app/collect_gpu_processes.py"]
