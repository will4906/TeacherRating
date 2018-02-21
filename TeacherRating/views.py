from django.http import JsonResponse
from django.shortcuts import render

from TeacherRating.forms import CaptchaForm
from common.dto.result import Result


def index(request):
    return render(request, 'index.html')


def check_captcha(request):
    try:
        captcha_form = CaptchaForm(request.GET)
        if captcha_form.is_valid():
            return JsonResponse(Result().__dict__)
        else:
            return JsonResponse(Result(Result.ERR).__dict__)
    except:
        return JsonResponse(Result(Result.ERR).__dict__)