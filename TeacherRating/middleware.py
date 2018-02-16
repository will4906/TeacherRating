# middleware.py
from django.middleware.common import CommonMiddleware

from TeacherRating.models import main_db


class PeeweeConnectionMiddleware(CommonMiddleware):
    def process_request(self, request):
        main_db.connect()
        cursor = main_db.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        main_db.commit()
        cursor.close()

    def process_response(self, request, response):
        if not main_db.is_closed():
            main_db.commit()
            main_db.close()
        return response