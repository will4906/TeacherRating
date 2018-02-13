import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from panel.models import TheClass
from rating.models import RatingEvent, RatingItem

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
    if request.method == 'GET':
        all_class = TheClass.select().dicts()
        return render(request, 'rating/create_event.html', {'all_class': all_class})
    elif request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        vote_type = request.POST.get('vote_type')
        status = 0
        classification = request.POST.get('classification')
        for key, value in request.POST.items():
            if key.find('check') != -1:
                if classification == 'classification_class':
                    pass
                # TeacherOnLessonOnClass.create(teacher_id=teacher.teacher_id, lc_id=key.split('_')[-1])
        logging.info(request.POST)
        return render(request, 'rating/create/create_result.html', {'result': 'success'})
    return render(request, 'rating/create_event.html')


@login_required()
def delete_event(request):
    pass


@login_required()
def item_admin(request):
    all_item = RatingItem.select().dicts()
    return render(request, 'rating/item_admin.html', {'all_item': all_item})


@login_required()
def create_item(request):
    pass


@login_required()
def delete_item(request):
    pass