from rest_framework import serializers

from app.account.models import RealUser, Department


class RealUserIdListSerializer(serializers.ModelSerializer):
    """
    账户id列表
    """
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='pk'
    )

    class Meta:
        model = RealUser
        fields = ('id', 'username', 'is_active', 'detail_url')
        read_only = True


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

    def to_representation(self, instance):
        """
        返回时删除password字段，避免泄露数据库中的密码
        """
        ret = super().to_representation(instance)
        del ret['password']
        return ret


class RealUserChangePasswordSerializer(serializers.ModelSerializer):
    """
    更改密码
    """

    class Meta:
        model = RealUser
        fields = ('password',)

    def to_representation(self, instance):
        """
        更改返回信息，不返回密码
        """
        ret = super().to_representation(instance)
        del ret['password']
        ret['detail'] = '更改成功'
        return ret


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
