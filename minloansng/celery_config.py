from django.conf.global_settings import TIME_ZONE

# Celery Settings
CELERY_BROKER_URL = 'redis://h:p1b15c4b4577060cc61d3711d622acbf3243b83ead7246a2419d1927cadacaddb@ec2-3-229-172-37.compute-1.amazonaws.com:31599'
CELERY_RESULT_BACKEND = 'redis://h:p1b15c4b4577060cc61d3711d622acbf3243b83ead7246a2419d1927cadacaddb@ec2-3-229-172-37.compute-1.amazonaws.com:31599'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
