from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.conrib.auth import login
from django.views.generic import (
        TemplateView, UpdateView,
        CreateView, ListView,
)

from .models import User
from .forms import FreelancerSignUpForm, OwnerSignUpForm



# 展示注册指引，让用户根据自己的身份选择注册自由职业者还是客户
class SignUpView(TemplateView):
    """
    提供注册选择页面
    """
    template_name = 'users/signup.html'


# 展示用户的个人信息
class UserDetailView(TemplateView):
    model = User
    template_name = 'users/user_profile.html'

    # 重写TemplateView 的get_context_data 方法
    def get_context_data(self, **kwargs):
        """
        Prepares user context value based on username request from url
        URL：127.0.0.1:8000/user/<str:username>，获取url请求的username值
        根据username调用指定的用户对象实例
        定义context['profile']，是模板可以直接使用profile调用该关键字
        返回context字典
        """
        context = super(UserDetailView, self).get_context_data(**kwargs)
        username = self.kwargs.get('username')
        context['profile'] = User.objects.get(username=username)
        return context


# 修改个人信息的view:
class UpdateProfileView(UpdateView):
    model = User
    # 指定页面表单将出现的字段，即在修改页面可以修改的字段
    fields = ['profile_photo', 'first_name', 'last_name', 'profile', 'skills'] # Keep listing whatever fields
    template_name = 'users/user_profile_update.html'

    def form_valid(self, form):
        """
        Checks valid form and add/save many to many tags field in user object.
        """
        user = form.save(commit=False) # False是为了不让表单值立即改变数据库
                                       # 保存前还能操作其他数值
        user.save()
        form.save_m2m() # 该方法保存了其他关联数据库变更信息
        messages.success(self.request, 'Your profile is updated successfully.')
        return redirect('users:user_profile', self.object.username) # 重定向到当前用户的个人详情页

    def get_success_url(self):
        '''
        当表单提交成功时跳转的链接
        '''
        return reverse('users:user_profile', kwargs={'username': self.object.username})


class ListFreelancersView(ListView):
    """
    Show all Freelancers
    """
    model = User
    context_object_name = 'freelancers' # 指定在模板中使用的变量名
    template_name = 'users/freelancer_list.html'

    def get_queryset(self):
        """
        基于user model 的 is_freelancer 列进行过滤筛选.
        返回的值是context_object_name的值，赋值给变量名freelancers。模板可以直接调用freelancers。
        """
        return User.objects.filter(is_freelancer=True)


class FreelancerSignUpView(CreateView):
    """
    Register a freelancer.
    """
    model = User
    form_class = FreelancerSignUpForm # 指定使用的表单
    template_name = 'users/signup_form.html'

    def get_context_data(self, **kwargs):
        """
        Updates context value 'user_type' in current context.
        将从该view注册的用户赋予自由职业者身份
        """
        kwargs['user_type'] = 'freelancer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        """
        表单POST后，存储新用户到数据库，并使用login登录。
        """
        user = form.save()
        login(self.request, user)
        return redirect('home')


class OwnerSignUpView(CreateView):
    """
    Register a user
    """
    model = User
    form_class = OwnerSignUpForm
    template_name = 'users/signup_form.html'

    def form_valid(self, form):
        user = form.save()
        login(self,request, user)
        return redirect('home')
