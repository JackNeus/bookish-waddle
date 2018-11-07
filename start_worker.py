# Custom RQ worker.

import sys
from mongoengine import register_connection
from rq import Connection, Worker
from worker import BookishWorker

from config import Config
config = vars(Config)

# Initialize MongoDB Connection
try:
	register_connection (
		alias = "default",
		name = config["DB_NAME"],
		username = config["DB_USER"],
		password = config["DB_PASSWORD"],
		host = config["DB_URL"],
		port = config["DB_PORT"]
	)
except:
	exit("Database could not be configured.")

# Provide queue names to listen to as arguments to this script,
# similar to rq worker
with Connection():
    qs = sys.argv[1:] or [config['REDIS_QUEUE_NAME']]

    w = BookishWorker(qs)
    w.work()