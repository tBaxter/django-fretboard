from django.db import models

class TopicManager(models.Manager):
 
    def with_totals(self):
        return self.get_queryset().annotate(post_count=models.Count('posts'))
