import json

from datetime import timedelta

import math
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.utils import timezone
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.views.generic.base import View
from rest_framework import status

from accounts.models import Profile, User
from banks.models import BankCode
from borrowers.models import Borrower
from company.models import Company, RemitaCredentials, RemitaMandateActivationData, RemitaMandateTransactionRecord, \
    RemitaPaymentDetails, RemitaMandateStatusReport
from loans.forms import CollateralForm, LoanFileForm
from loans.models import Loan, LoanType, ModeOfRepayments, Penalty, Collateral, LoanTerms, CollateralFiles, \
    CollateralType, LoanActivityComments
from minloansng.cloudinary_settings import cloudinary_upload_preset, cloudinary_url
from minloansng.minmarket.packages.remita import remita_dd_url, statuscode_success
from minloansng.mixins import GetObjectMixin
from minloansng.utils import random_string_generator, secondWordExtract, digitExtract, addDays, get_fileType, \
    armotizationLoanCalculator, removeNCharFromString

DESCRIPTION = "If a loan payment is due " \
              "and is not paid within the specified time constraints, " \
              "the payment will be considered past due. Late fees are " \
              "one of the most expensive penalties that can occur for a " \
              "past due bill. Lenders can charge anywhere from NGN500 to NGN1,000 for a late payment"


