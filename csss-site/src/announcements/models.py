from django.db import models
from django.utils.translation import ugettext_lazy as _
from announcements import utils
from django.utils import timezone
import six


class Post(models.Model):
    subject = models.CharField(
         _(u'Subject'),
         max_length=255,
         default='NA',
    )

    from_header = models.CharField(
        _(u'Author'),
        max_length=255,
        default='NA',
    )

    body = models.TextField(
        _(u'Body'),
    )

    processed = models.DateTimeField(
        _(u'Date and Time'),
        default=timezone.now,
    )

    def __str__(self):
        return self.subject


class AnnouncementAttachment(models.Model):
    message = models.ForeignKey(
        Post,
        related_name='attachments',
        null=True,
        blank=True,
        verbose_name=_('Post'),
        on_delete=models.CASCADE
    )

    document = models.FileField(
        _(u'Document'),
        upload_to=utils.get_attachment_save_path,
    )

    def delete(self, *args, **kwargs):
        """Deletes the attachment."""
        self.document.delete()
        return super(AnnouncementAttachment, self).delete(*args, **kwargs)

    def __delitem__(self, name):
        rehydrated = self._get_rehydrated_headers()
        del rehydrated[name]
        self._set_dehydrated_headers(rehydrated)

    def __setitem__(self, name, value):
        rehydrated = self._get_rehydrated_headers()
        rehydrated[name] = value
        self._set_dehydrated_headers(rehydrated)

    def get_filename(self):
        """Returns the original filename of this attachment."""
        file_name = self._get_rehydrated_headers().get_filename()
        if isinstance(file_name, six.string_types):
            result = utils.convert_header_to_unicode(file_name)
            if result is None:
                return file_name
            return result
        else:
            return None

    def items(self):
        return self._get_rehydrated_headers().items()

    def __getitem__(self, name):
        value = self._get_rehydrated_headers()[name]
        if value is None:
            raise KeyError('Header %s does not exist' % name)
        return value

    def __str__(self):
        return self.document.url

    class Meta:
        verbose_name = _('Message attachment')
        verbose_name_plural = _('Message attachments')
