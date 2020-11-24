from django.shortcuts import render
from django.utils.datetime_safe import datetime

# Create your views here.
from django.views.generic.base import View


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'minmarket/auth.html', context)