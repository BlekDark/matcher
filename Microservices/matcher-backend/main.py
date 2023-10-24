import os

from src.user_backend import fastapi_app as user_backend
from src.matcher_backend import fastapi_app as matcher_backend

import uvicorn
from sshtunnel import SSHTunnelForwarder

REMOTE_HOST = os.getenv('REMOTE_HOST', None)
REMOTE_SSH_PORT = os.getenv('REMOTE_SSH_PORT', None)
REMOTE_USERNAME = os.getenv('REMOTE_USERNAME', None)
REMOTE_PASSWORD = os.getenv('REMOTE_PASSWORD', None)

server = SSHTunnelForwarder((REMOTE_HOST, REMOTE_SSH_PORT),
                            ssh_username=REMOTE_USERNAME,
                            ssh_password=REMOTE_PASSWORD,
                            remote_bind_address=('localhost', 5432),
                            local_bind_address=('localhost', 5432))

if __name__ == '__main__':
    server.start()
    # uvicorn.run(user_backend, log_level='error', port=8000)
    uvicorn.run(matcher_backend, log_level='error', port=8000)
    server.stop()
