import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from common.database import database_using
from common.dto.result import Result
from panel.models import TheClass, Lesson, Teacher, LessonOnClass, TeacherOnLessonOnClass

logging.getLogger().setLevel(logging.DEBUG)


@login_required
def index(request):
    return render(request, 'panel/index.html')


@login_required()
def class_admin(request):
    all_class = TheClass().select().dicts()
    return render(request, 'panel/class_admin.html', {'all_class': all_class})


@database_using
@login_required()
def create_class(request, cursor):
    """
    创建或修改班级
    :param request: 其中type参数create/update指明是创建或修改，若为update会携带class_id
    :param cursor:
    :return:
    """
    if request.method == 'GET':
        target_type = request.GET.get('type', 'create')
        if target_type == 'create':
            # 创建班级页面
            all_lesson = Lesson().select().order_by(Lesson.lesson_id.desc()).dicts()
            return render(request, 'panel/create/create_class.html', {'type': 'create', 'all_lesson': all_lesson})
        elif target_type == 'update':
            # 修改班级页面
            class_id = request.GET.get("class_id")
            if class_id is None:
                raise Http404()
            else:
                the_class = TheClass().get(TheClass.class_id == class_id)
                cursor.execute(
                    "SELECT * FROM lessons WHERE lesson_id NOT IN (SELECT lessons.lesson_id "
                    "FROM lessons EXCEPT SELECT lesson_id FROM lesson_on_class WHERE class_id = %s)" %
                    (class_id,)
                )
                lesson_on_class = cursor.fetchall()
                cursor.execute(
                    "SELECT * FROM lessons WHERE lesson_id IN (SELECT lessons.lesson_id "
                    "FROM lessons EXCEPT SELECT lesson_id FROM lesson_on_class WHERE class_id = %s) ORDER BY lessons.lesson_id DESC " %
                    (class_id,)
                )
                lesson_not_on_class = cursor.fetchall()
                logging.info(lesson_not_on_class)
                return render(request, 'panel/create/create_class.html',
                              {'type': 'update', 'the_class': the_class, 'lesson_on_class': lesson_on_class,
                               'lesson_not_on_class': lesson_not_on_class})
    elif request.method == 'POST':
        # 提交信息页面
        target_type = request.POST.get('type', 'create')
        try:
            if target_type == 'create':
                title = request.POST.get('title')
                head_teacher = request.POST.get('head_teacher')
                description = request.POST.get('description')
                lesson_on_class_list = []
                for key, value in request.POST.items():
                    if key.find('check') != -1:
                        lesson_on_class_list.append(key.split('_')[-1])
                the_class = TheClass.create(title=title, head_teacher=head_teacher, description=description)
                for loc in lesson_on_class_list:
                    LessonOnClass.create(class_id=the_class.class_id, lesson_id=loc)
            elif target_type == 'update':
                class_id = request.POST.get('class_id')
                title = request.POST.get('title')
                head_teacher = request.POST.get('head_teacher')
                description = request.POST.get('description')
                lesson_on_class_list = []
                for key, value in request.POST.items():
                    if key.find('check') != -1:
                        lesson_on_class_list.append(key.split('_')[-1])

                q = (TheClass().update({TheClass.title: title,
                                        TheClass.head_teacher: head_teacher,
                                        TheClass.description: description}).where(
                    TheClass.class_id == class_id))
                q.execute()
                LessonOnClass.delete().where(LessonOnClass.class_id == class_id).execute()
                for loc in lesson_on_class_list:
                    LessonOnClass.create(class_id=class_id, lesson_id=loc)
            return render(request, 'panel/create/create_result.html', {'result': 'success'})
        except Exception as e:
            return render(request, 'panel/create/create_result.html', {'result': 'error', 'msg': e})
    else:
        raise Http404()


@login_required()
def delete_class(request):
    """
    删除班级
    :param request:
    :return:
    """
    for key, value in request.POST.items():
        if key.find('check') != -1:
            class_id = key.split('_')[-1]
            TheClass.delete().where(TheClass.class_id == class_id).execute()
    return HttpResponseRedirect(reverse('panel:class_admin'))


@login_required()
def lesson_admin(request):
    all_lesson = Lesson().select().dicts()
    return render(request, 'panel/lesson_admin.html', {'all_lesson': all_lesson})


@login_required()
def create_lesson(request):
    """
    创建或修改课程
    :param request: 其中type参数create/update指明是创建或修改，若为update会携带lesson_id
    :return:
    """
    if request.method == 'GET':
        target_type = request.GET.get('type', 'create')
        if target_type == 'create':
            # 创建课程页面
            return render(request, 'panel/create/create_lesson.html', {'type': 'create'})
        elif target_type == 'update':
            # 修改课程页面
            lesson_id = request.GET.get("lesson_id")
            if lesson_id is None:
                raise Http404()
            else:
                lesson = Lesson().get(Lesson.lesson_id == lesson_id)
                return render(request, 'panel/create/create_lesson.html', {'type': 'update', 'lesson': lesson})
    elif request.method == 'POST':
        # 提交信息页面
        type = request.POST.get('type', 'create')
        logging.info(request.POST)
        try:
            if type == 'create':
                logging.info(request.POST.get('title'))
                Lesson.create(title=request.POST.get('title'), description=request.POST.get('description'))
            elif type == 'update':
                q = (Lesson().update({Lesson.title: request.POST.get('title'),
                                      Lesson.description: request.POST.get('description')}).where(
                    Lesson.lesson_id == request.POST.get('lesson_id')))
                q.execute()
            return render(request, 'panel/create/create_result.html', {'result': 'success'})
        except Exception as e:
            return render(request, 'panel/create/create_result.html', {'result': 'error', 'msg': e})
    else:
        raise Http404()


