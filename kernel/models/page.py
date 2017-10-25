from django.core.cache import cache
from django.utils.html import strip_tags
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.template.defaultfilters import truncatechars_html
# Import over module
from stdimage.models import StdImageField
from ckeditor_uploader.fields import RichTextUploadingField
# Import kernel module
from kernel.utils import upload_dir, slugify
from kernel import managers as kman
from kernel.models.base import KernelByModel


__all__ = [
    'KernelPage',
]

IMAGE_VARIATIONS = {
            'promotion': (775, 275, True),
            'large': (600, 400, True),
            'thumbnail': (75, 75, True),
            'medium': (300, 200, True)
}

@python_2_unicode_compatible
class KernelPage(KernelByModel):
    HIDDEN_STATUS = -1
    DRAFT_STATUS = 0
    PUBLISHED_STATUS = 1

    STATUS_CHOICES = (
        (HIDDEN_STATUS, 'Hidden'),
        (DRAFT_STATUS, 'Draft'),
        (PUBLISHED_STATUS, 'Published')
    )

    publisher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    title = models.CharField(_(u'Заголовок'), max_length=255)
    longtitle = models.CharField(_(u'Расширенный заголовок'), blank=True, max_length=255)
    keywords = models.CharField(_(u'Ключевые слова'), blank=True, max_length=255)
    description = models.CharField(_(u'Описание'), blank=True, max_length=255)
    slug = models.CharField(
        _('URL'), help_text=_('Использовать в качестве урла транскрипцию ключевых слов'),
        max_length=140, unique=True, blank=True
    )
    image = StdImageField(
        upload_to=upload_dir,
        null=True, blank=True,
        variations=IMAGE_VARIATIONS,
    )
    introtext = models.TextField(verbose_name=_(u'Аннотация'))
    content = RichTextUploadingField(verbose_name=_(u'Статья'))

    status = models.IntegerField(_(u'Статус'), choices=STATUS_CHOICES, default=DRAFT_STATUS)
    comment_enabled = models.BooleanField(_('comment enabled'), default=True)

    views = models.IntegerField(default=0)

    objects = models.Manager()
    published = kman.PublishedManager()

    class Meta:
        ordering = ['-created_date']
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        cache.clear()
        obj = super(KernelPage, self).save(*args, **kwargs)
        return obj

    @classmethod
    def list_display(cls):
        return 'id',  'title', 'longtitle', 'status',

    @classmethod
    def list_fieldsets(cls):
        return (
           (_('Основная информация'), {'fields': ('longtitle', 'title', 'publisher', ('slug', 'status'), 'image', 'introtext', 'content')}),
           (_('SEO'), {'fields': ('keywords', 'description')}),
           #(_('Дополнительно'), {'fields': ('order', )}),
        )

    @property
    def word_count(self):
        return len(strip_tags(self.content))

    @property
    def get_content(self):
        return self.content

    @property
    def get_introtext(self):
        return truncatechars_html(self.introtext, 80)