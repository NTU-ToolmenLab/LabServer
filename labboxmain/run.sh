celery worker -A labboxmain.celery -B -D -l info -f /app/celery.log --pidfile=/tmp/%n.pid
gunicorn -b 0.0.0.0:5000 labboxmain:app --reload --access-logfile /app/access.log
