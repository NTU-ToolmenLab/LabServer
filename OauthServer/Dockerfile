FROM python:3.6-slim
COPY . /app/OauthServer
RUN pip3 install -r /app/OauthServer/requirements.txt && \
    pip3 install gunicorn

WORKDIR /app/OauthServer
CMD "celery worker -A oauthserver.celery -B -D -l info -f /app/OauthServer/celery.log --pidfile=/app/%n.pid && gunicorn -b 0.0.0.0:5000 oauthserver:app --reload --access-logfile /app/OauthServer/access.log"
