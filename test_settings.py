import os

SECRET_KEY = "lorem ipsum"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'fretboard/test_templates',
        ],
        'APP_DIRS': True,
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'fretboard',
    'typogrify',
    'voting',
    'easy_thumbnails',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

SITE_ID = 1

ROOT_URLCONF = 'fretboard.urls'

#stripped down middleware
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_DIRS = (
    'templates',
    os.path.join(os.path.dirname(__file__), '..', 'templates').replace('\\', '/')
)
