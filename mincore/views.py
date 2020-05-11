from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.views.generic.base import View
from sendgrid import SendGridAPIClient, Mail

from accounts.models import Profile
from company.models import Company
from mincore.models import Subscribers, Messages, SupportTickets
from minloansng import email_settings
from minloansng.utils import unique_slug_generator, random_string_generator


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


class ContactProcessor(View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        messageBody = data.get('messageBody')
        messageSender = data.get('messageSender')
        messageEmail = data.get('messageEmail')
        messageSubject = data.get('messageSubject')
        sg = SendGridAPIClient(email_settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=messageEmail,
            to_emails="customer@minloans.com.ng",
            subject=messageSubject,
            html_content=messageBody
        )
        sg.send(message)
        return JsonResponse({'message': 'Message Sent Successfully!'})


class MessageList(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.full_name and request.user.profile.phone:
            try:
                company_obj = Company.objects.get(user=request.user.profile, slug=kwargs.get('slug'))
                if company_obj.name:
                    user_profile_obj = Profile.objects.get(user=request.user)
                    user_plan = str(user_profile_obj.plan)
                    if request.user.profile.is_premium:
                        if user_plan == "STARTUP":
                            if timezone.now() > user_profile_obj.trial_days:
                                # return redirect to payment page
                                messages.error(request,
                                               "Account Expired!, Your Account Has Been Expired You Would Be "
                                               "Redirected To The Payment Portal Upgrade Your Payment")
                                # jQuery Handles Redirect
                                user_companies_qs = request.user.profile.company_set.all()
                                company_msg = Messages.objects.all().filter(to_obj=company_obj)
                                context = {
                                    'company': company_obj,
                                    'object': company_obj,
                                    'userCompany_qs': user_companies_qs,
                                    'msg': company_msg,
                                }
                                return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
                            else:
                                remaining_days = user_profile_obj.trial_days - timezone.now()
                                messages.warning(request,
                                                 "You Have %s Days Left Before Account Suspension, Please Upgrade "
                                                 "Your Account" % (remaining_days.days))
                                user_companies_qs = request.user.profile.company_set.all()
                                company_msg = Messages.objects.all().filter(to_obj=company_obj)
                                context = {
                                    'company': company_obj,
                                    'object': company_obj,
                                    'userCompany_qs': user_companies_qs,
                                    'msg': company_msg,
                                }
                                return render(request, "company/dashboard.html", context)
                        elif user_plan == "BUSINESS":
                            print("BUSINESS")
                        elif user_plan == "ENTERPRISE":
                            print("ENTERPRISE")
                        else:
                            return redirect(reverse('404_'))
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
                        if user_plan == "STARTUP":
                            if timezone.now() > user_profile_obj.trial_days:
                                # return redirect to payment page
                                messages.error(request,
                                               "Account Expired!, Your Account Has Been Expired You Would Be "
                                               "Redirected To The Payment Portal Upgrade Your Payment")
                                # jQuery Handles Redirect
                                user_companies_qs = request.user.profile.company_set.all()
                                company_msg = Messages.objects.all().filter(to_obj=company_obj)
                                context = {
                                    'company': company_obj,
                                    'object': company_obj,
                                    'userCompany_qs': user_companies_qs,
                                    'msg': company_msg,
                                }
                                return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
                            else:
                                remaining_days = user_profile_obj.trial_days - timezone.now()
                                messages.warning(request,
                                                 "You Have %s Days Left Before Account Suspension, Please Upgrade "
                                                 "Your Account" % (remaining_days.days))
                                user_companies_qs = request.user.profile.company_set.all()
                                company_msg = Messages.objects.all().filter(to_obj=company_obj)
                                context = {
                                    'company': company_obj,
                                    'object': company_obj,
                                    'userCompany_qs': user_companies_qs,
                                    'msg': company_msg,
                                }
                                return render(request, "company/dashboard.html", context)
                        elif user_plan == "BUSINESS":
                            print("BUSINESS")
                        elif user_plan == "ENTERPRISE":
                            print("ENTERPRISE")
                        else:
                            return redirect(reverse('404_'))
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


class AddStaffProcessor(View):
    def post(self, request, *args, **kwargs):
        messageSubject = "I Have Added You As My Staff"
        staff_obj = Profile.objects.get(keycode=request.POST.get("staffCode"))
        company_obj = Company.objects.get(name=request.POST.get("company"))
        # add firm to user
        staff_obj.working_for.add(company_obj)

        # add user to firm
        company_obj.staffs.add(staff_obj)

        # send mail notification to user
        sg = SendGridAPIClient(email_settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=company_obj.get_email(),
            to_emails=staff_obj.user.email,
            subject=messageSubject,
            html_content=request.POST.get("message")
        )
        sg.send(message)

        return JsonResponse({'message': 'Added Successfully!'})


class SupportTicketProcessor(View):
    def post(self, request, *args, **kwargs):
        print(request.POST)

        # create the user ticket
        user_obj = Profile.objects.get(user=request.user)
        company_obj = Company.objects.get(name__iexact=request.POST.get("company"))
        SupportTickets.objects.create(
            user=user_obj,
            title=request.POST.get("title"),
            content=request.POST.get("message"),
            ticket_id=random_string_generator(7),
            affected_company=company_obj,
            slug=random_string_generator(20),
        )

        # send mail to system core..
        sg = SendGridAPIClient(email_settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=email_settings.DEFAULT_FROM_EMAIL,
            to_emails=email_settings.SUPPORT_EMAIL,
            subject="A New Ticket Was Opened!",
            html_content="A support ticket has been opened please confirm and attend to all opened tickets."
        )
        sg.send(message)
        return JsonResponse({"message":"Ticket Created Successfully!"})
