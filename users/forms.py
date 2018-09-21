from django import forms
from django.conrib.auth.forms import ReadOnlyPasswordHashField
from django.db import transaction

from .models import User

class UserCreationForm(forms.ModelForm):
    """
    创建用户时的表单
    """
    username = forms.CharField(max_length=30, required=True, help_text='Required.')
    first_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    email = forms.EmailField(max_length=254, requried=True, help_text='Required. Inform a valid email address.')

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Passwrod Confirmation', widget=forms.PasswordInput) # 确认密码


    class Meta:
        # 注册表单字段
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def clean_password(self):
        # 检查两次密码是否相同
        password1 = self.clean_data.get("password1")
        password2 = self.clean_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")
        return password2

    def save(self, commit=True):
        # 以哈希格式存储密码
        user = super().save(commit=Fasle)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """
    A form for updating users.
    Includes all the fields on the user, but replaces the
    password field with admin's password hash display field.
    """

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'username', 'is_active', 'is_admin')

    def clean_password(self):
        # 不管用户填了什么，最后都返回初始值。因为field 无权访问初始值，所以在这里实现该方法
        return self.initial["password"]


class FreelancerSignUpForm(UserCreationForm):

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_freelancer = True
        user.save()
        return user


class OwnerSignUpForm(UserCreationForm):

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_owner = True
        if commit:
            user.save()
        return user
