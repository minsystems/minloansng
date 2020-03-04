from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic import DetailView, ListView

from borrowers.models import Borrower, BorrowerGroup
from company.models import Company
from minloansng.mixins import GetObjectMixin


class BorrowerCreateView(GetObjectMixin, LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'borrowers/add-borrower.html'

    def get_context_data(self, **kwargs):
        context = super(BorrowerCreateView, self).get_context_data(**kwargs)
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        context['borrowers_qs'] = self.get_object().borrower_set.all()
        context['borrower_group_qs'] = self.get_object().borrowergroup_set.all()
        return context

    def post(self):
        return JsonResponse({'message': 'Submitted For Processing'})


class BorrowerListView(LoginRequiredMixin, ListView):
    queryset = Borrower.objects.all()
    template_name = 'borrowers/borrower-list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BorrowerListView, self).get_context_data(*args, **kwargs)
        owner_company_qs = self.request.user.profile.company_set.all()
        owner_company_obj = owner_company_qs.first()
        context['company_borrowers'] = self.queryset.filter(registered_to=owner_company_obj)
        context['userCompany_qs'] = owner_company_qs
        return context


class BorrowerGroupsListView(LoginRequiredMixin, ListView):
    template_name = 'borrowers/borrower-group_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BorrowerGroupsListView, self).get_context_data(*args, **kwargs)
        context['userCompany_qs'] = self.request.user.profile.company_set.all()
        return context

    def get_queryset(self):
        owner_company_qs = self.request.user.profile.company_set.all()
        bg_qs = BorrowerGroup.objects.filter(registered_to=owner_company_qs)
        return bg_qs
