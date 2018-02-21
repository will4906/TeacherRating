from captcha.fields import CaptchaField
from django.forms import forms


class CaptchaForm(forms.Form):
    captcha = CaptchaField(required=True)
