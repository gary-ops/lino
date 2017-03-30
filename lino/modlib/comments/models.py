# -*- coding: UTF-8 -*-
# Copyright 2013-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""Database models for `lino.modlib.comments`.

"""
from builtins import str
from builtins import object

import logging
logger = logging.getLogger(__name__)

from django.utils.translation import ugettext_lazy as _
from django.contrib.humanize.templatetags.humanize import naturaltime
# from django.db import models

from lino.api import dd, rt
from lino.mixins import CreatedModified, BabelNamed
from lino.modlib.users.mixins import UserAuthored
# from lino.modlib.gfks.mixins import Controllable
from lino.modlib.notify.mixins import ChangeObservable
from lino.utils.xmlgen.html import E
from lino.mixins.bleached import Bleached
from lino.core.roles import SiteUser
# from lino.core.gfks import gfk2lookup
if dd.is_installed("inbox"):
    from lino_xl.lib.inbox.models import comment_email

try:    
    commentable_model = dd.plugins.comments.commentable_model
except AttributeError:
    commentable_model = None


class CommentType(BabelNamed):
    """The type of an upload.

    .. attribute:: shortcut

        Optional pointer to a virtual **upload shortcut** field.  If
        this is not empty, then the given shortcut field will manage
        uploads of this type.  See also :class:`Shortcuts
        <lino.modlib.uploads.choicelists.Shortcuts>`.

    """
    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'CommentType')
        verbose_name = _("Comment Type")
        verbose_name_plural = _("Comment Types")



    
    
@dd.python_2_unicode_compatible
class Comment(CreatedModified, UserAuthored, # Controllable,
              ChangeObservable, Bleached):
    """A **comment** is a short text which some user writes about some
    other database object. It has no recipient.

    .. attribute:: short_text

        A short "abstract" of your comment. This should not be more
        than one paragraph.

    """
    # ALLOWED_TAGS = ['a', 'b', 'i', 'em', 'ul', 'ol', 'li']
    bleached_fields = 'short_text more_text'
    
    class Meta(object):
        app_label = 'comments'
        abstract = dd.is_abstract_model(__name__, 'Comment')
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")

    short_text = dd.RichTextField(_("Short text"))
    owner = dd.ForeignKey(commentable_model, blank=True, null=True)
    reply_to = dd.ForeignKey(
        'self', blank=True, null=True, verbose_name=_("Reply to"))
    more_text = dd.RichTextField(_("More text"), blank=True)
    # private = models.BooleanField(_("Private"), default=False)
    comment_type = dd.ForeignKey(
        'comments.CommentType', blank=True, null=True)

    def __str__(self):
        return u'%s #%s' % (self._meta.verbose_name, self.pk)
        # return _('{user} {time}').format(
        #     user=self.user, obj=self.owner,
        #     time=naturaltime(self.modified))

    @classmethod
    def get_request_queryset(cls, ar):
        if commentable_model is None:
            return cls.objects.all()
        # if ar.get_user().profile.has_required_roles([SiteUser]):
        if ar.get_user().authenticated:
            return cls.objects.all()
        else:
            return cls.objects.exclude(owner__private=True)
        
    # def full_clean(self):
    #     super(Comment, self).full_clean()
    #     self.owner.setup_comment(self)

    def get_change_observers(self):
        if isinstance(self.owner, ChangeObservable):
            obs = self.owner
        else:
            obs = super(Comment, self)
        for u in obs.get_change_observers():
            yield u

    def get_change_subject(self, ar, cw):
        if cw is None:
            s = _("{user} commented on {obj}")
        else:
            s = _("{user} modified comment on {obj}")
        return s.format(user=ar.get_user(), obj=self.owner)
    
    def get_change_body(self, ar, cw):
        if cw is None:
            s = _("{user} commented on {obj}")
        else:
            s = _("{user} modified comment on {obj}")
        user = ar.get_user()
        s = s.format(
            user=user, obj=ar.obj2memo(self.owner))
        if dd.is_installed("inbox"):
            #mailto:ADDR@HOST.com?subject=SUBJECT&body=Filling%20in%20the%20Body!%0D%0Afoo%0D%0Abar
            s += ' <a href="{href}">{reply}</a>'.format(href=comment_email.gen_href(self, user), reply=_("Reply"))

        s += ': ' + self.short_text
        if False:
            s += '\n<p>\n' + self.more_text
        return s

    # def get_change_owner(self, ar):
    #     return self.owner

dd.update_field(Comment, 'user', editable=False)


from .ui import *

@dd.schedule_often(10)
def get_new_mail():
    for mb in rt.models.django_mailbox.Mailbox.objects.filter(active=True):
        mails = mb.get_new_mail()
        if mails:
            logger.info("got {} from mailbox: {}".format(mails,mb))
