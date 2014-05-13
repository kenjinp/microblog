import os
from authomatic.providers import oauth2, oauth2, openid
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

CONFIG = {

        'fb': {

        'class_': oauth2.Facebook,

        #Facebook is an authorizationProvider too.
        'consumer_key': '1413571332252515',
        'consumer_secret':'7b930cd8a0515af23fd4e5ef82f0b72c',

        #But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['user_about_me', 'email', 'publish_stream']
        }
}


PROVIDERS = [
    { 'name': 'facebook', 'url': 'login/fb' },
    { 'name': 'twitter', 'url': 'login/tw' }]
#    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
#    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
#    { 'name': 'MyOpenID', 'url': 'https://www.myopenid.com' }]
