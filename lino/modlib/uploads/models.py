# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Luc Saffre
# License: BSD (see file COPYING for details)
"""
Database models for `lino.modlib.uploads`.
"""
from builtins import str
from builtins import object

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.conf import settings
from django.utils.translation import string_concat
from django.utils.translation import pgettext_lazy as pgettext

from lino.api import dd, rt, _
from lino import mixins
from etgen.html import E, join_elems
from lino.modlib.gfks.mixins import Controllable
from lino.modlib.users.mixins import UserAuthored, My
from lino.modlib.office.roles import OfficeUser, OfficeStaff, OfficeOperator

from .choicelists import Shortcuts, UploadAreas
from .mixins import UploadController


class UploadType(mixins.BabelNamed):
    """The type of an upload.

    .. attribute:: shortcut

        Optional pointer to a virtual **upload shortcut** field.  If
        this is not empty, then the given shortcut field will manage
        uploads of this type.  See also :class:`Shortcuts
        <lino.modlib.uploads.choicelists.Shortcuts>`.

    """
    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'UploadType')
        verbose_name = _("Upload Type")
        verbose_name_plural = _("Upload Types")

    upload_area = UploadAreas.field(default=UploadAreas.as_callable('general'))

    max_number = models.IntegerField(
        _("Max. number"), default=-1,
        help_text=string_concat(
            _("No need to upload more uploads than N of this type."),
            "\n",
            _("-1 means no limit.")))
    wanted = models.BooleanField(
        _("Wanted"), default=False,
        help_text=_("Add a (+) button when there is no upload of this type."))

    shortcut = Shortcuts.field(blank=True)


class UploadTypes(dd.Table):
    """The table with all existing upload types.

    This usually is accessible via the `Configure` menu.
    """
    required_roles = dd.login_required(OfficeStaff)
    model = 'uploads.UploadType'
    column_names = "upload_area name max_number wanted shortcut *"
    order_by = ["upload_area", "name"]

    insert_layout = """
    name
    upload_area
    """

    detail_layout = """
    id upload_area wanted max_number shortcut
    name
    uploads.UploadsByType
    """


def filename_leaf(name):
    i = name.rfind('/')
    if i != -1:
        return name[i + 1:]
    return name


@dd.python_2_unicode_compatible
class Upload(mixins.Uploadable, UserAuthored, Controllable):
    """Represents an uploaded file.

    .. attribute:: file

        Pointer to the uploaded file. See
        :attr:`lino.mixins.uploadable.Uploadable.file`

    .. attribute:: description

        A short description entered manually by the user.

    .. attribute:: description_link

        Almost the same as :attr:`description`, but if :attr:`file` is
        not empty, the text is clickable, and clicking on it opens the
        uploaded file in a new browser window.

    """
    class Meta(object):
        abstract = dd.is_abstract_model(__name__, 'Upload')
        verbose_name = _("Upload")
        verbose_name_plural = _("Uploads")

    upload_area = UploadAreas.field(default=UploadAreas.as_callable('general'))

    type = dd.ForeignKey(
        "uploads.UploadType",
        blank=True, null=True)

    description = models.CharField(
        _("Description"), max_length=200, blank=True)

    def __str__(self):
        if self.description:
            s = self.description
        elif self.file:
            s = filename_leaf(self.file.name)
        else:
            s = str(self.id)
        if self.type:
            s = str(self.type) + ' ' + s
        return s

    @dd.displayfield(_("Description"))
    def description_link(self, ar):
        if ar is None:
            return ''
        if self.description:
            s = self.description
        elif self.file:
            s = filename_leaf(self.file.name)
        elif self.type:
            s = str(self.type)
        else:
            s = str(self.id)
        return self.get_file_button(s)

    @dd.chooser()
    def type_choices(self, upload_area):
        M = dd.resolve_model('uploads.UploadType')
        # logger.info("20140430 type_choices %s", upload_area)
        if upload_area is None:
            return M.objects.all()
        return M.objects.filter(upload_area=upload_area)

    def save(self, *args, **kw):
        if self.type is not None:
            self.upload_area = self.type.upload_area
        super(Upload, self).save(*args, **kw)


