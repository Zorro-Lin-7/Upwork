from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.generic import CreateView, RedirectView

from .models import Message, ChatRoom
from .forms import MessageForm
from .services import MessagingService


@method_decorator([login_required], name='dispatch') # 装饰器限制权限
class MessageView(RedirectView):
    # 判断用户是否存在对话，若有则重定向至对话界面，无则重定向至任务列表页面
    permanent = False
    query_string = True
    pattern_name = 'direct_messages:user_message'

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        chatroom = ChatRoom.objects.filter(Q(sender=user) | Q(recipient=user)).first()
        if chatroom:
            return super().get_redirect_url(*args, pk=chatroom.pk)

        return reverse('jobs:job_list')
