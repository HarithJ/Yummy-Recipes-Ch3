import os

class Config(object):
    """Parent configuration class."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = 'p9Bv<3Eid9%$i01'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://testuser:abc123@localhost:5432/testdb')
    UPLOAD_FOLDER = 'designs/UI/uploads/'

class DevelopmentConfig(Config):
    """Configurations for Development."""

    DEBUG = True

class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://testuser:abc123@localhost:5432/testdb'

class StagingConfig(Config):
    """Configurations for Staging."""
    DEBUG = True

class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
}

'''
SECRET_KEY = 'p9Bv<3Eid9%$i01'
SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_URL', 'postgresql://testuser:abc123@localhost:5432/testdb')
'''