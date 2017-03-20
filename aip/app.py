from __future__ import absolute_import, unicode_literals
from celery import Celery
from aip.libs import utils


app = Celery('ADSimportpipeline',
             broker='amqp://',
             include=['aip.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

app.conf.update(utils.load_config())

if __name__ == '__main__':
    app.start()