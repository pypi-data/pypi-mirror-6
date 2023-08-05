from django.db import models
from multisessionform.models import MultiSessionFormMixin

class MSFExample(MultiSessionFormMixin, models.Model):
    required_field_one = models.TextField()
    integer_field = models.IntegerField(blank = True, null = True, default = None)
    text_field = models.TextField(blank = True, null = True, default = None)
    
    def get_absolute_url(self):
        return "/test/"