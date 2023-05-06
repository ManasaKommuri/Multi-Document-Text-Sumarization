from django.db import models

# Create your models here.

class DocumentModel(models.Model):
    document =models.FileField(upload_to="documents")