dd.update_field(Upload, 'user', verbose_name=_("Uploaded by"))


class Uploads(dd.Table):
    "Shows all Uploads"
    model = 'uploads.Upload'
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    column_names = "file type user owner description *"
    order_by = ['-id']

    detail_layout = dd.DetailLayout("""
    file user
    upload_area type description
    owner
    """, window_size=(80, 'auto'))

    insert_layout = """
    type
    description
    file
    user
    """

    parameters = mixins.ObservedDateRange(
        # user=dd.ForeignKey(
        #     'users.User', blank=True, null=True,
        #     verbose_name=_("Uploaded by")),
        upload_type=dd.ForeignKey(
            'uploads.UploadType', blank=True, null=True))
    params_layout = "start_date end_date user upload_type"

    # simple_parameters = ['user']

    @classmethod
    def get_request_queryset(cls, ar, **filter):
        qs = super(Uploads, cls).get_request_queryset(ar, **filter)
        pv = ar.param_values

        if pv.user:
            qs = qs.filter(user=pv.user)

        if pv.upload_type:
            qs = qs.filter(type=pv.upload_type)

        return qs


class AllUploads(Uploads):
    use_as_default_table = False
    required_roles = dd.login_required(OfficeStaff)


class UploadsByType(Uploads):
    master_key = 'type'
    column_names = "file description user * "


class MyUploads(My, Uploads):
    """Shows only my Uploads (i.e. those whose author is current user)."""
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    column_names = "file description user owner *"
    # order_by = ["modified"]

    # @classmethod
    # def get_actor_label(self):
    #     return _("My %s") % _("Uploads")

    # @classmethod
    # def param_defaults(self, ar, **kw):
    #     kw = super(MyUploads, self).param_defaults(ar, **kw)
    #     kw.update(user=ar.get_user())
    #     return kw

class AreaUploads(Uploads):
    required_roles = dd.login_required((OfficeUser, OfficeOperator))
    stay_in_grid = True
    # _upload_area = UploadAreas.general
    slave_grid_format = 'summary'

    # 20180119
    # @classmethod
    # def get_known_values(self):
    #     return dict(upload_area=self._upload_area)
    # @classmethod
    # def get_actor_label(self):
    #     if self._upload_area is not None:
    #         return self._upload_area.text
    #     return self._label or self.__name__

    @classmethod
    def format_row_in_slave_summary(self, ar, obj):
        """almost as unicode, but without the type
        """
        return obj.description or filename_leaf(obj.file.name) \
            or str(obj.id)

    @classmethod
    def get_slave_summary(self, obj, ar):
        """Displays the uploads related to this controller as a list grouped
        by uploads type.

        Note that this also works on
        :class:`lino_welfare.modlib.uploads.models.UploadsByClient`
        and their subclasses for the different `_upload_area`.

        """
        if obj is None:
            return
        UploadType = rt.models.uploads.UploadType
        # Upload = rt.modules.uploads.Upload
        elems = []
        types = []
        perm = ar.get_user().user_type.has_required_roles(self.required_roles)
        qs = UploadType.objects.all()
        if isinstance(obj, UploadController):
            area = obj.get_upload_area()
            if area is not None:
                qs = qs.filter(upload_area=area)
        else:
            raise Exception("A {} is not an UploadController!".format(
                obj.__class__))
                
        for ut in qs:
            sar = ar.spawn(
                self, master_instance=obj,
                known_values=dict(type_id=ut.id))
            # logger.info("20140430 %s", sar.data_iterator.query)
            files = []
            for m in sar:
                text = self.format_row_in_slave_summary(ar, m)
                if text is None:
                    continue
                edit = ar.obj2html(
                    m,  text,  # _("Edit"),
                    # icon_name='application_form',
                    title=_("Edit metadata of the uploaded file."))
                if m.file.name:
                    show = ar.renderer.href_button(
                        settings.SITE.build_media_url(m.file.name),
                        # u"\u21A7",  # DOWNWARDS ARROW FROM BAR (↧)
                        # u"\u21E8",
                        u"\u21f2",  # SOUTH EAST ARROW TO CORNER (⇲)
                        style="text-decoration:none;",
                        # _(" [show]"),  # fmt(m),
                        target='_blank',
                        # icon_name=settings.SITE.build_static_url(
                        #     'images/xsite/link'),
                        # icon_name='page_go',
                        # style="vertical-align:-30%;",
                        title=_("Open the uploaded file in a new browser window"))
                    # logger.info("20140430 %s", E.tostring(e))
                    files.append(E.span(edit, ' ', show))
                else:
                    files.append(edit)
            if perm and ut.wanted \
               and (ut.max_number < 0 or len(files) < ut.max_number):
                btn = self.insert_action.request_from(
                    sar, master_instance=obj,
                    known_values=dict(type_id=ut.id)).ar2button()
                if btn is not None:
                    files.append(btn)
            if len(files) > 0:
                e = E.p(str(ut), ': ', *join_elems(files, ', '))
                types.append(e)
        # logger.info("20140430 %s", [E.tostring(e) for e in types])
        if len(types) == 0:
            elems.append(E.ul(E.li(ar.no_data_text)))
        else:
            elems.append(E.ul(*[E.li(e) for e in types]))
        return E.div(*elems)


