FROM python:3.6-slim
RUN apt update -y && apt install build-essential -y
RUN apt install -y xmlsec1 libxmlsec1-dev pkg-config
COPY . /app/LoginWeb/
RUN pip3 install -e /app/LoginWeb && \
    pip3 install gunicorn docker python3-saml

WORKDIR /app
RUN mkdir /app/sock/ -p
RUN touch /app/database.db

# activate the flask environment
EXPOSE 5000
CMD ["gunicorn", "tzfserver:app", "-b", "0.0.0.0:5000"]
