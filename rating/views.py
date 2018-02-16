import logging

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from TeacherRating.models import main_db
from panel.models import TheClass, LessonOnClass, Lesson, TeacherOnLessonOnClass, Teacher
from rating.models import RatingEvent, RatingItem, RatingLevel, LogRatingItem, LogRatingLevel, LogTheClass, \
    LogLessonOnClass, LogLesson, LogTeacherOnLessonOnClass, LogTeacher, EventOnTeacherOnLessonOnClass, LogItemOnEvent

logging.getLogger().setLevel(logging.DEBUG)


@login_required()
def index(request):
    return render(request, 'rating/index.html')


@login_required()
def event_admin(request):
    all_event = RatingEvent.select().order_by(RatingEvent.create_time.desc()).dicts()
    return render(request, 'rating/event_admin.html', {'all_event': all_event})


@login_required()
def create_event(request):
    """
    创建评分事件，TODO:代码过长需要简化
    :param request:
    :return:
    """
    if request.method == 'GET':
        all_class = TheClass.select().dicts()
        all_item = RatingItem.select().dicts()
        return render(request, 'rating/create_event.html', {'all_class': all_class, 'all_item': all_item})
    elif request.method == 'POST':
        with main_db.atomic() as mt:
            title = request.POST.get('title')
            description = request.POST.get('description')
            vote_type = request.POST.get('vote_type')
            votes = request.POST.get('votes')
            status = 0
            classification = request.POST.get('classification')
            rating_event = RatingEvent.create(title=title, description=description, status=status, vote_type=vote_type)
            for key, value in request.POST.items():
                if key.find('check_class') != -1:
                    if classification == 'classification_class':
                        class_id = key.split('_')[-1]
                        class_list = TheClass.select().where(TheClass.class_id == class_id).dicts()
                        for a_class in class_list:
                            log_the_class = LogTheClass.create(title=a_class.get('title'),
                                                               event_id=rating_event.event_id,
                                                               head_teacher=a_class.get('head_teacher'),
                                                               description=a_class.get('description'))
                            lesson_on_class_list = LessonOnClass.select().where(
                                LessonOnClass.class_id == a_class.get('class_id')).dicts()
                            for lesson_on_class in lesson_on_class_list:
                                lesson_list = Lesson.select().where(
                                    Lesson.lesson_id == lesson_on_class.get('lesson_id')).dicts()
                                for lesson in lesson_list:
                                    teacher_on_lesson_on_class_list = TeacherOnLessonOnClass.select().where(
                                        TeacherOnLessonOnClass.lc_id == lesson_on_class.get('lc_id')).dicts()
                                    for toloc in teacher_on_lesson_on_class_list:
                                        teacher_list = Teacher.select().where(
                                            Teacher.teacher_id == toloc.get('teacher_id')).dicts()
                                        for teacher in teacher_list:
                                            log_lesson = LogLesson.create(title=lesson.get('title'),
                                                                          event_id=rating_event.event_id,
                                                                          description=lesson.get('description'))
                                            log_lesson_on_class = LogLessonOnClass.create(
                                                event_id=rating_event.event_id,
                                                class_id=log_the_class.class_id,
                                                lesson_id=log_lesson.lesson_id)
                                            log_teacher = LogTeacher.create(name=teacher.get('name'),
                                                                            event_id=rating_event.event_id,
                                                                            description=teacher.get('description'))
                                            ltoloc = LogTeacherOnLessonOnClass.create(teacher_id=log_teacher.teacher_id,
                                                                                      event_id=rating_event.event_id,
                                                                                      lc_id=log_lesson_on_class.lc_id)
                                            EventOnTeacherOnLessonOnClass.create(event_id=rating_event.event_id,
                                                                                 tlc_id=ltoloc.tlc_id, votes=votes)
                if key.find('item_') != -1:
                    item_list = RatingItem.select().where(RatingItem.item_id == key.split('_')[-1]).dicts()
                    logging.info('before item list')
                    for rating_item in item_list:
                        logging.info('in item list')
                        # 这里只会有一个Item，所以循环没有影响。
                        log_rating_item = LogRatingItem.create(title=rating_item.get('title'),
                                                               event_id=rating_event.event_id,
                                                               description=rating_item.get('description'))
                        LogItemOnEvent.create(event_id=rating_event.event_id, item_id=log_rating_item.item_id)
                        level_list = RatingLevel.select().where(
                            RatingLevel.item_id == rating_item.get('item_id')).dicts()
                        for level in level_list:
                            LogRatingLevel.create(item_id=level.get('item_id'), title=level.get('title'),
                                                  score=level.get('score'))
            logging.info(request.POST)
            return HttpResponseRedirect(reverse('rating:event_admin'))
    return render(request, 'rating/create_event.html')


@login_required()
def delete_event(request):
    for key, value in request.POST.items():
        if key.find('check') != -1:
            event_id = key.split('_')[-1]
            RatingEvent.delete().where(RatingEvent.event_id == event_id).execute()
    return HttpResponseRedirect(reverse('rating:event_admin'))


@login_required()
def event_detail(request):
    event_id = request.GET.get('event_id')
    try:
        rating_event = RatingEvent.select().where(RatingEvent.event_id==event_id).dicts()[0]
        logging.info(rating_event)
    except:
        raise Http404()
    return render(request, 'rating/event_detail.html', {'rating_event': rating_event,})


@login_required()
def item_admin(request):
    all_item = RatingItem.select().dicts()
    item_list = []
    for a_item in all_item:
        item_list.append((a_item, RatingLevel.select().where(RatingLevel.item_id == a_item.get('item_id')).dicts()))
    return render(request, 'rating/item_admin.html', {'item_list': item_list})


@login_required()
def create_item(request):
    """
    创建评分项目
    :param request:
    :return:
    """
    if request.method == 'GET':
        target_type = request.GET.get('type')
        if target_type == 'create':
            return render(request, 'rating/create/create_item.html', {'type': 'create'})
        elif target_type == 'update':
            return render(request, 'rating/create/create_item.html', {'type': 'update'})
        else:
            raise Http404()
    elif request.method == 'POST':
        target_type = request.POST.get('type')
        if target_type == 'create':
            title = request.POST.get('title')
            description = request.POST.get('description')
            level_len = 0
            level_name_list = []
            level_score_list = []
            for key, value in request.POST.items():
                if key.find('level') != -1:
                    level_len += 1
                    part = key.split('_')[1]
                    index = key.split('_')[-1]
                    if part == 'name':
                        level_name_list.append((index, value))
                    elif part == 'score':
                        level_score_list.append((index, value))
            if level_len == 0:
                return render(request, 'rating/create/create_result.html',
                              {'result': 'error', 'msg': 'The level length is invalid'})

            rating_item = RatingItem.create(title=title, description=description)
            for name in level_name_list:
                for score in level_score_list:
                    if name[0] == score[0]:
                        RatingLevel.create(item_id=rating_item.item_id, title=name[1], score=score[1])
                        break
            return render(request, 'rating/create/create_result.html', {'result': 'success'})
        elif target_type == 'update':
            return render(request, 'rating/create/create_result.html', {'result': 'success'})
        else:
            raise Http404()


@login_required()
def delete_item(request):
    for key, value in request.POST.items():
        if key.find('check') != -1:
            item_id = key.split('_')[-1]
            RatingItem.delete().where(RatingItem.item_id == item_id).execute()
    return HttpResponseRedirect(reverse('rating:item_admin'))
