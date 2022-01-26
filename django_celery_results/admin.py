"""Result Task Admin interface."""

import logging

from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect

try:
    ALLOW_EDITS = settings.DJANGO_CELERY_RESULTS['ALLOW_EDITS']
except (AttributeError, KeyError):
    ALLOW_EDITS = False
    pass

from .models import GroupResult, TaskResult

logger = logging.getLogger(__name__)


class TaskResultAdmin(admin.ModelAdmin):
    """Admin-interface for results of tasks."""

    model = TaskResult
    actions = ['rerun_tasks', 'rerun_tasks_with_max_priority']
    save_on_top = True
    change_form_template = 'admin/celery_result_change_form.html'
    date_hierarchy = 'date_done'
    list_display = ('task_id', 'periodic_task_name', 'task_name', 'date_done',
                    'status', 'worker')
    list_filter = ('status', 'date_done', 'periodic_task_name', 'task_name',
                   'worker')
    readonly_fields = ('date_created', 'date_done', 'result', 'meta')
    search_fields = ('task_name', 'task_id', 'status', 'task_args',
                     'task_kwargs')
    fieldsets = (
        (None, {
            'fields': (
                'task_id',
                'task_name',
                'status',
                'worker',
                'content_type',
                'content_encoding',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Parameters'), {
            'fields': (
                'task_args',
                'task_kwargs',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Result'), {
            'fields': (
                'result',
                'date_created',
                'date_done',
                'traceback',
                'meta',
            ),
            'classes': ('extrapretty', 'wide')
        }),
    )

    def _rerun_tasks(self, request, queryset, priority: int = None):
        task_result: TaskResult
        for task_result in queryset:
            logger.debug('Rerunning celery task {} - {}'.format(task_result.task_id, task_result.task_name))
            try:
                task_result.reapply_async(priority=priority)
            except Exception:
                logger.error('Celery task rerun failed', exc_info=True, extra={
                    'task_id': task_result.task_id,
                    'task_name': task_result.task_name
                })

    def rerun_tasks(self, request, queryset):
        self._rerun_tasks(request, queryset)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if '_rerun' in request.POST:
            self.rerun_tasks(request, self.model.objects.filter(pk=object_id))
            return HttpResponseRedirect('.')

        if '_rerun_priority' in request.POST:
            self.rerun_tasks_with_max_priority(request, self.model.objects.filter(pk=object_id))
            return HttpResponseRedirect('.')

        return super().change_view(request, object_id, form_url, extra_context)

    def get_readonly_fields(self, request, obj=None):
        if ALLOW_EDITS:
            return self.readonly_fields
        else:
            return list({
                field.name for field in self.opts.local_fields
            })

    def has_change_permission(self, request, obj=None):
        return ALLOW_EDITS

    def has_add_permission(self, request):
        return ALLOW_EDITS


admin.site.register(TaskResult, TaskResultAdmin)


class GroupResultAdmin(admin.ModelAdmin):
    """Admin-interface for results  of grouped tasks."""

    model = GroupResult
    date_hierarchy = 'date_done'
    list_display = ('group_id', 'date_done')
    list_filter = ('date_done',)
    readonly_fields = ('date_created', 'date_done', 'result')
    search_fields = ('group_id',)


admin.site.register(GroupResult, GroupResultAdmin)
