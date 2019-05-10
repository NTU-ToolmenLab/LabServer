FROM python:3.7-slim
RUN mkdir /app
RUN pip3 install --no-cache-dir flask docker gunicorn
WORKDIR /app
EXPOSE 3476
CMD ["python3", "/app/api.py"]
