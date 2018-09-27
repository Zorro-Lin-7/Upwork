from django.forms import ModelForm
from django import forms

from .models import Message


class MessageForm(ModelForm):

# 消息输入框
    content = forms.CharField(
            max_length=1000,
            required=True,
            widget=forms.TextInput(    # 属性设置，相当于<form class='', name='' ... >
                attrs={'class': 'write_msg',
                       'name': 'content',
                       'placeholder': 'Reply...',  # 占位符：提示信息
                       }
                )
            )

    class Meta:
        model = Message
        fields = ['content']
