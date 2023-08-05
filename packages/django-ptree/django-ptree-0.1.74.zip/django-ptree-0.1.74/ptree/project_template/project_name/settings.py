import os
import ptree.settings

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

settings = {
    'CREATE_DEFAULT_SUPERUSER': True,
    'ADMIN_USERNAME': 'ptree',
    'ADMIN_PASSWORD': 'ptree',
    'AWS_ACCESS_KEY_ID': os.environ.get('AWS_ACCESS_KEY_ID'),
    'AWS_SECRET_ACCESS_KEY': os.environ.get('AWS_SECRET_ACCESS_KEY'),
    'DEBUG': DEBUG,
    'DATABASES': DATABASES,
    'INSTALLED_APPS': [
        'ptree',
    ],
    'INSTALLED_PTREE_APPS': [
    ],
    # don't share this with anybody.
    # Change this to something unique (e.g. mash your keyboard), and then delete this comment.
    'SECRET_KEY': 'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz',
    'BASE_DIR': BASE_DIR,
    'WSGI_APPLICATION': '{{ project_name }}.wsgi.application',
    'ROOT_URLCONF': '{{ project_name }}.urls',
}

ptree.settings.augment_settings(settings)
