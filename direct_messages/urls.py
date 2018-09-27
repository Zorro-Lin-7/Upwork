from django.urls import path, include

from .view import MessageView, MessageDetailView

app_name = 'direct_messages'

urlpatterns = [
        path('messages/', include(([
             path('', messageView.as_view(), name='list_messge'),
             path('<int:pk>', MessageDetailView.as_view(), name='user_message'),
        ])))
    ]
