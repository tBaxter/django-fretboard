SECRET_KEY = "lorem ipsum"

INSTALLED_APPS = (
    'fretboard',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SITE_ID = 1
