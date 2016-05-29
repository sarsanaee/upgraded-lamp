__author__ = 'alireza'
from Api import app as application
from Api.database import Base
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

application.debug = application.config["DEBUG"]
migrate = Migrate(application, Base)
manager = Manager(application)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
    #application.run(host=application.config["HOST"], port=application.config["PORT"])

