from rest_framework import viewsets

from app.account.models import RealUser
from app.account.serializers import RealUserSerializer


class RealUserViewSet(viewsets.ModelViewSet):
    queryset = RealUser.objects.all()
    serializer_class = RealUserSerializer
