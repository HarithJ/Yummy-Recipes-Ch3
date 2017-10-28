class Config(object):
    '''
    Common configurations that are common across all environments
    '''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'development mode'
    SQLALCHEMY_DATABASE_URI = 'postgresql://testuser:abc123@localhost:5432/testdb'

class DevelopmentConfig(Config):
    '''
    Development configurations
    '''
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    '''
    Production configurations
    '''
    DEBUG = False

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}