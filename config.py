HMAC_KEY = 'hBV+H7dt2aD/R3z'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:yokohama@localhost/FarmBase'
DEBUG = False
SECRET_KEY = '\xa1xec[\tg`\xac\x96\xafv\xff\xf6\x04\xa2bT\x13\xb6\xca\xf9@\xf2'
HOST = '0.0.0.0'
PORT = 6789
DAILY = 3599
MYKET_URL = 'https://api.myket.ir/IapService.svc/getpurchases?packagename={}&productId={}&token={}'
MYKET_ID = 1
IRANAPPS_ID = 2
LOG_COLLECTOR_PATH = '/var/www/upgraded-lamp/log_collector.sh'
#LOG_FORMAT = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(message)s"
LOG_FILE_PATH = "/var/log/uwsgi/upgraded-lamp/app.log"
#LOG_FILE_PATH = "app_log.txt"
LOG_MAX_BYTE = 10000000
BACKUP_COUNT = 5
