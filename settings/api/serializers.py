from rest_framework.serializers import ModelSerializer

from accounts.models import Profile


class CompanyStaffSerializer(ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            'id',
            'get_image',
            'get_name',
            'keycode',
            'role',
            'get_phone'
        ]