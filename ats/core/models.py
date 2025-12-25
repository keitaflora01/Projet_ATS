from django.db import models
from django_extensions.db.models import ActivatorModel, TimeStampedModel
import uuid

class AtsBaseModel(ActivatorModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
