from django.db import models

class AuditLog(models.Model):
    """
    Audit log for NLP-to-SQL queries.
    Stores the history of questions, generated SQL, and execution results.
    """
    timestamp = models.DateTimeField(auto_now_add=True)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_id = models.CharField(max_length=255, null=True, blank=True, help_text="User ID or identifier")
    question = models.TextField(help_text="Natural language question asked by user")
    sql = models.TextField(null=True, blank=True, help_text="Generated SQL query")
    success = models.BooleanField(default=False)
    row_count = models.IntegerField(default=0)
    error = models.TextField(null=True, blank=True, help_text="Error message if failed")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.timestamp} - {self.user_id} - {status}"
