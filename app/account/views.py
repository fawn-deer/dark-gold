from django.contrib.auth.hashers import make_password
from django.db.models import Q
from rest_framework import generics, mixins, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, AllowAny

from app.account.models import RealUser
from app.account.serializers import RealUserIdListSerializer, RealUserDetailSerializer, RealUserCreateSerializer


class RealUserViewSets(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       viewsets.GenericViewSet):
    """
    账户视图集，查看、修改账号信息，仅限登录普通用户
    """
    queryset = RealUser.objects.all()
    serializer_class = RealUserDetailSerializer


class CreateRealUser(mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """
    注册，任何人均可注册
    """
    queryset = RealUser.objects.all()
    serializer_class = RealUserCreateSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.password = make_password(instance.password)
        instance.save()


class DeleteRealUser(mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """
    删除账户，仅限管理员
    """
    queryset = RealUser.objects.all()
    serializer_class = RealUserDetailSerializer
    permission_classes = (IsAdminUser,)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


# 获取账户信息分页设置
class RealUserIdResultsSetPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10000


# 获取账户ID列表
class RealUserIdList(mixins.ListModelMixin,
                     generics.GenericAPIView):
    """
    获取账户ID列表
    """
    queryset = RealUser.objects.all().order_by('id')
    serializer_class = RealUserIdListSerializer
    pagination_class = RealUserIdResultsSetPagination
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# 获取id1到id2之间的全部账户信息
class RealUserDetailId1AndId2List(mixins.ListModelMixin,
                                  generics.GenericAPIView):
    """
    获取id1到id2之间的全部账户信息
    """
    serializer_class = RealUserDetailSerializer
    pagination_class = RealUserIdResultsSetPagination
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = RealUser.objects
        id1 = self.kwargs.get('id1', None)
        id2 = self.kwargs.get('id2', None)
        if id1 is not None and id2 is not None:
            if id1 == id2:
                queryset = queryset.filter(pk=id1)
            elif id1 > id2:
                queryset = queryset.filter(Q(pk__gte=id2) & Q(pk__lte=id1))
            else:
                queryset = queryset.filter(Q(pk__gte=id1) & Q(pk__lte=id2))
        else:
            queryset = queryset.all()
        return queryset.order_by('id')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
