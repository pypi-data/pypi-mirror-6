from .admin import JobAdmin
from .models import Job
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test


def job_run(request, pk):
    return JobAdmin(Job, admin.site).run_job_view(request, pk)
job_run = user_passes_test(lambda user: user.is_superuser)(job_run)
