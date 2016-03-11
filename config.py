class Config(object):
    DEBUG = True
    #DATABASE_URI = 'sqlite://:memory:'
    IP = '0.0.0.0'
    PORT = 5000
    SECRET_KEY = "\xa1xec[\tg`\xac\x96\xafv\xff\xf6\x04\xa2bT\x13\xb6\xca\xf9@\xf2"
    HMAC_KEY = "hBV+H7dt2aD/R3z"

    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
