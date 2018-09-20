from django.contrib.auth.models import User
from rest_framework import serializers

from app.account.models import RealUser


class RealUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RealUser
        fields = '__all__'


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    pass
