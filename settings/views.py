from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView

from accounts.models import Profile, ThirdPartyCreds
from company.models import Company
from loans.models import LoanType
from minloansng.mixins import GetObjectMixin
from minone.models import MinOneDescription


class CompanySettings(LoginRequiredMixin, GetObjectMixin, DetailView):
    model = Company
    template_name = "settings/settings.html"

    def get_context_data(self, **kwargs):
        context = super(CompanySettings, self).get_context_data(**kwargs)
        context['accessToken'] = self.get_object().user.token
        context['company'] = context['object'] = self.get_object()
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['staffs'] = self.get_object().staffs.all()
        context['loanCount'] = self.get_object().loan_set.all().count()
        context['staffCount'] = self.get_object().staffs.all().count()
        context['borrowerCount'] = self.get_object().borrower_set.all().count()

        # loan packages owned - loan types owned by this firm
        owner = self.get_object().user
        context['company_loanType_packages'] = owner.user.profile.loantype_set.all()
        context['company_collection_packages'] = owner.user.profile.modeofrepayments_set.all()
        context['minone_obj'] = MinOneDescription.objects.first()
        context['user_thirdparty_cred'] = owner.thirdpartycreds
        return context

    def render_to_response(self, context, **response_kwargs):
        if context:
            user_profile_obj = Profile.objects.get(user=self.get_object().user.user)
            if timezone.now() > user_profile_obj.trial_days:
                # return redirect to payment page
                messages.error(self.request,
                               "Account Expired!, Your Account Has Been Expired You Would Be "
                               "Redirected To The Payment Portal Upgrade Your Payment")
                return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
            if self.request.user.is_authenticated:
                thisUser = str(self.get_object().user)
                currentUser = str(self.request.user)
                if thisUser != currentUser:
                    return reverse('404_')
                for pkg in context['company_loanType_packages']:
                    if timezone.now() > self.get_object().user.get_expiry():
                        pkg.bought_by.remove(self.get_object().user)
                for collection_pkg in context['company_collection_packages']:
                    if timezone.now() > self.get_object().user.get_expiry_collection_pkgs():
                        collection_pkg.bought_by.remove(self.get_object().user)
            else:
                return redirect(reverse('404_'))
        return super(CompanySettings, self).render_to_response(context, **response_kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.POST.get('actionType') == 'update':
            company = Company.objects.get(name__iexact=self.request.POST.get('company'))
            staff = company.staffs.get(keycode__exact=self.request.POST.get('keycode'))
            if self.request.POST.get('keycode') == str(self.get_object().user.keycode):
                return messages.warning(self.request,
                                        "Fraudulent Act!, Cannot change or remove company owner, If you are the company "
                                        "owner, contact minloans support")
            else:
                staff.role = self.request.POST.get('role')
                staff.save()
                return JsonResponse({'message': 'Staff Updated Successfully'}, status=204)
        elif self.request.POST.get('actionType') == 'delete':
            company = Company.objects.get(name__iexact=self.request.POST.get('company'))
            staff = company.staffs.get(keycode__exact=self.request.POST.get('keycode'))
            if self.request.POST.get('keycode') == str(self.get_object().user.keycode):
                return messages.warning(self.request,
                                        "Fraudulent Act!, Cannot change or remove company owner, If you are the company "
                                        "owner, contact minloans support")
            else:
                # remove firm from user
                staff.working_for.remove(company)
                # remove user from firm
                company.staffs.remove(staff)
            return JsonResponse({'message': 'Staff Removed Successfully'}, status=202)
