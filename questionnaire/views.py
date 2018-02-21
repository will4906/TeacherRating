import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from TeacherRating.forms import CaptchaForm
from questionnaire.models import AnswerSheet, AnswerItem
from rating.models import RatingEvent, LogTheClass, LogTeacherOnLessonOnClass, \
    LogTeacher, LogLessonOnClass, LogLesson, LogRatingItem, LogRatingLevel, EventOnTeacherOnLessonOnClass

logging.getLogger().setLevel(logging.DEBUG)


def index(request):
    all_event = RatingEvent.select().dicts()
    return render(request, 'questionnaire/index.html', {'all_event': all_event})


def event_overview(request, event_id):
    rating_event = RatingEvent.select().where(RatingEvent.event_id == event_id).dicts()[0]
    if rating_event.get('classification') == 0:
        overview_list = LogTheClass.select().where(LogTheClass.event_id == event_id).dicts()

    return render(request, 'questionnaire/event_overview.html',
                  {'event_id': event_id, 'classification': 0, 'overview_list': overview_list})


def event_detail(request, event_id, classification, main_id):
    if request.method == 'GET':
        classification = int(classification)
        main_list = []
        item_list = []
        rating_event = RatingEvent.select().where(RatingEvent.event_id == event_id).dicts()[0]
        log_rating_item = LogRatingItem.select().where(LogRatingItem.event_id == event_id).dicts()
        for item in log_rating_item:
            rating_level_list = LogRatingLevel.select().where(LogRatingLevel.item_id == item.get('item_id')).dicts()
            item_list.append((item, rating_level_list))
        # eotoloc_list = EventOnTeacherOnLessonOnClass.select().where(
        #     EventOnTeacherOnLessonOnClass.event_id == event_id).dicts()
        if classification == 0:
            ltoloc_list = LogTeacherOnLessonOnClass.select().where(
                LogTeacherOnLessonOnClass.event_id == event_id).dicts()
            for ltoloc in ltoloc_list:
                try:
                    teacher_id = ltoloc.get('teacher_id')
                    lc_id = ltoloc.get('lc_id')
                    log_teacher = LogTeacher.select().where(LogTeacher.event_id == event_id,
                                                            LogTeacher.teacher_id == teacher_id).dicts()[0]
                    log_lesson_on_class = LogLessonOnClass.select().where(LogLessonOnClass.event_id == event_id,
                                                                          LogLessonOnClass.lc_id == lc_id,
                                                                          LogLessonOnClass.class_id == main_id).dicts()[0]
                    log_the_class = \
                    LogTheClass.select().where(LogTheClass.class_id == log_lesson_on_class.get('class_id')).dicts()[0]
                    log_lesson = \
                    LogLesson.select().where(LogLesson.lesson_id == log_lesson_on_class.get('lesson_id')).dicts()[0]

                    main_list.append((ltoloc, log_teacher, log_the_class, log_lesson, item_list))
                except:
                    pass
        captcha = CaptchaForm()
        return render(request, 'questionnaire/event_detail.html',
                      {'captcha': captcha, 'classification': classification, 'main_list': main_list})
    else:
        rating_event = RatingEvent.select().where(RatingEvent.event_id==event_id).dicts()[0]
        answer_sheet = AnswerSheet.create(event_id=rating_event.get('event_id'))
        for key, value in request.POST.items():
            if key.find('radio') != -1:
                ltoloc_id = key.split('_')[1] # LogTeacherOnLessonOnClass
                item_id = key.split('_')[-1]
                level_id = value
                AnswerItem.create(answer_id=answer_sheet.answer_id, tlc_id=ltoloc_id, log_item_id=item_id, log_level_id=level_id)

        eotoloc_list = EventOnTeacherOnLessonOnClass.select().where(EventOnTeacherOnLessonOnClass.event_id==event_id).dicts()
        bfinish = True
        for eotoloc in eotoloc_list:
            item_list = AnswerItem.select().where(AnswerItem.tlc_id==eotoloc.get('tlc_id')).dicts()
            len_rating_item = len(LogRatingItem.select().where(LogRatingItem.event_id==event_id).dicts())
            if len(item_list) / len_rating_item < eotoloc.get('votes'):
                bfinish = False
        if bfinish is True:
            RatingEvent.update(status=1).where(RatingEvent.event_id==event_id).execute()
        return HttpResponseRedirect(reverse('questionnaire:create_result'))


def create_result(request):
    return render(request, 'questionnaire/create_result.html')


