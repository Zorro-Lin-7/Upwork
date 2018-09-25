from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from .views import (
        JobApplyView,
        JobCreateView, ProposalAcceptView,
        JobDetailView, JobListView,
        JobCloseView,
        )

app_name = "jobs"

urlpatterns = [
    path('jobs/', include(([
        path('', JobListView.as_view(), name='job_list'),
        path('add/', JobCreateView.as_view(), name='job_add'),
        path('<int:pk>', JobDetailView.as_view(), name='job_detail'),
        path('<int:pk>/apply', JobApplyView.as_view(), name='job_apply'),
        path('<int:pk>/accept/<str:username>', ProposalAcceptView.as_view(), name='proposal_accept'),
        path('<int:pk>/apply', JobCloseView.as_view(), name='job_close'),
    ], 'jobs'), namespace='jobs')),
]

# media相关映射
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
