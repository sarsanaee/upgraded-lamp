__author__ = 'alireza'
from Api import app

if __name__ == '__main__':
    app.debug = app.config["DEBUG"]
    #manager.run()
    app.run(host=app.config["HOST"], port=app.config["PORT"])

