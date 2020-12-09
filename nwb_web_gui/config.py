import configparser
import os


class Config:
    """Base config."""
    # SECRET_KEY = 'SECRET_KEY'
    SESSION_COOKIE_NAME = 'SESSION_COOKIE_NAME'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    SEND_FILE_MAX_AGE_DEFAULT = 0

    NWB_GUI_CONVERTER_CLASS = 'example'  # default example converter


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

    # The following variables are recovered by the app from ENV variables
    # In Development, we get them from a .ini file and set the ENV vars
    # In production, these ENV vars should be set in other ways
    parser = configparser.ConfigParser()
    parser.read('config.ini')

    if 'PATH' in parser.sections():
        os.environ['NWB_GUI_ROOT_PATH'] = parser['PATH']['NWB_GUI_ROOT_PATH']

    if 'CONVERTER' in parser.sections():
        os.environ['NWB_GUI_CONVERTER_MODULE'] = parser['CONVERTER']['NWB_GUI_CONVERTER_MODULE']
        os.environ['NWB_GUI_CONVERTER_CLASS'] = parser['CONVERTER']['NWB_GUI_CONVERTER_CLASS']

    if 'DASHBOARD' in parser.sections():
        os.environ['NWB_GUI_DASHBOARD_MODULE'] = parser['DASHBOARD']['NWB_GUI_DASHBOARD_MODULE']
        os.environ['NWB_GUI_DASHBOARD_CLASS'] = parser['DASHBOARD']['NWB_GUI_DASHBOARD_CLASS']

    if 'SECRETS' in parser.sections():
        os.environ['NWB_GUI_SECRET_KEY'] = parser['SECRETS']['NWB_GUI_SECRET_KEY']


config = {
    'dev': ConfigDev,
    'prod': ConfigProduction,
    'default': ConfigDev,
}
