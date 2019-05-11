FROM python:3.7-slim
RUN pip3 install --no-cache-dir \
    flask Flask-SQLAlchemy Flask-Testing flask-login \
    Authlib passlib lxml requests \
    redis celery python-dateutil \
    gunicorn

RUN mkdir -p /app
WORKDIR /app
CMD "celery worker -A labboxmain.celery -B -D -l info -f /app/celery.log --pidfile=/tmp/%n.pid && gunicorn -b 0.0.0.0:5000 labboxmain:app --reload --access-logfile /app/access.log"
