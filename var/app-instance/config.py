'''
We will put configuration variables here that will not be pushed to version control due to their sensitive nature.
'''

SECRET_KEY = 'development mode'
SQLALCHEMY_DATABASE_URI = 'postgresql://testuser:abc123@localhost:5432/testdb'