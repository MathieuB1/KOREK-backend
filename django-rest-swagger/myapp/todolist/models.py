from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())


class TodoList(models.Model):
    # Attributes Class
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True)
    text = models.TextField(default='')
    owner = models.ForeignKey('auth.User', related_name='todos')

    # Adding customized python fields
    highlighted = models.TextField()

    class Meta:
        ordering = ('created',)

    def save(self, *args, **kwargs):
        """
        Use the `pygments` library to create a highlighted HTML
        representation of the code TodoList.
        """
        lexer = get_lexer_by_name('python')
        linenos = 'table'
        options = {'title': self.title}
        formatter = HtmlFormatter(style='friendly', linenos=linenos,
                                  full=True, **options)
        self.highlighted = highlight(self.text, lexer, formatter)

        # Create and save the validated object
        super(TodoList, self).save(*args, **kwargs)
