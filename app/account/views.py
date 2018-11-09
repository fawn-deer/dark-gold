import datetime
from calendar import timegm

from django.db.models import Q
from rest_framework import generics, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response

from app.account.models import RealUser, Department
from app.account.serializers import RealUserIdListSerializer, RealUserDetailSerializer, RealUserCreateSerializer, \
    RealUserChangePasswordSerializer, DepartmentSerializer


class RealUserViewSets(mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    """
    账户视图集
    """
    queryset = RealUser.objects.all()

    def get_permissions(self):
        permission_classes = []
        if self.action in ['list',
                           'retrieve',
                           'update',
                           'change_password']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['destroy']:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()

        # 非管理员，删除部分字段，设置只读字段
        if self.action not in ['create', 'change-password']:
            if not self.request.user or not self.request.user.is_superuser:
                serializer_class.Meta.exclude = ('password', 'is_superuser', 'is_staff', 'jwt_deadline')
                serializer_class.Meta.read_only_fields = ('is_active',)

        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        if self.action in ['create']:
            serializer_class = RealUserCreateSerializer
        elif self.action in ['change_password']:
            serializer_class = RealUserChangePasswordSerializer
        else:
            serializer_class = RealUserDetailSerializer
        return serializer_class

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 非管理员无法更改非登录账号资料
        if not request.user.is_superuser and int(kwargs['pk']) != request.user.pk:
            raise PermissionDenied('没有权限更改账户资料')
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.set_password(instance.password)
        instance.save()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    @action(
        methods=['POST'],
        detail=True,
        url_path='change-password',
        url_name='change_password',
    )
    def change_password(self, request, pk=None):
        """
        更改密码
        :param request:
        :param pk:
        :return:
        """
        user = self.get_object()
        # 非管理员或登录账户，无法更改其他账户密码
        if request.user.is_superuser or request.user.pk == int(pk):
            serializer = RealUserChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                user.set_password(request.data['password'])
                # 设置过期时间修改后3秒
                user.jwt_deadline = timegm(
                    (
                            datetime.datetime.utcnow() + datetime.timedelta(seconds=3)
                     ).utctimetuple()
                )
                user.save()
                return Response({'status': 'password set, please login after 3 seconds'})
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


# 通用分页设置
class CurrencyResultsSetPagination(PageNumberPagination):
    """
    通用分页设置，每页10条，最大10000页
    """
    page_size = 10
    max_page_size = 10000
    page_size_query_param = 'page_size'


# 获取账户ID列表
class RealUserIdList(mixins.ListModelMixin,
                     generics.GenericAPIView):
    """
    获取账户ID列表
    """
    queryset = RealUser.objects.all().order_by('id')
    serializer_class = RealUserIdListSerializer
    pagination_class = CurrencyResultsSetPagination
    permission_classes = (IsAdminUser,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# 获取id1到id2之间的全部账户信息
class RealUserSomeUserDetailIList(mixins.ListModelMixin,
                                  generics.GenericAPIView):
    """
    获取id1到id2之间的全部账户信息
    """
    serializer_class = RealUserDetailSerializer
    pagination_class = CurrencyResultsSetPagination
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        queryset = RealUser.objects
        id1 = self.request.query_params.get('id1', None)
        id2 = self.request.query_params.get('id2', None)
        # 无参数
        if id1 is None and id2 is None:
            return queryset.all().order_by('id')
        # 单参数
        if id1 is None:
            id1 = 0
        if id2 is None:
            id2 = 0

        if id1 is not None and id2 is not None:
            id1 = int(id1)
            id2 = int(id2)
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


class DepartmentViewSets(viewsets.ModelViewSet):
    """
    部门视图集
    """
    queryset = Department.objects.all().order_by('id')
    pagination_class = CurrencyResultsSetPagination

    def get_permissions(self):
        """
        普通用户只允许查看，管理员可以添加更新删除
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            serializer_class = DepartmentSerializer
            serializer_class.read_only = True
        elif self.action in ['create']:
            serializer_class = DepartmentSerializer
            serializer_class.Meta.fields = ('name',)
        else:
            serializer_class = DepartmentSerializer
        return serializer_class

    def perform_destroy(self, instance):
        users = RealUser.objects.filter(department=instance.id)
        users.update(department=None)
        instance.delete()
