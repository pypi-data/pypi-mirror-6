"""
sentry.models.useroption
~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from datetime import timedelta
from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from sentry.db.models import Model, sane_repr
from sentry.utils.http import absolute_uri


class LostPasswordHash(Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, unique=True)
    hash = models.CharField(max_length=32)
    date_added = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_lostpasswordhash'

    __repr__ = sane_repr('user_id', 'hash')

    def save(self, *args, **kwargs):
        if not self.hash:
            self.set_hash()
        super(LostPasswordHash, self).save(*args, **kwargs)

    def set_hash(self):
        import hashlib
        import random

        self.hash = hashlib.md5(str(random.randint(1, 10000000))).hexdigest()

    def is_valid(self):
        return self.date_added > timezone.now() - timedelta(days=1)

    def send_recover_mail(self):
        from sentry.utils.email import MessageBuilder

        context = {
            'user': self.user,
            'domain': urlparse(settings.SENTRY_URL_PREFIX).hostname,
            'url': absolute_uri(reverse(
                'sentry-account-recover-confirm',
                args=[self.user.id, self.hash]
            )),
        }
        msg = MessageBuilder(
            subject='%sPassword Recovery' % (settings.EMAIL_SUBJECT_PREFIX,),
            template='sentry/emails/recover_account.txt',
            context=context,
        )

        try:
            msg.send([self.user.email])
        except Exception, e:
            logger = logging.getLogger('sentry.mail.errors')
            logger.exception(e)
