# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext_noop

from openslides.participant.models import User


class Keypad(models.Model):
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        unique=True,
        verbose_name=_('Participant'),
        help_text=_('Leave this field blank for anonymous keypad.'),
    )
    keypad_id = models.IntegerField(unique=True, verbose_name=_('Keypad ID'))
    active = models.BooleanField(default=True, verbose_name=_('Active'))

    def __unicode__(self):
        if self.user is not None:
            return _('Keypad from %s') % self.user
        return _('Keypad %d') % self.keypad_id

    @models.permalink
    def get_absolute_url(self, link='edit'):
        if link == 'edit':
            return ('votecollector_keypad_edit', [str(self.id)])
        if link == 'delete':
            return ('votecollector_keypad_delete', [str(self.id)])

    class Meta:
        permissions = (
            ('can_manage_votecollector', ugettext_noop('Can manage VoteCollector')),
        )
