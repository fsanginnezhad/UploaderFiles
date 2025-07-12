from waitress import serve
from myproject.wsgi import application
import socket

hostname = socket.gethostname()
IP_LOCAL = socket.gethostbyname(hostname)

if __name__ == '__main__':
    serve(application, host=IP_LOCAL, port=8000)
