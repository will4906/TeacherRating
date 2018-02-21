import datetime
from django.db import models

# Create your models here.
from TeacherRating.models import BaseModel
from peewee import *

from rating.models import RatingEvent, LogTeacherOnLessonOnClass, LogRatingItem, LogRatingLevel


class AnswerSheet(BaseModel):
    answer_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    create_time = DateTimeField(default=datetime.datetime.now)
    anonymity = BooleanField(default=True)
    owner = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'answer_sheet'


class AnswerItem(BaseModel):
    answer_item_id = PrimaryKeyField()
    answer_id = ForeignKeyField(AnswerSheet, on_delete='CASCADE')
    tlc_id = ForeignKeyField(LogTeacherOnLessonOnClass, on_delete='CASCADE')
    log_item_id = ForeignKeyField(LogRatingItem, on_delete='CASCADE')
    log_level_id = ForeignKeyField(LogRatingLevel, on_delete='CASCADE')

    class Meta:
        table_name ='answer_item'

if __name__ == '__main__':
    AnswerSheet.create_table()
    AnswerItem.create_table()