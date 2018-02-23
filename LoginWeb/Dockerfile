FROM python:3.6-slim
COPY . /app/LoginWeb/
RUN pip3 install -e /app/LoginWeb && \
    pip3 install gunicorn docker

WORKDIR /app

# activate the flask environment
EXPOSE 5000
CMD ["gunicorn", "tzfserver:app", "-b", "0.0.0.0:5000"]
