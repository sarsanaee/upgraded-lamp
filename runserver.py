__author__ = 'alireza'
from Api import app as application
from Api.database import Base
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
import logging
from logging.handlers import RotatingFileHandler

application.debug = application.config["DEBUG"]

migrate = Migrate(application, Base)
manager = Manager(application)
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server(host=application.config["HOST"], port=application.config["PORT"]))


formatter = logging.Formatter(
application.config["LOG_FORMAT"])
handler = RotatingFileHandler(application.config["LOG_FILE_PATH"],
                              maxBytes=application.config["LOG_MAX_BYTE"],
                              backupCount=application.config["BACKUP_COUNT"])
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

application.logger.addHandler(handler)


if __name__ == '__main__':
    manager.run()
    #application.run(host=application.config["HOST"], port=application.config["PORT"])

