from dotenv import load_dotenv
load_dotenv()
bind = "127.0.0.1:8000"
wsgi_app = "bento_sts.sts:create_app()"
pidfile = "sts.pid"
errorlog = "error-sts.log"
accesslog = "access-sts.log"
loglevel = "debug"
workers = 2
# certfile = "/var/www/prv/fullchain.pem"
# keyfile = "/var/www/prv/privkey.pem"
# ca_certs = "/etc/ssl/certs/ca-certificates.crt"
