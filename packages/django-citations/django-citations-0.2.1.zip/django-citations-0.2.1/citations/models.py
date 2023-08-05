from django.contrib.humanize.templatetags.humanize import ordinal
from django.db import models
from django.utils.html import escape
from datetime import datetime
import pytz

REFERENCE_TYPE_CHOICES = (
    ('BK', 'Book'),
    ('EJL', 'Electronic Journal'),
    ('JL', 'Journal'),
    ('WB', 'Website'),
)


class Reference(models.Model):
    type = models.CharField(max_length=3, choices=REFERENCE_TYPE_CHOICES, default='BK')
    slug = models.CharField(max_length=128, unique=True)

    author = models.CharField(max_length=512)
    title = models.CharField(max_length=512)
    year = models.IntegerField(default=2000)

    series = models.IntegerField(blank=True, null=True)
    volume = models.IntegerField(blank=True, null=True)
    edition = models.IntegerField(blank=True, null=True)

    isbn = models.CharField(max_length=17, blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    publisher = models.CharField(max_length=128, blank=True, null=True)
    place = models.CharField(max_length=128, blank=True, null=True)

    abstract = models.TextField(blank=True, null=True)
    accessed = models.DateField(default=datetime.now(pytz.utc))

    def __unicode__(self):
        return u'[%s]: %s' % (self.slug, self.title)

    def build_citation(self):
        """
        Formats a specific citation based on the type of reference
        """
        citation = "{0} ({1}) <i>{2}</i>".format(
            escape(self.author), escape(self.year), escape(self.title))

        if self.edition and self.edition > 1:
            citation += " " + ordinal(self.edition) + " ed"

        if self.publisher:
            citation += ". {0}{1}".format(
                escape(self.publisher), ": " + escape(self.place) if self.place else "")

        if self.url:
            citation += " [Online]. Available from  <a href='{0}'>{0}</a>".format(
                escape(self.url))

        return citation + "."

    citation = property(build_citation)
