from django.db import models


class TodoList(models.Model):
    # Attributes Class
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField(default='')
    owner = models.ForeignKey('auth.User', related_name='todos')

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        # Create and save the validated object
        super(TodoList, self).save(*args, **kwargs)
