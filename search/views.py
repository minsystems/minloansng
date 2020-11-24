from django.shortcuts import render
from django.views.generic import ListView
from loans.models import Loan
from company.models import Company, BankAccountType
from transactions.models import Transaction
from borrowers.models import Borrower, BorrowerGroup, BorrowerBankAccount


class SearchSystemView(ListView):
    template_name = "search/view.html"

    def get_context_data(self, *args, **kwargs):
        context = super(SearchSystemView, self).get_context_data(*args, **kwargs)
        company_obj = Company.objects.get(slug=self.kwargs.get('slug'))
        query = self.request.GET.get('q')
        context['query'] = query
        context['userCompany_qs'] = company_obj.user.company_set.all()
        context.update({
            'company': company_obj,
            'object': company_obj,
        })
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        method_dict = request.GET
        query = method_dict.get('q', None)  # method_dict['q']
        if query is not None:
            return Loan.objects.search(query)  # .search(query)
        return Loan.objects.opened_loans()
        '''
        __icontains = field contains this
        __iexact = fields is exactly this
        '''
