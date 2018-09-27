from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from .models import Message, ChatRoom
from .signals import message_read, message_sent  # 导入Signal

class MessagingService(object):
    def send_message(self, sender, recipient, message):
        if sender == recipient:
            raise ValidationError("You can't send message to yourself.")

        # 创建message对象
        message = Message(sender=sender, recipient=recipient, content=str(message))
        message.save()
        # 通过message_sent signal 发送message
        message_sent.send(sender=message, from_user=message.sender, to=message.recipient)

        return message, 200  # 最后返回message 对象和 200 http状态码

    def get_unread_messages(self, user):
        return Message.objects.all().filter(recipient=user, read_at=None)  # 通过.filter操作数据库得到所有未读消息的集合

    def read_message_formatted(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            self.mark_as_read(message)
            return message.sender.username + ": " + message.content # 以固定格式返回message
        except Message.DoesNotExist:
            return ""

    def read_message(self, message_id):
        # 读消息，并返回消息的文本
        try:
            message = Message.objects.get(id=message_id)
            self.mark_as_read(message) # 读取消息的helper method，另外定义
            return message.content
        except Message.DoesNotExist:
            return ""

    def mark_as_read(self, message):
        # 设定message读取时间，并发送已读信号，然后将修改后的message存储到数据库
        if message.read_at is None:
            message.read_at = timezone.now()
            message_read.send(sender=message, from_user=message.sender, to=message.recipient)
            message.save()

    def get_conversations(self, user):
        # 获取当前用户的对话列表

        chatrooms = ChatRoom.objects.filter((Q(sender=user) | Q(recipient=user)))

        chatroom_mapper = []
        for chatroom in chatrooms:
            chatroom_dict = {}
            chatroom_dict['pk'] = chatroom.pk

            if user == chatroom.sender:
                recipient = chatroom.recipient
            else:
                recipient = chatroom.sender
            chatroom_dict['recipient'] = recipient
            chatroom_mapper.append(chatroom_dict)

        return chatroom_mapper

    def get_active_conversations(self, sender, recipient):
        # 获取当前对话的消息列表
        # Q 相当于SQL中的where
        active_conversations = Message.objects.filter(
                (Q(sender=sender) & Q(recipient=recipient)) |
                (Q(sender=recipient) & Q(recipient=sender))
                ).order_by('sent_at')

        return active_conversations
