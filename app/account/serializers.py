from rest_framework import serializers

from app.account.models import RealUser, Department


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


class RealUserChangePasswordSerializer(serializers.ModelSerializer):
    """
    更改密码
    """

    class Meta:
        model = RealUser
        fields = ('password',)


class DepartmentSerializer(serializers.ModelSerializer):
    """
    部门信息
    """

    def validate(self, data):
        if data['director'] and data['director'] not in [i for i in self.instance.department_name.all()]:
            raise serializers.ValidationError('部门主管必须属于该部门')
        return data

    class Meta:
        model = Department
        fields = '__all__'
