from rest_framework import serializers

from app.account.models import RealUser


class RealUserIdListSerializer(serializers.ModelSerializer):
    """
    账户id列表
    """
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='realuser-detail',
        lookup_field='pk'
    )

    class Meta:
        model = RealUser
        fields = ('id', 'username', 'is_active', 'detail_url')
        read_only = 'username'


class RealUserDetailSerializer(serializers.ModelSerializer):
    """
    获取账户信息
    """

    class Meta:
        model = RealUser
        exclude = ('password',)


class RealUserCreateSerializer(serializers.ModelSerializer):
    """
    注册账户
    """

    class Meta:
        model = RealUser
        fields = ('username', 'password')
