import os

SECRET_KEY = 'p9Bv<3Eid9%$i01'
SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_URL', 'postgresql://testuser:abc123@localhost:5432/testdb')