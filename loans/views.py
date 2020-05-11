from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import DetailView, ListView

from accounts.models import Profile
from borrowers.models import Borrower
from company.models import Company
from loans.models import Loan, LoanType
from minloansng.mixins import GetObjectMixin
from minloansng.utils import random_string_generator


class LoanCreateView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'loans/add-loan.html'

    def get_context_data(self, **kwargs):
        context = super(LoanCreateView, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['user_pkgs'] = self.request.user.profile.loantype_set.all()
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
        return super(LoanCreateView, self).render_to_response(context, **response_kwargs)

    def get_object(self, *args, **kwargs):
        slug = self.kwargs.get(self.slug_url_kwarg)
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

    def post(self, *args, **kwargs):
        number_of_repayment_fig = self.request.POST.get("repaymentIntervalFigure")
        number_of_repayment_period = self.request.POST.get("repaymentIntervalPeriod")
        repayment_span = "{figure} {period}".format(figure=number_of_repayment_fig, period=number_of_repayment_period)

        profile_inst = Profile.objects.get(user__exact=self.request.user)
        borrower_inst = Borrower.objects.get(slug__iexact=self.request.POST.get("borrower"))
        loan_inst = LoanType.objects.get(package__name__exact=self.request.POST.get("loanType"))

        Loan.objects.create(
            account_officer=profile_inst,
            company=self.get_object(),
            borrower=borrower_inst,
            loan_type=loan_inst,
            loan_key=random_string_generator(9),
            principal_amount=self.request.POST.get('amount'),
            interest=self.request.POST.get('interestFigure'),
            interest_period=self.request.POST.get('interestPeriod'),
            loan_duration_circle=self.request.POST.get('durationPeriod'),
            loan_duration_circle_figure=self.request.POST.get('durationFigure'),
            repayment_circle=self.request.POST.get('repaymentInterval'),
            number_repayments=repayment_span,
            release_date=self.request.POST.get('releaseDate'),
            processing_fee=self.request.POST.get('processingFee'),
            insurance=self.request.POST.get('insuranceFee'),
            balance_due='Calculate Balance Due Using Your Own Custom Loan Formula: Eg Armotisation Loan Formular',
            slug=slugify("{loanType}-{accountOfficer}-{primaryKey}".format(
                loanType=loan_inst, accountOfficer=profile_inst, primaryKey=random_string_generator(6)
            ))
        )
        return JsonResponse({'message': 'Submitted For Processing'})


class LoanListView(LoginRequiredMixin, ListView):
    queryset = Loan.objects.all()
    template_name = 'loans/list-loan.html'

    def get_context_data(self, *args, **kwargs):
        context = super(LoanListView, self).get_context_data(*args, **kwargs)
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        company_inst = Company.objects.get(slug=self.kwargs.get('slug'))
        context['company'] = context['object'] = company_inst
        context['open_loan_count'] = self.get_queryset().filter(loan_status__iexact='OPEN').count()
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
            staff_array = list()
            for user_obj in context.get('object').staffs.all():
                staff_array.append(str(user_obj))
            if self.request.user.email in staff_array or self.request.user.email == str(
                    context.get('object').user.user.email):
                pass
            else:
                redirect(reverse('404_'))
        return super(LoanListView, self).render_to_response(context, **response_kwargs)

    def get_queryset(self, *args, **kwargs):
        company_obj = Company.objects.get(slug=self.kwargs.get('slug'))
        qs = self.queryset.filter(company=company_obj)
        return qs


class LoanDetailView(LoginRequiredMixin, DetailView):
    model = Loan
    template_name = 'loans/detail-loan.html'

    def get_context_data(self, *args, **kwargs):
        print(args, kwargs)
        context = super(LoanDetailView, self).get_context_data(*args, **kwargs)
        company_inst = Company.objects.get(slug=self.kwargs.get('slug'))
        context['company'] = context['object'] = company_inst
        context['loan_obj'] = self.get_object()
        return context

    def render_to_response(self, context, **response_kwargs):
        print(context)
        if context:
            user_profile_obj = Profile.objects.get(user=self.request.user)
            if timezone.now() > user_profile_obj.trial_days:
                # return redirect to payment page
                messages.error(self.request,
                               "Account Expired!, Your Account Has Been Expired You Would Be "
                               "Redirected To The Payment Portal Upgrade Your Payment")
                return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
            staff_array = list()
            for user_obj in context.get('object').staffs.all():
                staff_array.append(str(user_obj))
            if self.request.user.email in staff_array or self.request.user.email == str(
                    context.get('object').user.user.email):
                pass
            else:
                redirect(reverse('404_'))
        return super(LoanDetailView, self).render_to_response(context, **response_kwargs)

    def get_object(self, *args, **kwargs):
        try:
            loan_obj = Loan.objects.get(slug=self.kwargs.get('loan_slug'))
        except Loan.DoesNotExist:
            return redirect(reverse("404_"))
        except Loan.MultipleObjectsReturned:
            loan_qs = Loan.objects.filter(slug=self.kwargs.get('loan_slug'))
            loan_obj = loan_qs.first()
        except:
            return redirect(reverse('404_'))
        return loan_obj
