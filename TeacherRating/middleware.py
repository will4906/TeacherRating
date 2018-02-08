# middleware.py
from django.middleware.common import CommonMiddleware

from panel.models import db  # Import the peewee database instance.


class PeeweeConnectionMiddleware(CommonMiddleware):
    def process_request(self, request):
        db.connect()
        cursor = db.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        db.commit()
        cursor.close()

    def process_response(self, request, response):
        if not db.is_closed():
            db.close()
        return response