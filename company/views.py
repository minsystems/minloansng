from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import DetailView, ListView, UpdateView, DeleteView, CreateView
from django.views.generic.base import View

from accounts.models import Profile, ThirdPartyCreds
from company.forms import BankAccountTypeUpdateForm
from company.models import Company, Branch, BankAccountType
from mincore.models import Messages
from minloansng.mixins import GetObjectMixin, IsUserOwnerMixin
from minloansng.utils import random_string_generator

TRIAL_WARNING_DAYS = 5


class Dashboard(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.full_name and request.user.profile.phone:
                try:
                    company_obj = Company.objects.get(slug=kwargs.get('slug'))
                    if company_obj.name:
                        ThirdPartyCreds.objects.get_or_create(user=company_obj.user)
                        user_profile_obj = Profile.objects.get(user=company_obj.user.user)
                        user_plan = str(user_profile_obj.plan)
                        print(user_plan)
                        if company_obj.user.is_premium:
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
                                    if remaining_days == 7:
                                        messages.warning(request,
                                                         "You Have %s Days Left Before Account Suspension, Please Upgrade "
                                                         "Your Account" % (remaining_days.days))
                                    else:
                                        messages.info(request, "Welcome, you are logged in as %s" % (request.user))
                                    user_companies_qs = request.user.profile.company_set.all()
                                    company_msg = Messages.objects.all().filter(to_obj=company_obj)
                                    context = {
                                        'company': company_obj,
                                        'object': company_obj,
                                        'userCompany_qs': user_companies_qs,
                                        'msg': company_msg,
                                    }
                                    return render(request, "company/dashboard.html", context)
                            elif user_plan == "ENTERPRISE":
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
                            else:
                                return redirect(reverse('404_'))
                        elif user_plan == "FREEMIUM":
                            if timezone.now() > user_profile_obj.trial_days:
                                # return redirect to payment page
                                messages.error(request, "Account Expired!, Your Account Has Been Expired You Would Be "
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
                        else:
                            return redirect(reverse('404_'))
                    else:
                        return redirect(
                            reverse('company-url:update-company-profile', kwargs={'slug': company_obj.slug}))
                except Company.DoesNotExist:
                    print("You work here!")
                    target_comp = Company.objects.get(slug=kwargs.get('slug'))
                    company_array = list()
                    user_profile_obj = Profile.objects.get(user=request.user)
                    for company_inst in user_profile_obj.working_for.all():
                        company_array.append(str(company_inst))

                    for comp_ in company_array:
                        if comp_ == str(target_comp):
                            if target_comp.name:
                                user_plan = str(target_comp.user.plan)
                                print(user_plan)
                                if target_comp.user.is_premium:
                                    if user_plan == "STARTUP":
                                        if timezone.now() > target_comp.user.trial_days:
                                            # return redirect to payment page
                                            messages.error(request,
                                                           "Account Expired!, Your Account Has Been Expired You Would Be "
                                                           "Redirected To The Payment Portal Upgrade Your Payment")
                                            # jQuery Handles Redirect
                                            user_companies_qs = target_comp.user.user.profile.company_set.all()
                                            company_msg = Messages.objects.all().filter(to_obj=target_comp)
                                            context = {
                                                'company': target_comp,
                                                'object': target_comp,
                                                'userCompany_qs': user_companies_qs,
                                                'msg': company_msg,
                                            }
                                            return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
                                        else:
                                            remaining_days = target_comp.user.trial_days - timezone.now()
                                            messages.warning(request,
                                                             "You Have %s Days Left Before Account Suspension, Please Upgrade "
                                                             "Your Account" % (remaining_days.days))
                                            user_companies_qs = target_comp.user.user.profile.company_set.all()
                                            company_msg = Messages.objects.all().filter(to_obj=target_comp)
                                            context = {
                                                'company': target_comp,
                                                'object': target_comp,
                                                'userCompany_qs': user_companies_qs,
                                                'msg': company_msg,
                                            }
                                            return render(request, "company/dashboard.html", context)
                                    elif user_plan == "BUSINESS":
                                        if timezone.now() > target_comp.user.trial_days:
                                            # return redirect to payment page
                                            messages.error(request,
                                                           "Account Expired!, Your Account Has Been Expired You Would Be "
                                                           "Redirected To The Payment Portal Upgrade Your Payment")
                                            # jQuery Handles Redirect
                                            user_companies_qs = target_comp.user.user.profile.company_set.all()
                                            company_msg = Messages.objects.all().filter(to_obj=target_comp)
                                            context = {
                                                'company': target_comp,
                                                'object': target_comp,
                                                'userCompany_qs': user_companies_qs,
                                                'msg': company_msg,
                                            }
                                            return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
                                        else:
                                            remaining_days = target_comp.user.trial_days - timezone.now()
                                            if remaining_days == 5:
                                                messages.warning(request,
                                                                 "You Have %s Days Left Before Account Suspension, Please Upgrade "
                                                                 "Your Account" % (remaining_days.days))
                                            else:
                                                messages.info(request,
                                                              "Welcome, you are logged in as %s" % (request.user))
                                            user_companies_qs = target_comp.user.user.profile.company_set.all()
                                            company_msg = Messages.objects.all().filter(to_obj=target_comp)
                                            context = {
                                                'company': target_comp,
                                                'object': target_comp,
                                                'userCompany_qs': user_companies_qs,
                                                'msg': company_msg,
                                            }
                                            return render(request, "company/dashboard.html", context)
                                    elif user_plan == "ENTERPRISE":
                                        print("ENTERPRISE")
                                    else:
                                        return redirect(reverse('404_'))
                                elif user_plan == "FREEMIUM":
                                    if timezone.now() > target_comp.user.trial_days:
                                        # return redirect to payment page
                                        messages.error(request,
                                                       "Account Expired!, Your Account Has Been Expired You Would Be "
                                                       "Redirected To The Payment Portal Upgrade Your Payment")
                                        # jQuery Handles Redirect
                                        user_companies_qs = target_comp.user.user.profile.company_set.all()
                                        company_msg = Messages.objects.all().filter(to_obj=target_comp)
                                        context = {
                                            'company': target_comp,
                                            'object': target_comp,
                                            'userCompany_qs': user_companies_qs,
                                            'msg': company_msg,
                                        }
                                        return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
                                    else:
                                        remaining_days = target_comp.user.trial_days - timezone.now()
                                        messages.warning(request,
                                                         "You Have %s Days Left Before Account Suspension, Please Upgrade "
                                                         "Your Account" % (remaining_days.days))
                                        user_companies_qs = target_comp.user.user.profile.company_set.all()
                                        company_msg = Messages.objects.all().filter(to_obj=target_comp)
                                        context = {
                                            'company': target_comp,
                                            'object': target_comp,
                                            'userCompany_qs': user_companies_qs,
                                            'msg': company_msg,
                                        }
                                        return render(request, "company/dashboard.html", context)
                                else:
                                    return redirect(reverse('404_'))
                            else:
                                return redirect(reverse('404_'))
                            return render(request, "company/dashboard.html", context)
                        else:
                            redirect(reverse('404_'))
                    return reverse('404_')
            else:
                return redirect(reverse('account:user-update'))
        else:
            # when user currentUser is not authenticated!
            try:
                company_obj = Company.objects.get(slug=kwargs.get('slug'))
                if company_obj.user.plan == "BUSINESS":
                    print("Have A Custom Homepage Without URL Masking")
                    return render(request, "company/public-home.html", context={})
                elif company_obj.user.plan == "ENTERPRISE":
                    print("Have A Custom Homepage With URL Masking")
                    return render(request, "company/public-home.html", context={})
                elif company_obj.user.plan == "FREEMIUM":
                    print("No Custom Homepage For Freemium Users")
                    return redirect(reverse('404_'))
            except Company.DoesNotExist:
                return redirect(reverse('404_'))
            except Company.MultipleObjectsReturned:
                company_qs = Company.objects.filter(slug=kwargs.get('slug'))
                company_obj = company_qs.first()

                if company_obj.user.plan == "BUSINESS":
                    print("Have A Custom Homepage Without URL Masking")
                    return render(request, "company/public-home.html", context={})
                elif company_obj.user.plan == "ENTERPRISE":
                    print("Have A Custom Homepage With URL Masking")
                    return render(request, "company/public-home.html", context={})
                elif company_obj.user.plan == "FREEMIUM":
                    print("No Custom Homepage For Freemium Users")
                    return redirect(reverse('404_'))


class UpdateCompanyProfileView(GetObjectMixin, DetailView):
    model = Company

    def get_context_data(self, **kwargs):
        context = super(UpdateCompanyProfileView, self).get_context_data(**kwargs)
        return context

    def render_to_response(self, context, **response_kwargs):
        if context:
            user_profile_obj = Profile.objects.get(user=self.request.user)
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
                else:
                    if self.get_object().name:
                        messages.warning(self.request,
                                         "You Can Only Access This Page Once!")  # jQuery handles redirect after this
                    else:
                        if self.get_object().user.phone is None:
                            print("Redirect To Profile Update!")
                        else:
                            messages.info(self.request,
                                          "Update Company Information")  # jQuery lets you update this information
            else:
                return redirect(reverse('404_'))
        return super(UpdateCompanyProfileView, self).render_to_response(context, **response_kwargs)

    def post(self, request, *args, **kwargs):
        branch_instance = Branch.objects.create(
            branch_custom=request.POST['branchCode'],
            address=request.POST['branchAddress'],
            slug=random_string_generator()
        )

        company_instance = self.get_object()
        company_instance.name = request.POST['companyName']
        if request.POST['companyEmail']:
            company_instance.email = request.POST['companyEmail']
        else:
            company_instance.email = self.get_object().user.user.email  # .user.user.email
        company_instance.branch = branch_instance
        company_instance.slug = "{name}-{randstr}".format(name=slugify(request.POST['companyName']),
                                                          randstr=random_string_generator(size=4))
        company_instance.save()

        payload = {"success": True}
        return JsonResponse(payload)


class CompanyAccountTypesList(LoginRequiredMixin, ListView):
    template_name = 'company/account_type.html'
    model = BankAccountType

    def get_queryset(self):
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        account_types_qs = self.model.objects.filter(company=company)
        return account_types_qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CompanyAccountTypesList, self).get_context_data(**kwargs)
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "object": company,
            "company": company,
            "account_type_list": self.get_queryset(),
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
        return context


class CompanyAccountTypeDetails(LoginRequiredMixin, DetailView):
    template_name = 'company/account_type_detail.html'
    model = BankAccountType

    def get_context_data(self, **kwargs):
        context = super(CompanyAccountTypeDetails, self).get_context_data(**kwargs)
        print(self.kwargs)
        company = Company.objects.get(slug=self.kwargs.get('company_slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "object": company,
            "object_detail": self.object,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
        return context


class CompanyAccountTypeUpdate(IsUserOwnerMixin, SuccessMessageMixin, UpdateView):
    template_name = 'company/account_type_update.html'
    model = BankAccountType
    form_class = BankAccountTypeUpdateForm
    success_message = "Account Type Was Updated Successfully!"

    def get_context_data(self, **kwargs):
        context = super(CompanyAccountTypeUpdate, self).get_context_data(**kwargs)
        company = Company.objects.get(slug=self.kwargs.get('company_slug'))
        company_qs = company.user.user.profile.company_set.all()
        account_type_obj = BankAccountType.objects.get(company=company, slug=self.kwargs.get('slug'))
        context.update({
            "form": self.form_class(instance=account_type_obj),
            "object": company,
            "object_detail": self.object,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
        return context


class CompanyAccountTypeDelete(IsUserOwnerMixin, SuccessMessageMixin, DeleteView):
    model = BankAccountType
    template_name = 'company/account_type_delete.html'
    success_message = "Account Type Deleted Successfully!"

    def get_success_url(self):
        return reverse("company-url:bank-account-type", kwargs={"slug": self.kwargs.get('company_slug')})

    def get_context_data(self, **kwargs):
        context = super(CompanyAccountTypeDelete, self).get_context_data(**kwargs)
        company = Company.objects.get(slug=self.kwargs.get('company_slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "object": company,
            "object_detail": self.object,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(CompanyAccountTypeDelete, self).delete(request, *args, **kwargs)


class CompanyAccountCreateForm(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = "company/account_create.html"
    model = BankAccountType
    success_message = "Bank Account For MFB Organization Was Created Successfully"
    form_class = BankAccountTypeUpdateForm

    def get_success_url(self):
        return reverse("company-url:bank-account-type", kwargs={"slug": self.kwargs.get('company_slug')})

    def get_context_data(self, **kwargs):
        context = super(CompanyAccountCreateForm, self).get_context_data(**kwargs)
        company = Company.objects.get(slug=self.kwargs.get('company_slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "form": self.form_class(self.request.POST),
            "object": company,
            "object_detail": self.object,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(CompanyAccountCreateForm, self).get_form_kwargs()
        print(kwargs)
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        company = Company.objects.get(slug=self.kwargs.get('company_slug'))
        self.object.company = company
        self.object.save()
        return super(CompanyAccountCreateForm, self).form_valid(form)

