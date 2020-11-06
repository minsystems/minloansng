from rest_framework.generics import ListAPIView

from company.models import Company
from settings.api.serializers import CompanyStaffSerializer


class CompanyStaffsAPIView(ListAPIView):
    lookup_field = 'slug',
    serializer_class = CompanyStaffSerializer # brings & validate data from any model

    def get_queryset(self):
        company_obj = Company.objects.get(slug=self.kwargs.get('slug'))
        return company_obj.staffs.all()
