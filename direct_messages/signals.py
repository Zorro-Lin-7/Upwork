from django.dispatch import Signal

# 所有信号都是django.dispatch.Signal的实例
message_sent = Signal(providing_args=['from_user', 'to'])
message_read = Signal(providing_args=['from_user', 'to'])

# 可以用message_sent.send()发送信号，返回的是一个元组对的列表
