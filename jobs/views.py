from django.shortcuts import redirect, get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import (
        CreateView, ListView,
        DetailView, RedirectView,
        )

from jobs.models import Job, JobProposal
from users.models import User

from direct_messages.services import MessagingService
from direct_messages.models import ChatRoom

class JobListView(ListView):
    """
    Show a list of jobs.
    """
    model = Job
    ordering = ('job_title',)
    context_object_name = 'jobs'
    template_name = 'jobs/job_list.html'
    queryset = Job.objects.all()


@method_decorator([login_required], name='dispatch')  # 装饰器，使该view只有登录用户才能使用
class JobCreateView(CreateView):
    """
    Create a job
    """
    model = Job
    fields = ('job_title', 'job_description', 'price', 'tags', 'document')
    template_name = 'jobs/job_add_form.html'

    def form_valid(self, form):
        job = form.save(commit=False) # 暂不存储表单数据到数据库，进行其他操作后再保存
        job.owner = self.request.user

        job.save()
        form.save_m2m()  # 存储关联的数据库
        return redirect('jobs:job_detail', job.pk)


@method_decorator([login_required], name='dispatch')
class JobDetailView(DetailView):
    """
    Show the job's detail
    """
    model = Job
    template_name = 'jobs/job_detail.html'

    def get_context_data(self, **kwargs):
        job_id = self.kwargs.get('pk')
        job = Job.objects.get(pk=job_id) # 从Job model 获取job_id
        # 若当前点击网站发起request 的user 不是任务发布者，且是自由职业者
        if job.owner != self.request.user and self.request.user in job.freelancers:
            kwargs['current_proposal'] = JobProposal.objects.get(  # 返回此任务的申请属性
                    job__pk=job_id,
                    freelancer=self.request.user
                    )

        context = super().get_context_data(**kwargs)
        return context


class JobApplyView(CreateView):
    """
    Try to apply a job
    """
    model = JobProposal
    fields = ('proposal', ) # fields 指定要显示的表单
    template_name = 'jobs/job_apply_form.html'

    # 从URL中获取当前任务id，方便后面对该任务的属性进行操作
    def get_context_data(self, **kwargs):
        kwargs['jobs'] = Job.objects.get(pk=self.kwargs.get('pk'))
        return super().get_context_data(**kwargs)

    # 表单提交后，将申请者指定为当前用户，并保存在数据库，最后跳转到自己的任务页面
    def form_valid(self, form):
        proposal = form.save(commit=False)
        proposal.job = Job.objects.get(pk=self.kwargs.get('pk'))
        proposal.freelancer = self.request.user

        proposal.save()
        return redirect('users:job_profile', self.request.user.username)


class ProposalAcceptView(RedirectView):
    """
    Accept a proposal
    """
    permanent = False # 定义重定向是否永久，http状态码不同，永久301，非永久302；默认False
    query_string = True # 是否将GET查询的字符串传递给新链接。True，将字符串（此处为username）附加到URL的最后；默认False丢弃；
    pattern_name = 'jobs:job_detail' # 重定向的地址

    # 指定job 给某freelancer，并将job的状态改为working
    def get_redirect_url(self, *args, **kwargs):
        job = get_object_or_404(Job, pk=kwargs['pk'])
        job.freelancer = User.objects.get(username=kwargs.get('username'))
        job.status = 'working'
        job.save()

        # 委托任务后，创建两者间的对话，并由owner发送第一个消息
        is_chatroom = False
        try:
            chatroom = ChatRoom.objects.get(sender=self.request.user(), recipient=job.freelancer)
            is_chatroom = True
        except:
            pass

        if not is_chatroom:
            try:
                chatroom = ChatRoom.objects.get(sender==job.freelancer, recipient=self.request.user)
            except:
                pass

        if not is_chatroom:
            chatroom = ChatRoom.objects.create(sender=self.request.user, recipient=job.freelancer)


        MessagingService().send_message(
                sender=self.request.user,
                recipient=job.freelancer,
                message="""
                    Hi {username},

                    Your proposal is accepted.

                    project details : <a href='{url}'>{job}</a>
                    """.format(username=job.freelancer.username,
                               url=reverse("job:job_detail", kwargs={"pk": job.pk}),
                               job=job.job_title
                               )
                    )
        )

        messages.success(
                self.request, 'User : {} is assigned to your project'.format(kwargs.get('username'))
                )

        return super().get_redirect_url(*args, pk=kwargs['pk'])

#class JobCloseView(RedirectView):
#    """
#    Close a job.
#    """
#    permanent = False
#    query_string = True
#    pattern_name = 'jobs:job_detail'
#
#    def get_redirect_url(self, *args, **kwargs):
#        job = get_object_or_404(Job, pk=kwargs['pk'])
#        job.status = 'ended'
#        job.save()
#
#        return super().get_redirect_url(*args, pk=kwargs['pk'])
