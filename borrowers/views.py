from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, HttpResponseRedirect

# Create your views here.
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import date
from django.utils.text import slugify
from django.views.generic import DetailView, ListView, CreateView
from django_countries import countries
from django_countries.fields import Country

from accounts.models import Profile
from banks.models import BankCode
from borrowers.forms import BorrowerUpdateForm, BorrowerBankAccountForm
from borrowers.models import Borrower, BorrowerGroup, BorrowerBankAccount
from company.models import Company, BankAccountType
from minloansng.mixins import GetObjectMixin
from minloansng.utils import random_string_generator


class BorrowerCreateView(GetObjectMixin, LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'borrowers/add-borrower.html'

    def get_context_data(self, **kwargs):
        context = super(BorrowerCreateView, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.get_object().user.company_set.all()
        context['borrowers_qs'] = self.get_object().borrower_set.all()
        context['borrower_group_qs'] = self.get_object().borrowergroup_set.all()
        context['banks'] = BankCode.objects.all()
        context['country_qs'] = countries
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
        return super(BorrowerCreateView, self).render_to_response(context, **response_kwargs)

    def post(self, *args, **kwargs):
        bank_inst = BankCode.objects.get(name__exact=self.request.POST.get('bank'))
        country_inst = Country(code=self.request.POST.get('country'))
        print(country_inst, country_inst.name)
        Borrower.objects.create(
            registered_to=self.get_object(),
            first_name=self.request.POST.get('firstName'),
            last_name=self.request.POST.get('lastName'),
            gender=self.request.POST.get('gender'),
            address=self.request.POST.get('address'),
            lga=self.request.POST.get('lga'),
            state=self.request.POST.get('state'),
            country=country_inst,
            title=self.request.POST.get('title'),
            phone=self.request.POST.get('phone'),
            land_line=self.request.POST.get('landPhone'),
            business_name=self.request.POST.get('businessName'),
            working_status=self.request.POST.get('workingStatus'),
            email=self.request.POST.get('email'),
            unique_identifier=self.request.POST.get('unique_identifier'),
            bank=bank_inst,
            account_number=self.request.POST.get('accountNumber'),
            bvn=self.request.POST.get('bvn'),
            date_of_birth=self.request.POST.get('dateOfBirth'),
            slug=slugify("{firstName}-{lastName}-{company}-{primaryKey}".format(
                firstName=self.request.POST.get('firstName'), lastName=self.request.POST.get('lastName'),
                company=self.get_object(), primaryKey=random_string_generator(4)
            ))
        )
        return JsonResponse({'message': 'Account created successfully!'})


def calculate_age(born):
    if born:
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    return 0


class BorrowerUpdateView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'borrowers/detail-update-borrower.html'

    def get_context_data(self, **kwargs):
        context = super(BorrowerUpdateView, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.get_object().user.company_set.all()
        context['borrowers_qs'] = self.get_object().borrower_set.all()
        borrower_obj = Borrower.objects.get(slug=self.kwargs.get('slug_borrower'))
        context['borrower_loan_qs'] = self.get_object().loan_set.all().filter(borrower=borrower_obj)
        context['borrower_obj'] = borrower_obj
        context['form'] = BorrowerUpdateForm(self.request.POST or None, self.request.FILES or None,
                                             instance=borrower_obj)
        context['age'] = calculate_age(borrower_obj.date_of_birth)

        return context

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        try:
            company_obj = Company.objects.get(slug=slug)
        except Company.DoesNotExist:
            return redirect(reverse("404_"))
        except Company.MultipleObjectsReturned:
            company_qs = Company.objects.filter(slug=slug)
            company_obj = company_qs.first()
        except:
            return redirect(reverse('404_'))
        return company_obj

    def render_to_response(self, context, **response_kwargs):
        if context:
            user_profile_obj = Profile.objects.get(user=self.request.user)
            if timezone.now() > user_profile_obj.trial_days:
                # return redirect to payment page
                messages.error(self.request,
                               "Account Expired!, Your Account Has Been Expired You Would Be "
                               "Redirected To The Payment Portal Upgrade Your Payment")
                return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
            staff_array = [str(user_obj) for user_obj in self.get_object().staffs.all()]
            if (
                    self.request.user.email not in staff_array
                    and self.request.user.email
                    != str(self.get_object().user.user.email)
            ):
                redirect(reverse('404_'))
        return super(BorrowerUpdateView, self).render_to_response(context, **response_kwargs)

    def post(self, *args, **kwargs):
        borrower_obj = Borrower.objects.get(slug=self.kwargs.get('slug_borrower'))
        borrower_form = BorrowerUpdateForm(self.request.POST or None, self.request.FILES or None, instance=borrower_obj)
        if borrower_form.is_valid():
            borrower_form.save()
            return JsonResponse({'message': 'Borrower Account Updated Successfully'})
        return JsonResponse({'message': 'An error during submission!'})


class BorrowerGroupCreateView(GetObjectMixin, LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'borrowers/add-borrower-group.html'

    def get_context_data(self, **kwargs):
        context = super(BorrowerGroupCreateView, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.get_object().user.company_set.all()
        context['borrowers_qs'] = self.get_object().borrower_set.all()
        context['borrower_group_qs'] = self.get_object().borrowergroup_set.all()
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
        return super(BorrowerGroupCreateView, self).render_to_response(context, **response_kwargs)

    def post(self):
        return JsonResponse({'message': 'Submitted For Processing'})


class BorrowerListView(LoginRequiredMixin, ListView):
    template_name = 'borrowers/borrower-list.html'

    def get_queryset(self):
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        return company.borrower_set.all()

    def get_context_data(self, *args, **kwargs):
        context = super(BorrowerListView, self).get_context_data(*args, **kwargs)
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "object": company,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
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
        return super(BorrowerListView, self).render_to_response(context, **response_kwargs)


class BorrowerFromMonoListView(LoginRequiredMixin, ListView):
    template_name = 'borrowers/borrower-from-mono-list.html'

    def get_queryset(self):
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        return company.borrower_set.all()

    def get_context_data(self, *args, **kwargs):
        context = super(BorrowerFromMonoListView, self).get_context_data(*args, **kwargs)
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "object": company,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
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
        return super(BorrowerFromMonoListView, self).render_to_response(context, **response_kwargs)


class BorrowerDetailView(LoginRequiredMixin, DetailView):
    template_name = 'borrowers/borrower-detail.html'
    model = Company

    def get_context_data(self, **kwargs):
        context = super(BorrowerDetailView, self).get_context_data(**kwargs)
        borrower_obj = Borrower.objects.get(slug=self.kwargs.get('slug_borrower'))
        try:
            borrower_account = borrower_obj.registered_to.borrowerbankaccount_set.all().first()
        except Exception as e:
            borrower_account = 0.00
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "object": company,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs,
            "borrowers_qs": self.get_object().borrower_set.all(),
            "borrower_obj": borrower_obj,
            "borrower_acc": borrower_account
        })

        context['borrower_loan_qs'] = self.get_object().loan_set.all().filter(borrower=borrower_obj)
        context['age'] = calculate_age(borrower_obj.date_of_birth)

        return context

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get('slug')
        try:
            company_obj = Company.objects.get(slug=slug)
        except Company.DoesNotExist:
            return redirect(reverse("404_"))
        except Company.MultipleObjectsReturned:
            company_qs = Company.objects.filter(slug=slug)
            company_obj = company_qs.first()
        except:
            return redirect(reverse('404_'))
        return company_obj


class BorrowerGroupsListView(LoginRequiredMixin, ListView):
    template_name = 'borrowers/borrower-group-list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BorrowerGroupsListView, self).get_context_data(*args, **kwargs)
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        context['userCompany_qs'] = company.user.user.profile.company_set.all()
        context['object'] = context['company'] = company
        context['borrower_group_qs'] = self.get_queryset()
        for bg in self.get_queryset():
            # print(bg.borrowers.all(), bg.borrowers.get_queryset())
            for member in bg.borrowers.all():
                print(member.get_image)
        return context

    def render_to_response(self, context, **response_kwargs):
        if context:
            comp_owner_profile_expiry = context['object'].user.trial_days
            if timezone.now() > comp_owner_profile_expiry:
                # return redirect to payment page
                messages.error(self.request,
                               "Account Expired!, Organization Account Has Been Expired You Would Be "
                               "Redirected To The Payment Portal Upgrade Your Payment")
                return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
        return super(BorrowerGroupsListView, self).render_to_response(context, **response_kwargs)

    def get_queryset(self):
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        return company.borrowergroup_set.all()


class AssignBankAccountToBorrower(LoginRequiredMixin, DetailView):
    template_name = "borrowers/bank-account-create.html"
    model = Company

    def get_context_data(self, **kwargs):
        context = super(AssignBankAccountToBorrower, self).get_context_data(**kwargs)
        mfb_account_type_qs = BankAccountType.objects.filter(company=self.object)
        context.update({
            'userCompany_qs': self.object.user.company_set.all(),
            'borrowers_qs': self.object.borrower_set.all(),
            'account_type_qs': mfb_account_type_qs
        })
        return context

    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        borrower_obj = Borrower.objects.get(slug=self.request.POST.get('borrower'))
        bank_account_type = BankAccountType.objects.get(slug=self.request.POST.get('account_type'))
        BorrowerBankAccount.objects.create(
            company=self.get_object(),
            borrower=borrower_obj,
            account_type=bank_account_type,
            account_no=(
                    borrower_obj.id + settings.ACCOUNT_NUMBER_START_FROM
            ),
            balance=self.request.POST.get('balance'),
            interest_start_date=self.request.POST.get('interest_start_date'),
            initial_deposit_date=self.request.POST.get('initial_deposit_date')
        )
        return JsonResponse({'message': 'Activated Successfully!'})


class CustomerAccountList(LoginRequiredMixin, ListView):
    template_name = 'borrowers/borrower-account-list.html'

    def get_queryset(self):
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        return company.borrowerbankaccount_set.all()

    def get_context_data(self, *args, **kwargs):
        context = super(CustomerAccountList, self).get_context_data(*args, **kwargs)
        company = Company.objects.get(slug=self.kwargs.get('slug'))
        company_qs = company.user.user.profile.company_set.all()
        context.update({
            "object": company,
            "company": company,
            "company_owner": company.user.user,
            "userCompany_qs": company_qs
        })
        return context
