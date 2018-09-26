from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from .models import Message, ChatRoom
from .signals import message_read, message_sent

class MessagingService(object):
