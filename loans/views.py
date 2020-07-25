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
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView
from django.views.generic.base import View

from accounts.models import Profile
from banks.models import BankCode
from borrowers.models import Borrower
from company.models import Company, RemitaCredentials, RemitaMandateActivationData
from loans.forms import CollateralForm, LoanFileForm
from loans.models import Loan, LoanType, ModeOfRepayments, Penalty, Collateral, LoanTerms, CollateralFiles, \
    CollateralType
from minloansng.cloudinary_settings import cloudinary_upload_preset, cloudinary_url
from minloansng.minmarket.packages.remita import remita_dd_url, statuscode_success
from minloansng.mixins import GetObjectMixin
from minloansng.utils import random_string_generator, secondWordExtract, digitExtract, addDays, get_fileType

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
        context['company'] = context['object'] = company_inst
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['loan_obj'] = self.get_object()
        context['form'] = LoanFileForm()
        if self.get_object().loan_file_upload is not None:
            file_type = get_fileType(self.get_object().loan_file_upload.url)
            context['fileType'] = str(file_type)
        if self.get_object().mode_of_repayments == "Remita Direct Debit":
            context['dd_obj'] = RemitaMandateActivationData.objects.get(loan_key=self.get_object())
            context['company_creds'] = RemitaCredentials.objects.get(connected_firm=company_inst)
        else:
            context['dd_obj'] = RemitaMandateActivationData.objects.get(loan_key=self.get_object())
            context['company_creds'] = RemitaCredentials.objects.get(connected_firm=company_inst)
        return context

    def render_to_response(self, context, **response_kwargs):
        if context:
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
            return JsonResponse({'message':'Loan File Uploaded Successfully!'})
        return JsonResponse({'message':'form Invalid'})


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
        collateral_type_instance = CollateralType.objects.get(name__iexact=self.request.POST.get('collateralType'))
        collateral_file_instance = CollateralFiles.objects.get(token=self.request.POST.get('collateralToken'))
        collateral_obj = Collateral.objects.get(slug=self.request.POST.get('collateralToken'))
        collateral_obj.collateral_type = collateral_type_instance
        collateral_obj.name = self.request.POST.get('collateralName')
        collateral_obj.registered_date = self.request.POST.get('registered_date')
        collateral_obj.registered_time = self.request.POST.get('collateralTime')
        collateral_obj.status = self.request.POST.get('collateralStatus')
        collateral_obj.value = self.request.POST.get('collateralValue')
        collateral_obj.condition = self.request.POST.get('collateralCondition')
        collateral_obj.view_shader = self.request.POST.get('collateralViewShade')
        collateral_obj.description = self.request.POST.get('collateralDescription')
        collateral_obj.collateral_files = collateral_file_instance
        collateral_obj.save()
        return JsonResponse({'message': 'Data Successfully Saved!'})


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
        payer_obj = Borrower.objects.get(phone__exact=self.request.POST.get("payerPhone"))
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
            hash_key=self.request.POST.get("hash"),
            serviceTypeId=self.request.POST.get("serviceTypeId"),
            loan_key=loan_instance,
        )

        # update the date of the loan date
        loan_instance.number_repayments = self.request.POST.get("maxNoOfDebits")
        loan_instance.release_date = datetime.strptime(self.request.POST.get('startDate'), "%d/%m/%Y")
        loan_instance.end_date = datetime.strptime(self.request.POST.get("endDate"), "%d/%m/%Y")
        loan_instance.save()

        return JsonResponse({'message': 'Submitted To DB, Processing to Remita Server..'})


class RemitaMandateUpdate(View):
    def post(self, *args, **kwargs):
        print(self.request.POST)
        print(self.request.POST['statuscode'])
        if self.request.POST['statuscode'] == statuscode_success:
            mandate_dd = RemitaMandateActivationData.objects.get(requestId=self.request.POST['requestId'])
            mandate_dd.status = self.request.POST['status']
            mandate_dd.statuscode = self.request.POST['statuscode']
            mandate_dd.mandateId = self.request.POST['mandateId']
            mandate_dd.save()
            return JsonResponse({'message': 'Mandate Activation Updated!', 'status': '007'})
        return JsonResponse({'message': 'Mandate Failed To Update Please Redo Process', 'status': '003'})
