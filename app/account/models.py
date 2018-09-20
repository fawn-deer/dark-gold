from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

HIGHEST_EDUCATION = (
    ('primary_school', '小学'),
    ('middle_school', '初中'),
    ('high_school', '高中'),
    ('polytechnic_school', '中专'),
    ('junior_college', '大专'),
    ('undergraduate', '本科'),
    ('master', '硕士'),
    ('doctor', '博士'),
)

SEX_CHOICES = (
    ('man', '男性'),
    ('woman', '女性')
)


# 部门
class Department(models.Model):
    """
    部门
    """

    class Meta:
        verbose_name = '部门'
        verbose_name_plural = '部门'

    name = models.CharField('''部门名称''', max_length=100, blank=False, null=False, db_index=True)
    '''部门名称'''
    director = models.ForeignKey(User, verbose_name='部门主管', on_delete=models.SET_NULL, null=True, blank=True)
    '''部门主管'''

    def __str__(self):
        return self.name

    # 自定义验证
    def clean(self):
        if self.director not in [i.user for i in self.realuser_set.all()]:
            raise ValidationError('部门主管必须属于该部门')


# 扩展User属性
class RealUser(models.Model):
    """
    扩展User属性
    """
    original_user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    '''Django默认用户'''
    id_number = models.CharField('''身份证号''', max_length=50, null=True, blank=True)
    '''身份证号'''
    sex = models.CharField('''性别''', choices=SEX_CHOICES, default='', null=True, blank=True, max_length=5)
    '''性别'''
    phone_number = models.CharField('''手机号''', max_length=11, null=True, blank=True)
    '''手机号'''
    highest_education = models.CharField('''最高学历''', choices=HIGHEST_EDUCATION, default='', max_length=20)
    '''最高学历'''
    department = models.ForeignKey(Department, verbose_name='部门', on_delete=models.SET_NULL, null=True, blank=True)
    '''部门'''
    entry_date = models.DateField('''入职日期''', default=None, null=True, blank=True)
    '''入职日期'''
    leave_date = models.DateField('''离职日期''', default=None, null=True, blank=True)
    '''离职日期'''

    def __str__(self):
        return ' '.join([
            str(self.original_user.get_username()),
            str(self.original_user.get_full_name())
        ])


@receiver(post_save, sender=User)
def create_user_real_user(sender, instance, created, **kwargs):
    if created:
        RealUser.objects.create(original_user=instance)


@receiver(post_save, sender=User)
def save_user_real_user(sender, instance, **kwargs):
    instance.realuser.save()
