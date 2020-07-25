from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import DetailView
from django.views.generic.base import View

from accounts.models import Profile
from company.models import Company, Branch
from mincore.models import Messages
from minloansng.mixins import GetObjectMixin
from minloansng.utils import random_string_generator

TRIAL_WARNING_DAYS = 5


class Dashboard(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.full_name and request.user.profile.phone:
                try:
                    company_obj = Company.objects.get(user=request.user.profile, slug=kwargs.get('slug'))
                    if company_obj.name:
                        user_profile_obj = Profile.objects.get(user=request.user)
                        user_plan = str(user_profile_obj.plan)
                        print(user_plan)
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
                                                messages.info(request, "Welcome, you are logged in as %s" %(request.user))
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
