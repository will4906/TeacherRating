import os
from peewee import SqliteDatabase, Model

from TeacherRating.settings import BASE_DIR

main_db = SqliteDatabase(os.path.join(BASE_DIR, 'rating.db'))


class BaseModel(Model):
    class Meta:
        database = main_db