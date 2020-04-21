
import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:00000@localhost:5433/database'
CSRF_ENABLED = True 
SQLALCHEMY_TRACK_MODIFICATIONS = True


    
#import os
#basedir = os.path.abspath(os.path.dirname(__file__))


#class Config(object):
    #DEBUG = True
    #TESTING = True
    #ECSRF_ENABLED = True
    #SECRET_KEY = os.urandom(32)
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:00000@localhost:5433/fyyur'

