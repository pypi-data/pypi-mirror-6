# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'uppsell',
        'USER': "root",
        "PASSWORD": "h0014093",
        "HOST": "localhost",
        "PORT": "3306",
        "default-character-set": "utf8",
        'init_command': 'SET storage_engine=INNODB',
    },
}

