import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your models here.
class PlanCharge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tier = models.IntegerField()
    charge_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='plans', on_delete=models.CASCADE)

    def __unicode__(self):
        return str(self.charge_id)