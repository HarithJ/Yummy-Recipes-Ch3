class Config(object):
    """
    Common Configurations
    """
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    UPLOAD_FOLDER = 'designs/UI/uploads/'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

class DevelopmentConfig(Config):
    """
    Developement configurations
    """
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """
    Production configurations
    """
    DEBUG = False

class TestingConfig(Config):
    """
    Testing configurations
    """

    TESTING = True

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}