import os

bind = "0.0.0.0:" + os.environ.get("PORT", "5000")
workers = int(os.environ.get("WEB_CONCURRENCY", "2"))
timeout = int(os.environ.get("APP_GUNICORN_TIMEOUT", "120"))
preload_app = True  # REQUIRED: single create_app() call, shared SECRET_KEY
accesslog = "-"
errorlog = "-"
loglevel = "info"
