from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView

from company.models import Company
from minloansng.mixins import GetObjectMixin


class LoanCreateView(GetObjectMixin, LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'loans/add-loan.html'

    def get_context_data(self, **kwargs):
        context = super(LoanCreateView, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['user_pkgs'] = self.request.user.profile.loantype_set.all()
        context['borrowers_qs'] = self.get_object().borrower_set.all()
        context['borrower_group_qs'] = self.get_object().borrowergroup_set.all()
        return context

    def post(self):
        return JsonResponse({'message':'Submitted For Processing'})

    # def get_object(self, *args, **kwargs):
    #     slug = self.kwargs.get(self.slug_url_kwarg)
    #     try:
    #         company_obj = Company.objects.get(slug=slug)
    #     except Company.DoesNotExist:
    #         return redirect(reverse("404_"))
    #     except Company.MultipleObjectsReturned:
    #         company_qs = Company.objects.filter(slug=slug)
    #         company_obj = company_qs.first()
    #     except:
    #         return redirect(reverse('404_'))
    #     return company_obj
