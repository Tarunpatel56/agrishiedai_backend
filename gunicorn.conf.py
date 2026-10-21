import os

# Bind to the PORT environment variable provided by Render/Heroku (default 5000)
port = os.getenv("PORT", "5000")
bind = f"0.0.0.0:{port}"

# Concurrency & timeout settings
workers = int(os.getenv("WEB_CONCURRENCY", "1"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "120"))
keepalive = 5

# Logging to stdout/stderr
accesslog = "-"
errorlog = "-"
