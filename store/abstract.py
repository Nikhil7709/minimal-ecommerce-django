from django.db import models

class AbstractAuditCreator(models.Model):
    """
    Abstract model to track the user who created the object.
    """
    created_by = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True


class AbstractAuditUpdater(models.Model):
    """
    Abstract model to track the user who last updated the object.
    """
    updated_by = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        abstract = True

