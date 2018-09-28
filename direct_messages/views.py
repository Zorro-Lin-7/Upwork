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


class MessageDetailView(CreateView):

    # 定义好模型、表单和模板
    model = ChatRoom
    form_class = MessageForm
    template_name = 'direct_messages/direct_messages.html'

    def get_context_data(self, **kwargs):

        chat_id = self.kwargs.get('pk')

        chatroom = ChatRoom.objects.get(pk=chat_id)

        message = Message.objects.filter(
                sender=chatroom.sender,
                recipient=chatroom.recipient
                ).first()
        if not message:
            message = Message.objects.filter(
                    sender=chatroom.sender,
                    recipient=chatroom.recipient
                    ).first()

        user = self.request.user
        # 向模板返回active_conversation变量
        kwargs['active_conversation'] = message
        # 向模板返回conversations变量
        current_conversations = MessagingService().get_conversations(user=self.request.user)
        kwargs['conversations'] = current_conversations

        if user == message.sender:
            active_recipient = message.recipient
        else:
            active_recipient = message.sender
        # 向模板返回running_conversations变量
        running_conversations = MessagingService().get_active_conversations(user, active_recipient)
        kwargs['running_conversations'] = running_conversations

        return super().get_context_data(**kwargs)


    def form_valid(self, form):
        # 在提交表单后，指定sender 和recipient，然后存储到数据库
        obj = self.get_object()

        if self.request.user == obj.sender:
            recipient = obj.recipient
        else:
            recipient = obj.sender

        message = form.save(commit=False)
        message.sender = self.request.user
        message.recipient = recipient

        message.save()
        messages.success(self.request, 'The message is sent with success!')
        return redirect('direct_messages:user_message', obj.pk)
