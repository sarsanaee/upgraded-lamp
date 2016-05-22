__author__ = 'alireza'
from Api import app

app.debug = app.config["DEBUG"]
#manager.run()
app.run(host='0.0.0.0', port=6789)
