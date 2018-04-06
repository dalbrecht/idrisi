from tinymongo import TinyMongoClient
from datetime import datetime

class Persistence:
    def __init__(self):
        self._connection = TinyMongoClient()
        self._db = self._connection.idrisi_scrapes

    def save_object(self, model_object):
        collection = model_object.get_type()
        parent = model_object.get_parent()
        self._db[collection].update(
            {"_id":model_object.get_id()},
            model_object.get_properties(),
            {"upsert": "true"})
        self._db[collection].update(
            {"_id":model_object.get_id},
            {"$addToSet": {"scans": datetime.now()}}
        )

