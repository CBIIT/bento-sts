from dotenv import load_dotenv
load_dotenv()
bind = "127.0.0.1:8000"
wsgi_app = "bento_sts.sts:create_app()"
pidfile = "/var/www/run/sts.pid"
errorlog = "/var/www/log/error-sts.log"
accesslog = "/var/www/log/access-sts.log"
loglevel = "info"
workers = 2
# certfile = "/var/www/prv/fullchain.pem"
# keyfile = "/var/www/prv/privkey.pem"
# ca_certs = "/etc/ssl/certs/ca-certificates.crt"
