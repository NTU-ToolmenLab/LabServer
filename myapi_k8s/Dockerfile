FROM python:3.7-slim
RUN pip3 install kubernetes flask gunicorn pyaml
RUN mkdir /app
COPY myapi_k8s.py /app/myapi_k8s.py
EXPOSE 3476
CMD ["python3", "/app/myapi_k8s.py"]
