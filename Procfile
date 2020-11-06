web: gunicorn minloansng.wsgi --log-file -

celery -A minloansng worker -l info

celery -A minloansng beat -l info