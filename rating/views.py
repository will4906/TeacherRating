import logging

import decimal
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from TeacherRating.models import main_db
from common.database import database_using
from panel.models import TheClass, LessonOnClass, Lesson, TeacherOnLessonOnClass, Teacher
from questionnaire.models import AnswerSheet, AnswerItem
from rating.models import RatingEvent, RatingItem, RatingLevel, LogRatingItem, LogRatingLevel, LogTheClass, \
    LogLessonOnClass, LogLesson, LogTeacherOnLessonOnClass, LogTeacher, EventOnTeacherOnLessonOnClass, LogItemOnEvent


# logging.getLogger().setLevel(logging.DEBUG)


@login_required()
def index(request):
    return render(request, 'rating/index.html')


@login_required()
def event_admin(request):
    all_event = RatingEvent.select().order_by(RatingEvent.create_time.desc()).dicts()
    return render(request, 'rating/event_admin.html', {'all_event': all_event})


def get_paired_last(paired_list, source):
    for paired in paired_list:
        if paired[0] == source:
            return paired[1]
    return None


@database_using
@login_required()
def create_event(request, cursor):
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
            if classification == 'classification_class':
                rating_event = RatingEvent.create(title=title, description=description, status=status,
                                                  vote_type=vote_type, classification=0)
            else:
                rating_event = RatingEvent.create(title=title, description=description, status=status,
                                                  vote_type=vote_type, classification=-1)

            paired_class_list = []
            for key, value in request.POST.items():
                if key.find('check_class') != -1:
                    if classification == 'classification_class':
                        class_id = key.split('_')[-1]
                        # 创建班级log
                        class_list = TheClass.select().where(TheClass.class_id == class_id).dicts()
                        for a_class in class_list:
                            log_the_class = LogTheClass.create(title=a_class.get('title'),
                                                               event_id=rating_event.event_id,
                                                               head_teacher=a_class.get('head_teacher'),
                                                               description=a_class.get('description'))
                            paired_class_list.append((a_class.get('class_id'), log_the_class.class_id))

                if key.find('item_') != -1:
                    item_list = RatingItem.select().where(RatingItem.item_id == key.split('_')[-1]).dicts()
                    for rating_item in item_list:
                        # 这里只会有一个Item，所以循环没有影响。
                        log_rating_item = LogRatingItem.create(title=rating_item.get('title'),
                                                               event_id=rating_event.event_id,
                                                               description=rating_item.get('description'))
                        LogItemOnEvent.create(event_id=rating_event.event_id, item_id=log_rating_item.item_id)
                        level_list = RatingLevel.select().where(
                            RatingLevel.item_id == rating_item.get('item_id')).dicts()
                        for level in level_list:
                            LogRatingLevel.create(item_id=log_rating_item.item_id, title=level.get('title'),
                                                  score=level.get('score'))

            # 创建课程log
            paird_lesson_list = []
            lesson_list = Lesson.select().dicts()
            for lesson in lesson_list:
                log_lesson = LogLesson.create(
                    title=lesson.get('title'),
                    event_id=rating_event.event_id,
                    description=lesson.get('description')
                )
                paird_lesson_list.append((lesson.get('lesson_id'), log_lesson.lesson_id))

            # 创建教师Log
            paired_teacher_list = []
            teacher_list = Teacher.select().dicts()
            for teacher in teacher_list:
                log_teacher = LogTeacher.create(
                    name=teacher.get('name'),
                    event_id=rating_event.event_id,
                    description=teacher.get('description')
                )
                paired_teacher_list.append((teacher.get('teacher_id'), log_teacher.teacher_id))

            # 创建班级课程log
            paired_lc_list = []
            for the_class in paired_class_list:
                log_class_id = the_class[1]
                old_class_id = the_class[0]
                lesson_on_class_list = LessonOnClass.select().where(LessonOnClass.class_id == old_class_id).dicts()
                for lesson_on_class in lesson_on_class_list:
                    log_lesson_id = get_paired_last(paird_lesson_list, lesson_on_class.get('lesson_id'))
                    log_lesson_on_class = LogLessonOnClass.create(
                        event_id=rating_event.event_id,
                        class_id=log_class_id,
                        lesson_id=log_lesson_id)
                    paired_lc_list.append((lesson_on_class.get('lc_id'), log_lesson_on_class.lc_id))

            # 创建教师课程关联log
            paired_tlc_list = []
            for paired_lc in paired_lc_list:
                old_lc_id = paired_lc[0]
                log_lc_id = paired_lc[1]
                toloc_list = TeacherOnLessonOnClass.select().where(TeacherOnLessonOnClass.lc_id == old_lc_id).dicts()
                for toloc in toloc_list:
                    log_teacher_id = get_paired_last(paired_teacher_list, toloc.get('teacher_id'))
                    ltoloc = LogTeacherOnLessonOnClass.create(teacher_id=log_teacher_id,
                                                              event_id=rating_event.event_id,
                                                              lc_id=log_lc_id)
                    EventOnTeacherOnLessonOnClass.create(event_id=rating_event.event_id,
                                                         tlc_id=ltoloc.tlc_id, votes=votes)
                    paired_tlc_list.append((toloc.get('tlc_id'), ltoloc.tlc_id))

        cursor.execute(
            '''
            DELETE FROM log_teachers 
            WHERE 
            log_teachers.event_id = %d
            AND
            log_teachers.teacher_id NOT IN 
            (SELECT teacher_id FROM log_teacher_on_lesson_on_class AS t1 WHERE t1.event_id=%d)
            ''' % (rating_event.event_id, rating_event.event_id)
        )
        cursor.execute(
            '''
            DELETE FROM log_lessons
            WHERE 
            log_lessons.event_id = %d
            AND 
            log_lessons.lesson_id NOT IN 
            (SELECT lesson_id FROM log_lesson_on_class WHERE event_id = %d)
            ''' % (rating_event.event_id, rating_event.event_id)
        )
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
        rating_event = RatingEvent.select().where(RatingEvent.event_id == event_id).dicts()[0]
        logging.info(rating_event)
    except:
        raise Http404()
    return render(request, 'rating/event_detail.html', {'rating_event': rating_event, })


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


