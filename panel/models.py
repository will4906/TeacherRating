import os
from django.db import models
from peewee import *

# from django.db import models

# Create your models here.
from TeacherRating.models import BaseModel


class TheClass(BaseModel):
    """
    班级
    """
    class_id = PrimaryKeyField()
    title = CharField(max_length=256)
    head_teacher = CharField(max_length=256)  # 描述性信息，不与教师表关联
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'the_classes'


class Lesson(BaseModel):
    """
    课程
    """
    lesson_id = PrimaryKeyField()
    title = CharField(max_length=256)
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'lessons'


class LessonOnClass(BaseModel):
    """
    班级课程
    """
    lc_id = PrimaryKeyField()
    class_id = ForeignKeyField(TheClass, on_delete='CASCADE')
    lesson_id = ForeignKeyField(Lesson, on_delete='CASCADE')

    class Meta:
        table_name = 'lesson_on_class'


class Teacher(BaseModel):
    """
    教师
    """
    teacher_id = PrimaryKeyField()
    name = CharField(max_length=256)
    description = CharField(max_length=256, null=True)

    class Meta:
        table_name = 'teachers'


class TeacherOnLessonOnClass(BaseModel):
    """
    教师课程
    """
    tlc_id = PrimaryKeyField()
    teacher_id = ForeignKeyField(Teacher, on_delete='CASCADE')
    lc_id = ForeignKeyField(LessonOnClass, on_delete='CASCADE', unique=True)

    class Meta:
        table_name = 'teacher_on_lesson_on_class'


if __name__ == '__main__':
    TheClass().create_table()
    Lesson().create_table()
    LessonOnClass().create_table()
    Teacher().create_table()
    TeacherOnLessonOnClass().create_table()
