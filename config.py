
class Config:
    """Base config."""
    SECRET_KEY = 'SECRET_KEY'
    SESSION_COOKIE_NAME = 'SESSION_COOKIE_NAME'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SEND_FILE_MAX_AGE_DEFAULT = 0

    NWB_CONVERTER = 'example'


class ConfigProduction(Config):
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'DATABASE_URI_PRODUCTION'


class ConfigDev(Config):
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    DATABASE_URI = 'DEV_DATABASE_URI'

    EXPLORER_PATH = '/home/vinicius/Área de Trabalho/Trabalhos/nwb-web-gui/files'
    #EXPLORER_PATH = r'C:\Users\Luiz\Desktop\data_app'