class LoanCreateView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'loans/add-loan.html'

    def get_context_data(self, **kwargs):
        context = super(LoanCreateView, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['user_pkgs'] = self.request.user.profile.loantype_set.all()
        context['user_collection_pkgs'] = self.request.user.profile.modeofrepayments_set.all()
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
        loan_key_value = random_string_generator(9)

        profile_inst = Profile.objects.get(user__exact=self.request.user)
        borrower_inst = Borrower.objects.get(slug__iexact=self.request.POST.get("borrower"))
        loan_inst = LoanType.objects.get(package__name__exact=self.request.POST.get("loanType"))
        loan_collection_type = ModeOfRepayments.objects.get(
            package__name__exact=self.request.POST.get("loanCollectionType"))

        release_date = datetime.strptime(self.request.POST.get('releaseDate'), '%Y-%m-%d')

        loan_slug = slugify("{loanType}-{accountOfficer}-{primaryKey}".format(
            loanType=loan_inst, accountOfficer=profile_inst, primaryKey=random_string_generator(6)
        ))

        if secondWordExtract(repayment_span) == "Months":
            collection_date = release_date + relativedelta(months=1)
            end_date = release_date + relativedelta(months=int(digitExtract(repayment_span)))
            print(release_date, collection_date, end_date)
        elif secondWordExtract(repayment_span) == "Years":
            collection_date = release_date + relativedelta(years=1)
            end_date = release_date + relativedelta(years=int(digitExtract(repayment_span)))
        elif secondWordExtract(repayment_span) == "Weeks":
            collection_date = release_date + relativedelta(weeks=1)
            end_date = release_date + relativedelta(weeks=int(digitExtract(repayment_span)))
        else:
            collection_date = release_date + relativedelta(days=1)
            end_date = release_date + relativedelta(days=int(digitExtract(repayment_span)))

        Loan.objects.create(
            account_officer=profile_inst,
            company=self.get_object(),
            borrower=borrower_inst,
            loan_type=loan_inst,
            loan_key=loan_key_value,
            principal_amount=self.request.POST.get('amount'),
            interest=self.request.POST.get('interestFigure'),
            interest_period=self.request.POST.get('interestPeriod'),
            loan_duration_circle=self.request.POST.get('durationPeriod'),
            loan_duration_circle_figure=self.request.POST.get('durationFigure'),
            repayment_circle=self.request.POST.get('repaymentInterval'),
            number_repayments=repayment_span,
            collection_date=collection_date,
            release_date=release_date,
            end_date=end_date,
            processing_fee=self.request.POST.get('processingFee'),
            insurance=self.request.POST.get('insuranceFee'),
            balance_due="Modify/Change Loan",
            mode_of_repayments=loan_collection_type,
            slug=loan_slug,
        )

        base_url = getattr(settings, 'BASE_URL', 'https://www.minloans.com.ng')

        if str(loan_collection_type) == "Remita Direct Debit":
            urlpath = reverse('loans-url:loan-standing-order-create',
                              kwargs={'slug': self.get_object().slug, 'loan_slug': loan_slug,
                                      'loan_key': loan_key_value})
            finalpath = "{base}{path}".format(base=base_url, path=urlpath)
            print(finalpath)
            loan_data = {'companySlug': self.get_object().slug, 'loanSlug': loan_slug, 'loanKey': loan_key_value}
        elif str(loan_collection_type) == "Data Referencing":
            urlpath = ""
            finalpath = ""
            loan_data = ""
        elif str(loan_collection_type) == "Quick Loans":
            urlpath = ""
            finalpath = ""
            loan_data = ""
        return JsonResponse({'message': 'Submitted For Processing', 'urlpath': finalpath, 'loanKey': loan_key_value,
                             'loan_data': loan_data})


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
        context = super(LoanDetailView, self).get_context_data(*args, **kwargs)
        company_inst = Company.objects.get(slug=self.kwargs.get('slug'))
        context['accessToken'] = company_inst.user.token
        context['company'] = context['object'] = company_inst
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['loan_obj'] = self.get_object()
        context['penalty'] = self.get_object().penalty
        if timezone.now() >= self.get_object().end_date:
            context['overdue'] = "active"
        else:
            context['overdue'] = 'notActive'
        context['installment_repayment'] = armotizationLoanCalculator(self.get_object().principal_amount, self.get_object().interest, self.get_object().number_repayments)
        context['loan_comment_qs'] = LoanActivityComments.objects.filter(loan=self.get_object())
        context['form'] = LoanFileForm()
        if self.get_object().loan_file_upload is not None:
            file_type = get_fileType(self.get_object().loan_file_upload.url)
            context['fileType'] = str(file_type)
        if str(self.get_object().mode_of_repayments) == "Remita Direct Debit":
            context['dd_obj'] = RemitaMandateActivationData.objects.get(loan_key=self.get_object())
            context['loanActions'] = 'DD'
            requestId_obj = company_inst.remitamandateactivationdata_set.all().get(loan_key=self.get_object())
            context['requestId'] = company_inst.remitamandateactivationdata_set.all().get(loan_key=self.get_object())
            context['loanMandateId'] = requestId_obj.mandateId
            context['company_dd_creds'] = company_inst.user.thirdpartycreds
            borrowerBank = BankCode.objects.get(code__exact=requestId_obj.payer_bank_code)
            context['account_number'] = self.get_object().borrower.account_number
            try:
                mandateTransactionRecord = RemitaMandateTransactionRecord.objects.get(loan=self.get_object())
                paymentDetails = RemitaPaymentDetails.objects.filter(loan=self.get_object())
                context['mandateTransactionRecord'] = mandateTransactionRecord
                context['paymentDetails'] = paymentDetails
                amountArray = []
                for amountValue in paymentDetails:
                    amountArray.append(amountValue.amount)
                context['amountArray'] = amountArray
            except RemitaMandateTransactionRecord.DoesNotExist:
                context['mandateTransactionRecord'] = "No mandate Transaction Record Found"
                context['paymentDetails'] = "No Payment Record For This Transactiom"
                amountArray = []
                context['amountArray'] = amountArray
            if borrowerBank.otp_enabled:
                context['otpCheck'] = 1
            else:
                context['otpCheck'] = 0
            try:
                context['dd_status_report'] = RemitaMandateStatusReport.objects.get(loan=self.get_object())
            except RemitaMandateStatusReport.DoesNotExist:
                context['dd_status_report'] = None
        else:
            context['dd_obj'] = RemitaMandateActivationData.objects.get(loan_key=self.get_object())
            context['company_creds'] = RemitaCredentials.objects.get(connected_firm=company_inst)
            context['loanActions'] = 'OD'
        return context

    def render_to_response(self, context, **response_kwargs):
        if context:
            print(context)
            """
            check if loan is overdue, check should happen anytime this view is opened
            """
            if timezone.now() >= self.get_object().end_date:
                messages.warning(
                    self.request,
                    "The loan %s has been overdue and system is scheduled to calculate penalty on current loan" % self.get_object().loan_key
                )

                # get grace period
                grace_period = int(self.get_object().grace_period)

                overdue_period = timezone.now() - self.get_object().end_date
                total_overdue_period = overdue_period - timedelta(days=grace_period)

                penalty_increment_period = self.get_object().penalty.period
                if penalty_increment_period == "Per Week":
                    week_delta = timedelta(days=7)
                    value_data = total_overdue_period/week_delta
                    period_gone = math.trunc(value_data)
                    if period_gone > 0:
                        # add basefee to balance and multiply period fee with period gone and add all together
                        baseFee = int(context['penalty'].punishment_fee)
                        balanceFee = str(digitExtract(context['loan_obj'].balance_due))
                        balanceFee = removeNCharFromString(2, balanceFee)
                        balanceFee = int(balanceFee)
                        print(balanceFee)
                        periodFee = int(context['penalty'].value_on_period)
                        loan_ = Loan.objects.get(loan_key=context['loan_obj'])
                        loan_.balance_due = (balanceFee + baseFee) + (periodFee * period_gone)
                        loan_.save()
                elif penalty_increment_period == "Per Day":
                    week_delta = timedelta(days=1)
                    value_data = total_overdue_period / week_delta
                    period_gone = math.trunc(value_data)
                    if period_gone > 0:
                        # add basefee to balance and multiply period fee with period gone and add all together
                        baseFee = int(context['penalty'].punishment_fee)
                        balanceFee = str(digitExtract(context['loan_obj'].balance_due))
                        balanceFee = removeNCharFromString(2, balanceFee)
                        balanceFee = int(balanceFee)
                        print(balanceFee)
                        periodFee = int(context['penalty'].value_on_period)
                        loan_ = Loan.objects.get(loan_key=context['loan_obj'])
                        loan_.balance_due = (balanceFee + baseFee) + (periodFee * period_gone)
                        loan_.save()
                elif penalty_increment_period == "Per Month":
                    week_delta = timedelta(days=30)
                    value_data = total_overdue_period / week_delta
                    period_gone = math.trunc(value_data)
                    if period_gone > 0:
                        # add basefee to balance and multiply period fee with period gone and add all together
                        baseFee = int(context['penalty'].punishment_fee)
                        balanceFee = str(digitExtract(context['loan_obj'].balance_due))
                        balanceFee = removeNCharFromString(2, balanceFee)
                        balanceFee = int(balanceFee)
                        print(balanceFee)
                        periodFee = int(context['penalty'].value_on_period)
                        loan_ = Loan.objects.get(loan_key=context['loan_obj'])
                        loan_.balance_due = (balanceFee + baseFee) + (periodFee * period_gone)
                        loan_.save()
                elif penalty_increment_period == "Per Year":
                    week_delta = timedelta(days=365)
                    value_data = total_overdue_period / week_delta
                    period_gone = math.trunc(value_data)
                    if period_gone > 0:
                        # add basefee to balance and multiply period fee with period gone and add all together
                        baseFee = int(context['penalty'].punishment_fee)
                        balanceFee = str(digitExtract(context['loan_obj'].balance_due))
                        balanceFee = removeNCharFromString(2, balanceFee)
                        balanceFee = int(balanceFee)
                        print(balanceFee)
                        periodFee = int(context['penalty'].value_on_period)
                        loan_ = Loan.objects.get(loan_key=context['loan_obj'])
                        loan_.balance_due = (balanceFee + baseFee) + (periodFee * period_gone)
                        loan_.save()
                else:
                    pass

            CollateralType.objects.get_or_create(owned=self.get_object())
            if self.get_object().balance_due == "Modify/Change Loan":
                thisArmortizedValue = armotizationLoanCalculator(
                    self.get_object().principal_amount,
                    self.get_object().interest,
                    self.get_object().number_repayments
                )
                newloanInstance = Loan.objects.get(loan_key=self.get_object())
                newloanInstance.balance_due = int(thisArmortizedValue) * int(self.get_object().number_repayments)
                newloanInstance.save()
            if self.get_object().penalty is None:
                loan_penalty = Penalty.objects.get(title__exact=self.get_object().loan_key)
                loan_penalty.company = context.get('company')
                loan_penalty.describe = DESCRIPTION
                loan_penalty.punishment_fee = 500
                loan_penalty.re_occuring = True
                loan_penalty.value_on_period = 500
                loan_penalty.period = "Per Week"
                loan_penalty.save()
                instance = Loan.objects.get(loan_key=self.get_object())
                instance.penalty = loan_penalty
                instance.save()
            if self.get_object().collateral is None:
                loan_collateral = Collateral.objects.get(slug=self.get_object().loan_key)
                instance = Loan.objects.get(loan_key=self.get_object())
                instance.collateral = loan_collateral
                instance.save()
            if self.get_object().loan_terms is None:
                loan_tc = LoanTerms.objects.get(title__exact=self.get_object().loan_key)
                instance = Loan.objects.get(loan_key=self.get_object())
                instance.loan_terms = loan_tc
                instance.save()
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

    def post(self, *args, **kwargs):
        instance = self.get_object()
        form = LoanFileForm(self.request.POST or None, self.request.FILES or None, instance=instance)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Loan File Uploaded Successfully!'})
        return JsonResponse({'message': 'form Invalid'})


class LoanCollateralDetail(LoginRequiredMixin, DetailView):
    model = Loan
    template_name = 'loans/detail-loan-collateral.html'

    def get_context_data(self, *args, **kwargs):
        context = super(LoanCollateralDetail, self).get_context_data(*args, **kwargs)
        company_inst = Company.objects.get(slug=self.kwargs.get('slug'))
        context['company'] = context['object'] = company_inst
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['loan_obj'] = self.get_object()
        context['cloudinary_upload_preset'] = cloudinary_upload_preset
        context['cloudinary_url'] = cloudinary_url
        context['form'] = CollateralForm()
        c_file = CollateralFiles.objects.get_or_create(token=self.get_object().loan_key)
        print(type(c_file))  # returns a tuple (instance, boolean)
        c_file_instance, c_file_bool = c_file
        if c_file_instance.file_url is not None:
            file_type = get_fileType(c_file_instance.file_url)
            context['fileType'] = str(file_type)
        if c_file_bool is False:
            # already existing and not created
            context['collateral_file_url'] = c_file_instance.file_url
        else:
            context['collateral_file_url'] = c_file.file_url
        if self.get_object().mode_of_repayments == "Remita Direct Debit":
            context['dd_obj'] = RemitaMandateActivationData.objects.get(loan_key=self.get_object())
            context['company_creds'] = RemitaCredentials.objects.get(connected_firm=company_inst)
        else:
            context['dd_obj'] = RemitaMandateActivationData.objects.get(loan_key=self.get_object())
            context['company_creds'] = RemitaCredentials.objects.get(connected_firm=company_inst)
        return context

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

    @csrf_exempt
    def post(self, *args, **kwargs):
        imgUrl = self.request.POST.get("imageUrl")
        file_inst = CollateralFiles.objects.get(token=self.get_object().loan_key)
        file_inst.file_url = imgUrl
        file_inst.save()
        return JsonResponse({'message': 'Image Processing Complete..'})


class CollateralFormProcessor(View):
    def post(self, request, *args, **kwargs):
        print(self.request.POST)
        loanInstance = Loan.objects.get(loan_key=self.request.POST.get('collateralToken'))
        collateral_type_instance = CollateralType.objects.get(owned=loanInstance)
        collateral_file_instance = CollateralFiles.objects.get(token=self.request.POST.get('collateralToken'))
        collateral_obj = Collateral.objects.get(slug=self.request.POST.get('collateralToken'))
        collateral_obj.collateral_type = collateral_type_instance
        collateral_obj.name = self.request.POST.get('collateralName')
        collateral_obj.registered_date = self.request.POST.get('collateralRegisteredDate')
        collateral_obj.registered_time = self.request.POST.get('collateralTime')
        collateral_obj.status = self.request.POST.get('collateralStatus')
        collateral_obj.value = self.request.POST.get('collateralValue')
        collateral_obj.condition = self.request.POST.get('collateralCondition')
        collateral_obj.view_shader = self.request.POST.get('collateralViewShade')
        collateral_obj.description = self.request.POST.get('collateralDescription')
        collateral_obj.collateral_files = collateral_file_instance
        collateral_obj.save()
        return JsonResponse({'message': 'Data Successfully Saved!'})


class LoanDetailAutoSaveProcessor(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoanDetailAutoSaveProcessor, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            print(self.request.POST, request, *args, **kwargs)
            loan_instance = Loan.objects.get(loan_key__iexact=self.request.POST.get('loanInstance'))
            loan_instance.description = self.request.POST.get('description')
            loan_instance.save()
            return JsonResponse({'message': 'Updated!'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Ajax Method Required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LoanRepaymentProcessor(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoanRepaymentProcessor, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            loan_obj = Loan.objects.get(loan_key__iexact=self.request.POST.get('loanInstance'))
            loan_obj.balance_due = self.request.POST.get('balanceDue')
            loan_obj.save()
            return JsonResponse({'message': 'Repayment Balance Has Been Updated Successfully!'},
                                status=status.HTTP_201_CREATED)
        return JsonResponse({'message': 'Ajax Method Required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LoanStatusChangeProcessor(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoanStatusChangeProcessor, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            loan_obj = Loan.objects.get(loan_key__iexact=self.request.POST.get('loanInstance'))
            loan_obj.loan_status = self.request.POST.get('status')
            loan_obj.save()
            return JsonResponse({'message': 'Loan Status Has Been Updated Successfully!'},
                                status=status.HTTP_201_CREATED)
        return JsonResponse({'message': 'Ajax Method Required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LoanCommentProcessor(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoanCommentProcessor, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            loan_instance = Loan.objects.get(loan_key__iexact=self.request.POST.get('loanInstance'))
            userAssigned = User.objects.get(email__exact=self.request.POST.get('assignedTo'))
            doneBy = Profile.objects.get(user=self.request.user)
            assigned_user = Profile.objects.get(user=userAssigned)
            LoanActivityComments.objects.create(
                assigned_to=assigned_user,
                done_by=doneBy,
                loan=loan_instance,
                comment=self.request.POST.get('taskContent')
            )
            return JsonResponse({'message': 'Updated!'}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Ajax Method Required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LoanPenaltyRepayment(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoanPenaltyRepayment, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax():
            print(self.request.POST)
            loan_instance = Loan.objects.get(loan_key__iexact=self.request.POST.get('linked_loan'))
            company_obj = loan_instance.company
            loan_penalty = Penalty.objects.get(company=company_obj, title__exact=loan_instance)
            loan_penalty.punishment_fee = self.request.POST.get('baseFee')
            loan_penalty.value_on_period = self.request.POST.get('continuousFee')
            loan_penalty.period = self.request.POST.get('reoccurringPeriod')
            loan_penalty.linked_loan = loan_instance
            loan_penalty.save()
            return JsonResponse({'message': 'Updated For User Loan! %s' % loan_instance}, status=status.HTTP_200_OK)
        return JsonResponse({'message': 'Ajax Method Required'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class RemitaStandingOrder(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'loans/remita/standing-order/setupmandate.html'

    def get_context_data(self, **kwargs):
        print(self.query_pk_and_slug, self.slug_url_kwarg)
        print(self.kwargs)
        context = super(RemitaStandingOrder, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['user_pkgs'] = self.request.user.profile.loantype_set.all()
        context['user_collection_pkgs'] = self.request.user.profile.modeofrepayments_set.all()
        context['borrowers_qs'] = self.get_object().borrower_set.all()
        context['borrower_group_qs'] = self.get_object().borrowergroup_set.all()

        context['loan_key'] = self.kwargs.get('loan_key')

        # get the user and their account number from the loankey
        loan_obj = Loan.objects.get(loan_key__iexact=self.kwargs.get('loan_key'))
        context['loan_obj'] = loan_obj

        context['collection_date'] = loan_obj.collection_date
        context['num_of_repayments'] = digitExtract(loan_obj.number_repayments)
        context['borrower'] = loan_obj.borrower

        context['remitaCredential_obj'] = RemitaCredentials.objects.get(connected_firm=self.get_object())
        context['dd_url'] = remita_dd_url

        return context

    def render_to_response(self, context, **response_kwargs):
        print(context, **response_kwargs)
        if context:
            user_profile_obj = Profile.objects.get(user=self.request.user)
            if timezone.now() > user_profile_obj.trial_days:
                # return redirect to payment page
                messages.error(self.request,
                               "Account Expired!, Your Account Has Been Expired You Would Be "
                               "Redirected To The Payment Portal Upgrade Your Payment")
                return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
            try:
                loan_obj_remita_dd = RemitaMandateActivationData.objects.get(
                    loan_key__iexact=self.kwargs.get('loan_key'))
                if loan_obj_remita_dd:
                    messages.error(self.request, "Mandate Has Been Activated On This Loan Already!")
                    return HttpResponseRedirect(reverse("mincore-url:account-upgrade"))
                else:
                    messages.warning(self.request, "Mandate Activation Can Only Be Done Once On A Loan Instance")
            except:
                messages.warning(self.request, "Mandate Activation Can Only Be Done Once On A Loan Instance")

        return super(RemitaStandingOrder, self).render_to_response(context, **response_kwargs)

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
        try:
            payer_obj = Borrower.objects.get(phone__exact=self.request.POST.get("payerPhone"))
        except Borrower.DoesNotExist:
            return JsonResponse({'message': 'Borrower Does Not Exist!'}, status=status.HTTP_404_NOT_FOUND)
        except Borrower.MultipleObjectsReturned:
            payer_qs = Borrower.objects.filter(phone__exact=self.request.POST.get("payerPhone"))
            payer_obj = payer_qs.last()

        payerName = payer_obj.get_borrowers_full_name()
        payerEmail = Borrower.objects.get(email__exact=self.request.POST.get("payerEmail")).email
        payerBankCode = BankCode.objects.get(code__exact=self.request.POST.get("payerBankCode")).code
        loan_instance = Loan.objects.get(loan_key__iexact=self.request.POST.get("loanKey"))
        loanKey = loan_instance.loan_key

        RemitaMandateActivationData.objects.create(
            connected_firm=self.get_object(),
            amount=self.request.POST.get("amount"),
            start_date=self.request.POST.get("startDate"),
            end_date=self.request.POST.get("endDate"),
            max_number_of_debits=self.request.POST.get("maxNoOfDebits"),
            mandate_type=self.request.POST.get("mandateType"),
            payer_account=self.request.POST.get("payerAccount"),
            payer_bank_code=payerBankCode,
            payer_name=payerName,
            payer_email=payerEmail,
            payer_phone=self.request.POST.get("payerPhone"),
            requestId=self.request.POST.get("requestId"),
            merchantId=self.request.POST.get("merchantId"),
            mandate_requestId=self.request.POST.get("requestId"),
            hash_key=self.request.POST.get("hash"),
            serviceTypeId=self.request.POST.get("serviceTypeId"),
            loan_key=loan_instance,
        )

        # update the date of the loan date
        loan_instance.number_repayments = self.request.POST.get("maxNoOfDebits")
        loan_instance.release_date = datetime.strptime(self.request.POST.get('startDate'), "%d/%m/%Y")
        loan_instance.end_date = datetime.strptime(self.request.POST.get("endDate"), "%d/%m/%Y")
        loan_instance.save()

        return JsonResponse({'message': 'Submitted To DB, Processing to Remita Server..'},
                            status=status.HTTP_200_OK)


class RemitaMandateUpdate(View):
    def post(self, *args, **kwargs):
        if self.request.POST['statuscode'] == statuscode_success:
            mandate_dd = RemitaMandateActivationData.objects.get(requestId=self.request.POST['requestId'])
            mandate_dd.status = self.request.POST['status']
            mandate_dd.statuscode = self.request.POST['statuscode']
            mandate_dd.mandateId = self.request.POST['mandateId']
            mandate_dd.save()
            return JsonResponse({'message': 'Mandate Activation Updated!', 'status': '007'})
        return JsonResponse({'message': 'Mandate Failed To Update Please Redo Process', 'status': '003'})


class RemitaTransRefUpdate(View):
    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            data = self.request.body.decode("utf-8")
            payload = json.loads(data)
            print(type(payload), payload['loan_key'], payload['remitaTransRef'])
            loanInstance = Loan.objects.get(loan_key=payload['loan_key'])
            mandate_dd = RemitaMandateActivationData.objects.get(loan_key=loanInstance)
            mandate_dd.remitaTransRef = payload['remitaTransRef']
            mandate_dd.save()
            return JsonResponse({'message': 'Transaction Reference Has Been Updated!'}, status=201)
        return JsonResponse({'message': 'Method Not Allowed'}, status=501)


class RRRandTransactionRef(View):
    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            data = self.request.body.decode("utf-8")
            payload = json.loads(data)
            print(payload)
            loanInstance = Loan.objects.get(loan_key=payload['loan_key'])
            mandate_dd = RemitaMandateActivationData.objects.get(loan_key=loanInstance)
            mandate_dd.rrr = payload['rrr']
            mandate_dd.requestId = payload['requestId']
            mandate_dd.transactionRef = payload['transactionRef']
            mandate_dd.save()
            return JsonResponse({'message': 'Transaction Reference Has Been Updated!'}, status=201)
        return JsonResponse({'message': 'Method Not Allowed'}, status=501)


class RRRandTransactionRefAmount(View):
    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            data = self.request.body.decode("utf-8")
            payload = json.loads(data)
            print(payload)
            loanInstance = Loan.objects.get(loan_key=payload['loan_key'])
            mandate_dd = RemitaMandateActivationData.objects.get(loan_key=loanInstance)
            mandate_dd.rrr = payload['rrr']
            mandate_dd.requestId = payload['requestId']
            mandate_dd.transactionRef = payload['transactionRef']
            mandate_dd.amount_debited_at_instance = payload['amountDebitted']
            mandate_dd.lastStatusUpdateTime = payload['lastStatusUpdateTime']
            mandate_dd.save()
            return JsonResponse({'message': 'Transaction Has Been Updated!'}, status=201)
        return JsonResponse({'message': 'Method Not Allowed'}, status=501)


class RemitaDDMandateTransactionRecord(View):
    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            data = self.request.body.decode("utf-8")
            payload = json.loads(data)
            print(payload['record_data']['data']['totalAmount'])
            loanInstance = Loan.objects.get(loan_key=payload['loan_key'])
            mandateDatas = RemitaMandateActivationData.objects.get(loan_key=loanInstance)
            try:
                remita_dd_history = RemitaMandateTransactionRecord.objects.get(loan=loanInstance)
                remita_dd_history.total_amount = payload['record_data']['data']['totalAmount']
                remita_dd_history.total_transaction_count = payload['record_data']['data']['totalTransactionCount']
                remita_dd_history.save()
            except RemitaMandateTransactionRecord.DoesNotExist:
                remita_dd_history = RemitaMandateTransactionRecord.objects.create(
                    remita_dd_mandate_owned_record=mandateDatas,
                    loan=loanInstance,
                    total_amount=payload['record_data']['data']['totalAmount'],
                    total_transaction_count=payload['record_data']['data']['totalTransactionCount']
                )
            try:
                exists = RemitaPaymentDetails.objects.get(lastStatusUpdateTime=payload['record_data']['data']['paymentDetails'][0]['lastStatusUpdateTime'])
                exists.status = payload['record_data']['data']['paymentDetails'][0]['status']
                exists.save()
            except RemitaPaymentDetails.DoesNotExist:
                for _ in range(int(payload['record_data']['data']['totalTransactionCount'])):
                    RemitaPaymentDetails.objects.create(
                        loan=loanInstance,
                        amount=payload['record_data']['data']['paymentDetails'][0]['amount'],
                        lastStatusUpdateTime=payload['record_data']['data']['paymentDetails'][0]['lastStatusUpdateTime'],
                        status=payload['record_data']['data']['paymentDetails'][0]['status'],
                        statuscode=payload['record_data']['data']['paymentDetails'][0]['statuscode'],
                        RRR=payload['record_data']['data']['paymentDetails'][0]['RRR'],
                        transactionRef=payload['record_data']['data']['paymentDetails'][0]['transactionRef'],
                        remita_transactions=remita_dd_history
                    )
            return JsonResponse({'message': 'Transaction Has Been Updated!', 'statuscode':'051'}, status=201)
        return JsonResponse({'message': 'Method Not Allowed'}, status=501)


class RemitaDDStatusReport(View):
    def post(self, *args, **kwargs):
        if self.request.is_ajax():
            data = self.request.body.decode("utf-8")
            payload = json.loads(data)
            print(payload)
            loanInstance = Loan.objects.get(loan_key=payload['loan_key'])
            try:
                dd_status = RemitaMandateStatusReport.objects.get(loan=loanInstance)
                dd_status.loan = loanInstance
                dd_status.start_date = payload['startDate']
                dd_status.end_date = payload['endDate']
                dd_status.request_id = payload['requestId']
                dd_status.mandate_id = payload['mandateId']
                dd_status.registration_date = payload['registrationDate']
                dd_status.mandate_status = payload['isActive']
                dd_status.report_status = payload['status']
                dd_status.save()
            except RemitaMandateStatusReport.DoesNotExist:
                RemitaMandateStatusReport.objects.create(
                    loan=loanInstance,
                    start_date=payload['startDate'],
                    end_date=payload['endDate'],
                    request_id=payload['requestId'],
                    mandate_id=payload['mandateId'],
                    registration_date=payload['registrationDate'],
                    mandate_status=payload['isActive'],
                    report_status=payload['status']
                )
            return JsonResponse({'message': 'Transaction Has Been Updated!'}, status=201)
        return JsonResponse({'message': 'Method Not Allowed'}, status=501)