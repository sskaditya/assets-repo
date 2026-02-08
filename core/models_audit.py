"""
Comprehensive Audit Logging System
Tracks all create, update, and delete operations across the system
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import json


class AuditLog(models.Model):
    """
    Comprehensive audit log for tracking all user actions.
    Uses generic foreign keys to track changes to any model.
    """
    
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('EXPORT', 'Export'),
        ('IMPORT', 'Import'),
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
    ]
    
    # Who performed the action
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    username = models.CharField(
        max_length=150, 
        help_text="Username at time of action (preserved even if user deleted)"
    )
    
    # What was affected (generic relation)
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Type of object that was modified"
    )
    object_id = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="ID of the object that was modified"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(
        max_length=500,
        help_text="String representation of the object at time of action"
    )
    
    # Action details
    action = models.CharField(
        max_length=20, 
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    description = models.TextField(
        help_text="Human-readable description of what happened"
    )
    
    # Data tracking
    old_values = models.JSONField(
        null=True, 
        blank=True,
        help_text="Previous values before the change (for UPDATE/DELETE)"
    )
    new_values = models.JSONField(
        null=True, 
        blank=True,
        help_text="New values after the change (for CREATE/UPDATE)"
    )
    changed_fields = models.JSONField(
        null=True, 
        blank=True,
        help_text="List of fields that were changed"
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        null=True, 
        blank=True,
        help_text="Browser/client user agent string"
    )
    request_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="URL path of the request"
    )
    request_method = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="HTTP method (GET, POST, PUT, DELETE, etc.)"
    )
    
    # Timestamp
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the action occurred"
    )
    
    # Company context (for multi-tenancy)
    company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="Company context at time of action"
    )
    
    # Additional metadata
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional metadata about the action"
    )
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['content_type', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['company', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.action} - {self.object_repr} - {self.timestamp}"
    
    @property
    def action_display(self):
        """Get human-readable action name"""
        return dict(self.ACTION_CHOICES).get(self.action, self.action)
    
    @property
    def changes_summary(self):
        """Get a summary of changes made"""
        if self.action == 'CREATE':
            return f"Created {self.object_repr}"
        elif self.action == 'DELETE':
            return f"Deleted {self.object_repr}"
        elif self.action == 'UPDATE' and self.changed_fields:
            fields = ', '.join(self.changed_fields)
            return f"Updated {fields} on {self.object_repr}"
        else:
            return self.description


class UserActivitySummary(models.Model):
    """
    Aggregated summary of user activity for quick reporting.
    Updated periodically via management command.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_summary')
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True)
    
    # Date range
    date = models.DateField(help_text="Date of activity")
    
    # Activity counts
    creates = models.IntegerField(default=0, help_text="Number of create actions")
    updates = models.IntegerField(default=0, help_text="Number of update actions")
    deletes = models.IntegerField(default=0, help_text="Number of delete actions")
    views = models.IntegerField(default=0, help_text="Number of view actions")
    logins = models.IntegerField(default=0, help_text="Number of logins")
    exports = models.IntegerField(default=0, help_text="Number of exports")
    
    # Total activity
    total_actions = models.IntegerField(default=0, help_text="Total actions for the day")
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_activity_summary'
        ordering = ['-date', 'user']
        verbose_name = 'User Activity Summary'
        verbose_name_plural = 'User Activity Summaries'
        unique_together = [['user', 'company', 'date']]
        indexes = [
            models.Index(fields=['-date', 'user']),
            models.Index(fields=['company', '-date']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.total_actions} actions"
