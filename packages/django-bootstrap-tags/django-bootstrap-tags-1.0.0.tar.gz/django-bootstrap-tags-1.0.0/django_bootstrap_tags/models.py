from django.db import models

class Tag(models.Model):
    tag = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.tag