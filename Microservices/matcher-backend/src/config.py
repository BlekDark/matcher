import os

DB_HOST = os.getenv('DB_HOST', None)
DB_NAME = os.getenv('DB_NAME', None)
DB_USER = os.getenv('DB_USER', None)
DB_PASS = os.getenv('DB_PASS', None)

if not (DB_HOST or DB_NAME or DB_USER or DB_PASS):
    raise EnvironmentError("Missing database credentials!")

TEST_MATCHER = os.getenv('TEST_MATCHER', None)

if not TEST_MATCHER:
    raise EnvironmentError("Missing test_ matcher host!")
