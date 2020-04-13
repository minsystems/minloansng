from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View

from accounts.models import Profile
from company.models import Company
from mincore.models import Subscribers, Messages


class SubscriberProcessor(View):
    def post(self, request, *args, **kwargs):
        mList = Subscribers.objects.all()
        email = request.POST.get('email')
        obj_list = list()
        for obj in mList:
            obj_list.append(obj)
        if email in obj_list:
            return JsonResponse({'message': 'This email is already subscribed!'})
        Subscribers.objects.create(email=email)
        return JsonResponse({'message': 'Subscription Successfully!'})


class MessageList(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.full_name and request.user.profile.phone:
            try:
                company_obj = Company.objects.get(user=request.user.profile, slug=kwargs.get('slug'))
                if company_obj.name:
                    user_profile_obj = Profile.objects.get(user=request.user)
                    user_plan = str(user_profile_obj.plan)
                    if request.user.profile.is_premium:
                        pass
                        # perform code block here
                    elif user_plan == "FREEMIUM":
                        if timezone.now() > user_profile_obj.trial_days:
                            # return redirect to payment page
                            messages.error(request, "Account Expired!")  # jQuery Handles Redirect
                        else:
                            user_companies_qs = request.user.profile.company_set.all()
                            company_msg = Messages.objects.all().filter(to_obj=company_obj)
                            context = {
                                'company': company_obj,
                                'object': company_obj,
                                'userCompany_qs': user_companies_qs,
                                'msg': company_msg,
                            }
                            return render(self.request, 'company/messages.html', context)
                    else:
                        return redirect(reverse('404_'))
                else:
                    return redirect(
                        reverse('company-url:update-company-profile', kwargs={'slug': company_obj.slug}))
            except Company.DoesNotExist:
                return redirect('404_')
        else:
            return redirect(reverse('account:user-update'))


class MessageDetail(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.full_name and request.user.profile.phone:
            try:
                company_obj = Company.objects.get(user=request.user.profile, slug=kwargs.get('slug'))
                if company_obj.name:
                    user_profile_obj = Profile.objects.get(user=request.user)
                    user_plan = str(user_profile_obj.plan)
                    if request.user.profile.is_premium:
                        pass
                    elif user_plan == "FREEMIUM":
                        if timezone.now() > user_profile_obj.trial_days:
                            # return redirect to payment page
                            messages.error(request, "Account Expired!")  # jQuery Handles Redirect
                        else:
                            user_companies_qs = request.user.profile.company_set.all()
                            company_msg_obj = Messages.objects.get(to_obj=company_obj, slug=kwargs.get('slug_message'))
                            context = {
                                'company': company_obj,
                                'object': company_obj,
                                'userCompany_qs': user_companies_qs,
                                'msg_obj': company_msg_obj,
                            }
                            return render(self.request, 'company/messages-detail.html', context)
                    else:
                        return redirect(reverse('404_'))
                else:
                    return redirect(
                        reverse('company-url:update-company-profile', kwargs={'slug': company_obj.slug}))
            except Company.DoesNotExist:
                return redirect('404_')
        else:
            return redirect(reverse('account:user-update'))


class AccountUpgrade(View):
    def get(self, *args, **kwargs):
        return render(self.request, template_name="payment-upgrade/account-upgrade.html", context={})
