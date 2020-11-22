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
        try:
            company_obj = Company.objects.get(slug=kwargs.get('slug'))
            user_companies_qs = company_obj.user.company_set.all()
            company_msg = company_obj.messages_set.all()
            context = {
                'company': company_obj,
                'object': company_obj,
                'userCompany_qs': user_companies_qs,
                'msg': company_msg,
            }
            return render(request, "company/messages.html", context)
        except Company.DoesNotExist:
            return redirect(reverse('404_'))


class MessageDetail(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            company_obj = Company.objects.get(user=request.user.profile, slug=kwargs.get('slug'))
            company_msg_obj = Messages.objects.get(to_obj=company_obj, slug=kwargs.get('slug_message'))
            user_companies_qs = company_obj.user.company_set.all()
            context = {
                'company': company_obj,
                'object': company_obj,
                'userCompany_qs': user_companies_qs,
                'msg_obj': company_msg_obj,
            }
            return render(request, "company/messages-detail.html", context)
        except Company.DoesNotExist:
            return redirect(reverse('404_'))


class AccountUpgrade(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_anonymous:
            user = "Guest User"
        else:
            user = self.request.user.get_full_name()
        return render(self.request, template_name="payment-upgrade/account-upgrade.html", context={"user":user})


class AddStaffProcessor(View):
    def post(self, request, *args, **kwargs):
        messageSubject = "I Have Added You As My Staff"
        staff_obj = Profile.objects.get(keycode=request.POST.get("staffCode"))
        company_obj = Company.objects.get(name=request.POST.get("company"))
        # add firm to user
        staff_obj.working_for.add(company_obj)

        # add user to firm
        company_obj.staffs.add(staff_obj)

        from django.core.mail import EmailMessage
        message = EmailMessage(
            messageSubject, request.POST.get("message"), email_settings.EMAIL_HOST_USER, [staff_obj.user.email]
        )
        message.fail_silently = False
        message.send()
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
