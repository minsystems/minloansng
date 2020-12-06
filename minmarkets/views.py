from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse

# Create your views here.
from django.views.generic.base import View

from accounts.models import Profile
from minloansng.mixins import IsUserCookieExists
from minmarkets.models import LoanCollectionPackage


class WelcomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not self.request.user.full_name or not self.request.user.profile.phone:
            return redirect(reverse('account:user-update'))
        currentUser = self.request.user
        company_qs = currentUser.profile.company_set.all()
        incomplete_comp = []
        complete_comp = list()
        for comp_obj in company_qs:
            if comp_obj.name is None:
                incomplete_comp.append(comp_obj)
            complete_comp.append(comp_obj)

        if len(complete_comp) >= 1:
            context = {
                'user_companies': company_qs
            }
            return render(request, 'minmarket/auth.html', context)

    def post(self, request, *args, **kwargs):
        user_profile_qs = Profile.objects.all()
        accessTokens = [user_obj.token for user_obj in user_profile_qs]
        data_token = request.POST.get('accessToken')
        if data_token in accessTokens and data_token == request.user.profile.token:
            # create some cookies and store in browser local storage
            parsed_token = str(data_token).encode()
            html_parsed_token = HttpResponse(parsed_token)
            html_parsed_token.set_cookie('accessToken', value=parsed_token, max_age=None, expires=None)
            return JsonResponse(
                {'message': 'Access Token Validation Successful For %s' % (user_profile_qs.get(token=data_token))},
                status=200)
        return JsonResponse({'message': 'Error With This Token, Please Check and Validate Token'}, status=500)


class StoreHomepage(IsUserCookieExists, View):
    def get(self, request, *args, **kwargs):
        featured_packages = LoanCollectionPackage.objects.all()
        context = {'featured_packages':featured_packages}
        return render(request, 'minmarket/homepage.html', context)