def base_info(request, cursor, event_id):
    rating_event = RatingEvent.select().where(RatingEvent.event_id == event_id).dicts()[0]
    rating_item_list = LogRatingItem.select().where(LogRatingItem.event_id == event_id).dicts()
    sum_score = 0
    for rating_item in rating_item_list:
        cursor.execute("SELECT max(score) AS score FROM log_rating_level WHERE item_id = ?",
                       (rating_item.get('item_id'),))
        score = cursor.fetchone()[0]
        rating_item.__setitem__('max_score', score)
        sum_score += score
    return rating_event, rating_item_list, sum_score


@database_using
@login_required()
def detail_class(request, cursor):
    event_id = request.GET.get('event_id')
    rating_event, rating_item_list, sum_score = base_info(request, cursor, event_id)
    info_answer_list = []
    class_list = LogTheClass.select().where(LogTheClass.event_id == event_id).dicts()
    for index_class in class_list:
        answer_list = AnswerSheet.select().where(AnswerSheet.event_id == event_id).dicts()
        for answer in answer_list:
            index_lesson_class_list = LogLessonOnClass.select().where(LogLessonOnClass.event_id == event_id,
                                                                      LogLessonOnClass.class_id == index_class.get(
                                                                          'class_id')).dicts()
            info_item_list = []
            add_answer = True
            for index_lesson_class in index_lesson_class_list:
                index_teacher_lesson_class_list = LogTeacherOnLessonOnClass.select().where(
                    LogTeacherOnLessonOnClass.lc_id == index_lesson_class.get('lc_id')).dicts()
                lesson = LogLesson.select().where(LogLesson.lesson_id == index_lesson_class.get('lesson_id')).dicts()[0]
                for index_teacher_lesson_class in index_teacher_lesson_class_list:
                    teacher = LogTeacher.select().where(
                        LogTeacher.teacher_id == index_teacher_lesson_class.get('teacher_id')
                    ).dicts()[0]
                    single_sum = 0
                    info_raing_item_list = []
                    add_rating = True
                    for rating_item in rating_item_list:
                        try:
                            answer_item = AnswerItem.select().where(
                                AnswerItem.tlc_id == index_teacher_lesson_class.get('tlc_id'),
                                AnswerItem.answer_id == answer.get('answer_id'),
                                AnswerItem.log_item_id == rating_item.get('item_id')).dicts()[0]
                            rating_level = LogRatingLevel.select().where(
                                LogRatingLevel.level_id == answer_item.get('log_level_id')
                            ).dicts()[0]
                            single_sum += rating_level.get('score')
                            info_raing_item_list.append((answer_item, rating_level))
                        except:
                            add_answer = False
                            add_rating = False
                    if add_rating is True:
                        info_item_list.append((teacher, index_class, lesson, info_raing_item_list, single_sum))
            if add_answer is True:
                info_answer_list.append(info_item_list)

    return render(request, 'rating/detail/detail_class.html',
                  {'rating_event': rating_event, 'rating_item_list': rating_item_list,
                   'sum_score': sum_score,
                   'info_answer_list': info_answer_list})


