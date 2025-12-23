from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user_id', 'question_preview', 'success', 'row_count')
    list_filter = ('success', 'timestamp', 'user_id')
    search_fields = ('question', 'sql', 'error', 'user_id')
    readonly_fields = ('timestamp', 'client_ip', 'user_id', 'question', 'sql', 'success', 'row_count', 'error')

    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = "Question"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
