"""
sentry.models.alert
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2013 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from datetime import timedelta

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from sentry.constants import (
    STATUS_RESOLVED, STATUS_UNRESOLVED, MINUTE_NORMALIZATION
)
from sentry.db.models import (
    Model, GzippedDictField, BoundedPositiveIntegerField, sane_repr
)
from sentry.utils.db import has_trending
from sentry.utils.http import absolute_uri


class Alert(Model):
    project = models.ForeignKey('sentry.Project')
    group = models.ForeignKey('sentry.Group', null=True)
    datetime = models.DateTimeField(default=timezone.now)
    message = models.TextField()
    data = GzippedDictField(null=True)
    related_groups = models.ManyToManyField('sentry.Group', through='sentry.AlertRelatedGroup', related_name='related_alerts')
    status = BoundedPositiveIntegerField(default=0, choices=(
        (STATUS_UNRESOLVED, _('Unresolved')),
        (STATUS_RESOLVED, _('Resolved')),
    ), db_index=True)

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_alert'

    __repr__ = sane_repr('project_id', 'group_id', 'datetime')

    # TODO: move classmethods to manager
    @classmethod
    def get_recent_for_project(cls, project_id):
        return cls.objects.filter(
            project=project_id,
            group_id__isnull=True,
            datetime__gte=timezone.now() - timedelta(minutes=60),
            status=STATUS_UNRESOLVED,
        ).order_by('-datetime')

    @classmethod
    def maybe_alert(cls, project_id, message, group_id=None):
        from sentry.models import Group

        now = timezone.now()
        manager = cls.objects
        # We only create an alert based on:
        # - an alert for the project hasn't been created in the last 30 minutes
        # - an alert for the event hasn't been created in the last 60 minutes

        # TODO: there is a race condition if we're calling this function for the same project
        if manager.filter(
                project=project_id, datetime__gte=now - timedelta(minutes=60)).exists():
            return

        if manager.filter(
                project=project_id, group=group_id,
                datetime__gte=now - timedelta(minutes=60)).exists():
            return

        alert = manager.create(
            project_id=project_id,
            group_id=group_id,
            datetime=now,
            message=message,
        )

        if not group_id and has_trending():
            # Capture the top 5 trending events at the time of this error
            related_groups = Group.objects.get_accelerated([project_id], minutes=MINUTE_NORMALIZATION)[:5]
            for group in related_groups:
                AlertRelatedGroup.objects.create(
                    group=group,
                    alert=alert,
                )

        return alert

    @property
    def team(self):
        return self.project.team

    @property
    def is_resolved(self):
        return (self.status == STATUS_RESOLVED
                or self.datetime < timezone.now() - timedelta(minutes=60))

    def get_absolute_url(self):
        return absolute_uri(reverse('sentry-alert-details', args=[
            self.team.slug, self.project.slug, self.id]))


class AlertRelatedGroup(Model):
    group = models.ForeignKey('sentry.Group')
    alert = models.ForeignKey(Alert)
    data = GzippedDictField(null=True)

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_alertrelatedgroup'
        unique_together = (('group', 'alert'),)

    __repr__ = sane_repr('group_id', 'alert_id')
