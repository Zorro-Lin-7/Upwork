from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

# 这里还读取了Django设置中的用户模型，也就是我们先前编写的模型，设置为常量的目的是便于引用
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class ChatRoom(models.Model):

# sender, recipient 都是用户对象
    sender = models.ForeignKey(
            AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='chatroom_sender',
            verbose_name='Sender'
            )
    recipient = models.ForeignKey(
            AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='chatroom_recipient'
            )
    created_at = models.DateTimeField('sent at', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # 根据创建时间降序排列
        unique_together = ('sender', 'recipient')

class Message(models.Model):

    content = models.TextField('Content') # 消息文本
    sender = models.ForeignKey(
            AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='sent_dm',
            verbose_name='Sender',
            )
    recipient = models.ForeignKey(
            AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='received_dm',
            verbose_name='Recipient',
            )
    sent_at = models.DateTimeField('sent at', auto_now_add=True) # 发送时间
    read_at = models.DateTimeField('read at', null=True, blank=True) # 读取时间

    class Meta:
        ordering = ['-sent_at'] # 消息按发送实践降序

# unread 方法判断是否已读，使用装饰器将其设为属性
    @property
    def unread(self):
        if self.read_at is not None:
            return True

    def __str__(self):
        return self.content

    def save(self, **kwargs):
        if self.sender == self.recipient:
            raise ValidationError("You can't send message to yourself!")
       # 发送后保存发送时间
        if not self.id:
            self.sent_at = timezone.now()
        super(Message, self).save(**kwargs)