@database_using
@login_required()
def detail_answer(request, cursor):
    event_id = request.GET.get('event_id')
    rating_event, rating_item_list, sum_score = base_info(request, cursor, event_id)
    class_list = LogTheClass.select().where(LogTheClass.event_id == event_id).dicts()
    info_tlc_list = []
    for the_class in class_list:
        lesson_class_list = LogLessonOnClass.select().where(
            LogLessonOnClass.class_id == the_class.get('class_id')).dicts()
        for lesson_class in lesson_class_list:
            try:
                teacher_lesson_class = LogTeacherOnLessonOnClass.select().where(
                    LogTeacherOnLessonOnClass.lc_id == lesson_class.get('lc_id')).dicts()[0]  # 这里只有一个和没有的情况
                teacher = LogTeacher.select().where(
                    LogTeacher.teacher_id == teacher_lesson_class.get('teacher_id')
                ).dicts()[0]
                lesson = LogLesson.select().where(
                    LogLesson.lesson_id == lesson_class.get('lesson_id')
                ).dicts()[0]
                anwer_list = AnswerSheet.select().where(AnswerSheet.event_id == event_id).dicts()
                info_answer_list = []
                aver_rating_list = []
                for answer in anwer_list:
                    single_sum = 0
                    info_rating_item_list = []
                    add_answer = True
                    for i, rating_item in enumerate(rating_item_list):
                        try:
                            answer_item = AnswerItem.select().where(
                                AnswerItem.tlc_id == teacher_lesson_class.get('tlc_id'),
                                AnswerItem.answer_id == answer.get('answer_id'),
                                AnswerItem.log_item_id == rating_item.get('item_id')).dicts()[0]
                            rating_level = LogRatingLevel.select().where(
                                LogRatingLevel.level_id == answer_item.get('log_level_id')
                            ).dicts()[0]
                            single_sum += rating_level.get('score')
                            info_rating_item_list.append((answer_item, rating_level))
                            try:
                                rating_score = aver_rating_list[i]
                                aver_rating_list[i] = (rating_score[0] + rating_level.get('score'), rating_score[1] + 1)
                            except Exception as e:
                                aver_rating_list.append((rating_level.get('score'), 1))
                        except:
                            add_answer = False
                    if add_answer is True:
                        info_answer_list.append(
                            (teacher, the_class, lesson, info_rating_item_list, single_sum))
                if info_answer_list:
                    aver_list = []
                    aver_sum = decimal.Decimal(0)
                    for i, aver in enumerate(aver_rating_list):
                        aver_score = aver[0] / decimal.Decimal(aver[1])
                        aver_list.append(round(aver_score, 2))
                        aver_sum += aver_score
                    info_tlc_list.append((info_answer_list, aver_list, round(aver_sum, 2)))
            except:
                pass
    return render(request, 'rating/detail/detail_answer.html',
                  {'rating_event': rating_event, 'rating_item_list': rating_item_list,
                   'sum_score': sum_score,
                   'info_tlc_list': info_tlc_list})


@database_using
@login_required()
def detail_aver(request, cursor):
    event_id = request.GET.get('event_id')
    rating_event, rating_item_list, sum_score = base_info(request, cursor, event_id)
    teacher_list = LogTeacher.select().where(LogTeacher.event_id == event_id).dicts()
    info_tlc_list = []

    for teacher in teacher_list:
        info_lesson_class_list = []
        ltlc_list = LogTeacherOnLessonOnClass.select().where(LogTeacherOnLessonOnClass.teacher_id == teacher.get('teacher_id')).dicts()
        for ltlc in ltlc_list:
            lesson_class = LogLessonOnClass.select().where(LogLessonOnClass.lc_id == ltlc.get('lc_id')).dicts()[0]
            the_class = LogTheClass.select().where(LogTheClass.class_id == lesson_class.get('class_id')).dicts()[0]
            lesson = LogLesson.select().where(LogLesson.lesson_id == lesson_class.get('lesson_id')).dicts()[0]
            aver_rating_list = []
            sum_aver_score = 0
            for i, rating_item in enumerate(rating_item_list):
                answer_item_list = AnswerItem.select().where(
                    AnswerItem.tlc_id == ltlc.get('tlc_id'),
                    AnswerItem.log_item_id == rating_item.get('item_id')).dicts()
                sum_score = 0
                for answer_item in answer_item_list:
                    rating_level = LogRatingLevel.select().where(LogRatingLevel.level_id == answer_item.get('log_level_id')).dicts()[0]
                    sum_score += rating_level.get('score')
                division = len(answer_item_list)
                if division != 0:
                    aver_score = sum_score / division
                else:
                    aver_score = 0
                aver_rating_list.append(round(aver_score, 2))
                sum_aver_score += aver_score
            info_lesson_class_list.append((teacher, the_class, lesson, aver_rating_list, round(sum_aver_score, 2)))
        if info_lesson_class_list:
            aver_whole_rating_list = []
            for info_lesson_class in info_lesson_class_list:
                for i, aver_rating in enumerate(info_lesson_class[3]):
                    try:
                        aver_whole = aver_whole_rating_list[i]
                        aver_whole_rating_list[i] = (aver_whole[0] + aver_rating, aver_whole[1] + 1)
                    except:
                        aver_whole_rating_list.append((aver_rating, 1))

            print(len(aver_whole_rating_list))
            new_aver_whole_list = []
            new_aver_sum = 0
            for aver_whole in aver_whole_rating_list:
                new_aver = round(aver_whole[0] / aver_whole[1], 2)
                new_aver_whole_list.append(new_aver)
                new_aver_sum += new_aver
            info_tlc_list.append((info_lesson_class_list, new_aver_whole_list, new_aver_sum))

    return render(request, 'rating/detail/detail_aver.html',
                  {'rating_event': rating_event, 'rating_item_list': rating_item_list,
                   'sum_score': sum_score,
                   'info_tlc_list': info_tlc_list})
