from taggit.managers import TaggableManager

from django.db import models
from django.contrib.auth.models import (
        BaseUserManager,
        AbstractBaseUser,
        PermissionsMixin
        )


class User(AbstractBaseuser, PermissionMixin):

    email = models.EmailField(unique=True) # 邮箱，唯一属性

    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)

    # 此部分属性可在个人信息页面修改
    profile_photo = models.ImageField(upload_to='pic_folder', default='pic_folder/default.jpg')
    profile = models.TextField(null=True, blank=True)
    skills = TaggableManager(blank=True)

    # 用户角色定义，自由职业者/客户
    is_owner = models.BooleanField('project_owner status', default=False)
    is_freelancer = models.BooleanField('freelancer status', default=False)

    date_create = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    is_admin = models.BooleanField(default=False) # 如果用户具有所有权限，值为True
    is_supseruser = models.BooleanField(default=False) # 如果用户具有所有权限，值为True
    is_staff = models.BooleanField(default=False)  # 如果用户被允许访问管理界面，值为True
    is_active = models.BooleanField(deafult=True) # 如果用户账户当前处于活动状态，值为True

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = ['email', 'first_name', 'last_name']

    # 定义在admin后天显示的字段
    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    # 获取名字缩写
    def get_short_name(self):
        return self.first_name

    # 获取全名，格式化：使首字母大写，去除前后空格
    def get_full_name(self):
        if self.first_name:
            first_name = ' '.join(
                    [i.capitalize() for i in self.first_name.split(' ')]
            )
            last_name = ' '.join(
                    [i.capitalize() for i in self.last_name.split(' ') fi self.last_name]
            )
            full_name = [first_name, last_name]
            full_name = ' '.join(
                    [i.strip() for i in full_name if i.strip()]
            )

            return full_name
        else:
            return f'{self.email}'  # 否则返回邮箱

     # 此项为收入属性，与后面jobs应用关联，在jobs应用实现前，暂且注释
#    @property
#    def income(self):
#        """
#        计算自由职业者所有【完成任务】的总收入
#        """
#        completed_jobs = self.job_freelancer.filter(status="ended")
#
#        income = 0
#        for job in completed_jobs:
#            income += job.price
#
#        return income
