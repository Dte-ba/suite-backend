from local_settings import *
import dj_database_url

DEBUG = False
DATABASES['default'] = dj_database_url.config(conn_max_age=600)
