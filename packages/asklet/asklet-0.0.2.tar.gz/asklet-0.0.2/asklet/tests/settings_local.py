import sys
if 'test' not in sys.argv:
    #ALTER USER asklet WITH PASSWORD 'asklet';
    DATABASES = {
        'default':{
            'ENGINE': 'django.db.backends.postgresql_psycopg2', #'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'asklet',                      # Or path to database file if using sqlite3.
            'USER': 'asklet',                      # Not used with sqlite3.
            'PASSWORD': 'asklet',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }