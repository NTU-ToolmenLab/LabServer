FROM python:3.6-slim
COPY . /app/OauthServer
RUN pip3 install -r /app/OauthServer/requirements.txt && \
    pip3 install gunicorn

WORKDIR /app/OauthServer
CMD "celery -A oauthserver.celery worker -B -D && gunicorn -b 0.0.0.0:5000 app:app --access-logfile /app/OauthServer/access.log"