@login_required()
def delete_lesson(request):
    """
    删除课程
    :param request:
    :return:
    """
    for key, value in request.POST.items():
        if key.find('check') != -1:
            lesson_id = key.split('_')[-1]
            Lesson.delete().where(Lesson.lesson_id == lesson_id).execute()
    return HttpResponseRedirect(reverse('panel:lesson_admin'))


@login_required()
def teacher_admin(request):
    all_teacher = Teacher().select().dicts()
    return render(request, 'panel/teacher_admin.html', {'all_teacher': all_teacher})


@database_using
@login_required()
def create_teacher(request, cursor):
    """
    创建或修改教师
    :param request:
    :param cursor:
    :return:
    """
    if request.method == 'GET':
        target_type = request.GET.get('type', 'create')
        if target_type == 'create':
            # 创建教师页面
            cursor.execute(
                '''
                SELECT lesson_on_class.lc_id, the_classes.title AS class_title, the_classes.description AS class_description,
                lessons.title AS lesson_title, lessons.description AS lesson_description
                FROM the_classes, lessons, lesson_on_class
                WHERE
                the_classes.class_id = lesson_on_class.class_id
                AND 
                lessons.lesson_id = lesson_on_class.lesson_id
                AND 
                lesson_on_class.lc_id NOT IN 
                (
                SELECT lc_id FROM teacher_on_lesson_on_class AS tolc
                )
                '''
            )
            lesson_on_class = cursor.fetchall()
            return render(request, 'panel/create/create_teacher.html',
                          {'type': 'create', 'lesson_on_class': lesson_on_class})
        elif target_type == 'update':
            # 修改教师页面
            teacher_id = request.GET.get("teacher_id")
            if teacher_id is None:
                raise Http404("Can't find the teacher")
            else:
                teacher = Teacher().get(Teacher.teacher_id == teacher_id)
                cursor.execute(
                    '''
                    SELECT lesson_on_class.lc_id, the_classes.title AS class_title, the_classes.description AS class_description,
                    lessons.title AS lesson_title, lessons.description AS lesson_description
                    FROM the_classes, lessons, lesson_on_class
                    WHERE
                    the_classes.class_id = lesson_on_class.class_id
                    AND 
                    lessons.lesson_id = lesson_on_class.lesson_id
                    AND 
                    lesson_on_class.lc_id NOT IN 
                    (
                    SELECT lc_id FROM teacher_on_lesson_on_class AS tolc
                    )
                    '''
                )
                last_lesson_on_class = cursor.fetchall()
                cursor.execute(
                    '''
                    SELECT lesson_on_class.lc_id, the_classes.title AS class_title, the_classes.description AS class_description,
                    lessons.title AS lesson_title, lessons.description AS lesson_description
                    FROM the_classes, lessons, lesson_on_class
                    WHERE
                    the_classes.class_id = lesson_on_class.class_id
                    AND 
                    lessons.lesson_id = lesson_on_class.lesson_id
                    AND 
                    lesson_on_class.lc_id IN 
                    (
                    SELECT lc_id FROM teacher_on_lesson_on_class AS tolc
                    WHERE tolc.teacher_id = %s
                    )
                    ''' % (teacher_id,)
                )
                teacher_lesson_on_class = cursor.fetchall()
                return render(request, 'panel/create/create_teacher.html',
                              {'type': 'update', 'teacher': teacher, 'last_lesson_on_class': last_lesson_on_class,
                               'teacher_lesson_on_class': teacher_lesson_on_class})
    elif request.method == 'POST':
        try:
            target_type = request.GET.get('type', 'create')
            if target_type == 'create':
                name = request.POST.get('name')
                description = request.POST.get('description')
                teacher = Teacher().create(name=name, description=description)
                for key, value in request.POST.items():
                    if key.find('check') != -1:
                        TeacherOnLessonOnClass.create(teacher_id=teacher.teacher_id, lc_id=key.split('_')[-1])
            elif target_type == 'update':
                teacher_id = request.POST.get('teacher_id')
                if teacher_id is None:
                    raise Http404("Can't find the teacher")
                else:
                    name = request.POST.get('name')
                    description = request.POST.get('description')
                    Teacher.update({Teacher.name: name, Teacher.description: description}).where(Teacher.teacher_id==teacher_id).execute()
                    TeacherOnLessonOnClass.delete().where(TeacherOnLessonOnClass.teacher_id == teacher_id).execute()
                    for key, value in request.POST.items():
                        if key.find('check') != -1:
                            TeacherOnLessonOnClass.create(teacher_id=teacher_id, lc_id=key.split('_')[-1])
            return render(request, 'panel/create/create_result.html', {'result': 'success'})
        except Exception as e:
            return render(request, 'panel/create/create_result.html', {'result': 'error', 'msg': e})
    return render(request, 'panel/create/create_teacher.html')


@login_required()
def delete_teacher(request):
    for key, value in request.POST.items():
        if key.find('check') != -1:
            teacher_id = key.split('_')[-1]
            Teacher.delete().where(Teacher.teacher_id == teacher_id).execute()
    return HttpResponseRedirect(reverse('panel:teacher_admin'))
