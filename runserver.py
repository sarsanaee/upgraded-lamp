__author__ = 'alireza'
from Api import app
from Api.database import Base
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


migrate = Migrate(app, Base)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    app.debug = app.config["DEBUG"]
    #manager.run()
    app.run(host=app.config["HOST"], port=app.config["PORT"])

