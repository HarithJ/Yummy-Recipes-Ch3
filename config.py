class Config(object):
    '''
    Common configurations that are common across all environments
    '''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'development mode'
    SQLALCHEMY_DATABASE_URI = 'postgres://hlugpiywpgwxnx:cb0b209e0de7b05ea3f8f9729b8883e0aee7d377c1f5e6baa5ccbe81067c1d66@ec2-54-225-94-143.compute-1.amazonaws.com:5432/dclmujdgvt0sbr'

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