class UploadsByController(AreaUploads):
    "UploadsByController"
    master_key = 'owner'
    column_names = "file type description user *"

    insert_layout = """
    file
    type
    description
    """

    @classmethod
    def format_upload(self, obj):
        return str(obj.type)

@dd.receiver(dd.pre_analyze)
def before_analyze(sender, **kwargs):
    """This is the successor for `quick_upload_buttons`."""

    # remember that models might have been overridden.
    UploadType = sender.modules.uploads.UploadType
    Shortcuts = sender.modules.uploads.Shortcuts

    for i in Shortcuts.items():

        def f(obj, ar):
            if obj is None or ar is None:
                return E.div()
            try:
                utype = UploadType.objects.get(shortcut=i)
            except UploadType.DoesNotExist:
                return E.div()
            items = []
            target = sender.modules.resolve(i.target)
            sar = ar.spawn_request(
                actor=target,
                master_instance=obj,
                known_values=dict(type=utype))
                # param_values=dict(pupload_type=et))
            n = sar.get_total_count()
            if n == 0:
                iar = target.insert_action.request_from(
                    sar, master_instance=obj)
                btn = iar.ar2button(
                    None, _("Upload"), icon_name="page_add",
                    title=_("Upload a file from your PC to the server."))
                items.append(btn)
            elif n == 1:
                after_show = ar.get_status()
                obj = sar.data_iterator[0]
                items.append(sar.renderer.href_button(
                    sender.build_media_url(obj.file.name),
                    _("show"),
                    target='_blank',
                    icon_name='page_go',
                    style="vertical-align:-30%;",
                    title=_("Open the uploaded file in a "
                            "new browser window")))
                after_show.update(record_id=obj.pk)
                items.append(sar.window_action_button(
                    sar.ah.actor.detail_action,
                    after_show,
                    _("Edit"), icon_name='application_form',
                    title=_("Edit metadata of the uploaded file.")))
            else:
                obj = sar.sliced_data_iterator[0]
                items.append(ar.obj2html(
                    obj, pgettext("uploaded file", "Last")))

                btn = sar.renderer.action_button(
                    obj, sar, sar.bound_action,
                    _("All {0} files").format(n),
                    icon_name=None)
                items.append(btn)

            return E.div(*join_elems(items, ', '))

        vf = dd.VirtualField(dd.DisplayField(i.text), f)
        dd.inject_field(i.model_spec, i.name, vf)
        # logger.info("Installed upload shortcut field %s.%s",
        #             i.model_spec, i.name)

