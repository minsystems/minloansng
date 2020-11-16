from __future__ import print_function

from django.contrib.auth import logout, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, DetailView, View, UpdateView, TemplateView
from django.views.generic.edit import FormMixin
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from rest_framework import status

from company.models import Company
from mincore.models import PlanDetails, SupportTickets
from minloansng.mixins import NextUrlMixin, RequestFormAttachMixin
from .forms import LoginForm, RegisterForm, GuestForm, ReactivateEmailForm, UserDetailChangeForm
from .models import EmailActivation, Profile, User


class AccountHomeView(LoginRequiredMixin, DetailView):
    template_name = 'accounts/home.html'

    def get_object(self):
        return self.request.user


class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, "Your email has been confirmed. Proceed to login!")
                return redirect("login")
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    reset_link = reverse("account-password:password_reset")
                    msg = """Your email has already been confirmed
                    Do you need to <a href="{link}">reset your password</a>?
                    """.format(link=reset_link)
                    messages.success(request, mark_safe(msg))
                    return redirect("login")
        context = {'form': self.get_form(), 'key': key}
        return render(request, 'registration/activation-error.html', context)

    def post(self, request, *args, **kwargs):
        # create form to receive an email
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = """Activation link sent, please check your email."""
        request = self.request
        messages.success(request, msg)
        email = form.cleaned_data.get("email")
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        context = {'form': form, "key": self.key}
        return render(self.request, 'registration/activation-error.html', context)


class GuestRegisterView(NextUrlMixin, RequestFormAttachMixin, CreateView):
    form_class = GuestForm
    default_next = '/register/'

    def get_success_url(self):
        return self.get_next_url()

    def form_invalid(self, form):
        return redirect(self.default_next)


class LoginView(NextUrlMixin, RequestFormAttachMixin, FormView):
    form_class = LoginForm
    success_url = '/'
    template_name = 'accounts/login.html'
    default_next = '/'

    def form_valid(self, form):
        next_path = self.get_next_url()
        return redirect(next_path)

    def render_to_response(self, context, **response_kwargs):
        if context:
            if self.request.user.is_authenticated:
                profile_obj = Profile.objects.get(user=self.request.user)
                try:
                    company_obj = Company.objects.get(user=profile_obj)
                except Company.MultipleObjectsReturned:
                    company_qs = Company.objects.filter(user=profile_obj)
                    company_obj = company_qs.first()
                return redirect(reverse('company-url:dashboard', kwargs={'slug': company_obj.slug}))
            else:
                pass
        return super(LoginView, self).render_to_response(context, **response_kwargs)


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'
    success_message = "An Email Has Been Sent To You For Confirmation, Please Activate Your Email"


class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/')


class UserDetailUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserDetailChangeForm
    template_name = 'accounts/detail-update-view.html'

    def get_object(self):
        return self.request.user

    def get_context_data(self, *args, **kwargs):
        context = super(UserDetailUpdateView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Update Your Account Details'
        return context

    def post(self, *args, **kwargs):
        form = UserDetailChangeForm(self.request.POST or None, instance=self.get_object())
        user_profile_obj = Profile.objects.get(user=self.get_object())
        phone = self.request.POST.get("phone")
        full_name = self.request.POST.get("full_name")
        if form.is_valid():
            user_profile_obj.phone = phone
            user_profile_obj.save()
            self.get_object().full_name = full_name
            form.save()
            messages.success(self.request, "Successfully Completed Account Activation")
            return redirect(reverse('success'))
        else:
            messages.error(self.request, "Please Validate Fields, Check If Phone is In +234XXXXXXXX format")
        return render(self.request, 'accounts/detail-update-view.html', {'form': form})

    def get_success_url(self):
        return reverse("account:profile-detail", kwargs={'slug': self.get_object().profile.slug})


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile-detail.html'

    def get_context_data(self, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context['user_comp_qs'] = self.object.user.profile.company_set.all()
        context['user_plan'] = self.object.user.profile.get_plan_display()  # .plan #get_modelfield_display()
        context['works_for'] = self.object.user.profile.working_for.all()
        staffs_ = list()
        for staff_obj in self.object.user.profile.company_set.all():
            staffs_.append(staff_obj)
        context['staff_count'] = (len(staffs_))

        if timezone.now() <= self.object.user.profile.trial_days:
            context["plan_title"] = "ACTIVE"
        else:
            context["plan_title"] = "EXPIRED"

        try:
            context['plan_info_obj'] = PlanDetails.objects.get(name__iexact=self.object.user.profile.get_plan_display())
        except:
            context['plan_info_obj'] = "No Fee Plan"

        user_code = list()
        for code_obj in Profile.objects.all():
            user_code.append(code_obj.keycode)

        context["userKeyCode"] = user_code
        context['userTickets_qs'] = SupportTickets.objects.filter(user__exact=self.object)[:10]
        return context
