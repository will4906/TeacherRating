"""
评分模型定义，其中Log开头的定义均为历史记录，只可增加，不可修改或删除。
"""
import datetime
from django.db import models
from peewee import *

# Create your models here.

# from TeacherRating.settings import BASE_DIR
from TeacherRating.models import BaseModel
from panel.models import TeacherOnLessonOnClass


class RatingEvent(BaseModel):
    """
    评分事件，将所有信息汇总
    """
    event_id = PrimaryKeyField()
    title = CharField(max_length=256)
    status = IntegerField(default=0)    # 0:投票中， 1:投票结束
    vote_type = IntegerField(default=0)     # 0:不记名投票， 1：记名投票
    classification = IntegerField()  # 分类方式: 0->班级
    create_time = DateTimeField(default=datetime.datetime.now)
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'rating_event'


class RatingItem(BaseModel):
    """
    评分项目，e.g. 教师讲课效果、教师纪律管理等
    """
    item_id = PrimaryKeyField()
    title = CharField(max_length=256)
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'rating_item'


class LogRatingItem(BaseModel):
    """
    评分项目记录，e.g. 教师讲课效果、教师纪律管理等
    """
    item_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    title = CharField(max_length=256)
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'log_rating_item'


class RatingLevel(BaseModel):
    """
    评分级别，e.g. 好:10分，一般:7分，差: 5分
    """
    level_id = PrimaryKeyField()
    item_id = ForeignKeyField(RatingItem, on_delete='CASCADE')
    title = CharField(max_length=256)
    score = DecimalField()

    class Meta:
        table_name = 'rating_level'


class LogRatingLevel(BaseModel):
    """
    评分级别记录，e.g. 好:10分，一般:7分，差: 5分
    """
    level_id = PrimaryKeyField()
    item_id = ForeignKeyField(LogRatingItem, on_delete='CASCADE')
    title = CharField(max_length=256)
    score = DecimalField()

    class Meta:
        table_name = 'log_rating_level'


class LogItemOnEvent(BaseModel):
    """
    评分项与评分事件的绑定
    """
    ie_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    item_id = ForeignKeyField(LogRatingItem, on_delete='CASCADE')

    class Meta:
        table_name = 'log_item_on_event'


class LogTheClass(BaseModel):
    """
    班级记录
    """
    class_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    title = CharField(max_length=256)
    head_teacher = CharField(max_length=256)  # 描述性信息，不与教师表关联
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'log_the_classes'


class LogLesson(BaseModel):
    """
    课程记录
    """
    lesson_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    title = CharField(max_length=256)
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'log_lessons'


class LogLessonOnClass(BaseModel):
    """
    班级课程记录
    """
    lc_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    class_id = ForeignKeyField(LogTheClass, on_delete='CASCADE')
    lesson_id = ForeignKeyField(LogLesson, on_delete='CASCADE')

    class Meta:
        table_name = 'log_lesson_on_class'


class LogTeacher(BaseModel):
    """
    教师记录
    """
    teacher_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    name = CharField(max_length=256)
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'log_teachers'


class LogTeacherOnLessonOnClass(BaseModel):
    """
    教师课程记录
    """
    tlc_id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    teacher_id = ForeignKeyField(LogTeacher, on_delete='CASCADE')
    lc_id = ForeignKeyField(LogLessonOnClass, on_delete='CASCADE', unique=True)

    class Meta:
        table_name = 'log_teacher_on_lesson_on_class'


class EventOnTeacherOnLessonOnClass(BaseModel):
    """
    需要评分的课程与评分事件的绑定
    """
    id = PrimaryKeyField()
    event_id = ForeignKeyField(RatingEvent, on_delete='CASCADE')
    tlc_id = ForeignKeyField(LogTeacherOnLessonOnClass, on_delete='CASCADE')
    votes = IntegerField(default=10)

    class Meta:
        table_name = 'event_on_teacher_on_lesson_on_class'
        indexes = (
            (('event_id', 'tlc_id', ), True),
        )


if __name__ == '__main__':

    LogLesson.create_table()
    LogTheClass.create_table()
    LogLessonOnClass.create_table()
    LogTeacher.create_table()
    LogTeacherOnLessonOnClass.create_table()

    RatingItem.create_table()
    LogRatingItem.create_table()
    RatingLevel.create_table()
    LogRatingLevel.create_table()
    RatingEvent.create_table()
    LogItemOnEvent.create_table()
    EventOnTeacherOnLessonOnClass.create_table()