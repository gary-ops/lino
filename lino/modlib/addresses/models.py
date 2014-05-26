# Copyright 2014 Luc Saffre
# This file is part of the Lino project.
# Lino is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
The :xfile:`models.py` module of the :mod:`lino.modlib.addresses` app.

Defines the following actors:

- the :class:`ml.addresses.Address` model
- the :class:`ml.addresses.DataSources` choicelist
- the the :class:`ml.addresses.AddressTypes` choicelist

"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _

from lino import dd
from lino.utils.xmlgen.html import E
from lino.modlib.countries.models import AddressLocation


class AddressTypes(dd.ChoiceList):
    verbose_name = _("Address type")
    verbose_name_plural = _("Address types")

add = AddressTypes.add_item
add('01', _("Official address"), 'official')  # IT020
add('02', _("Unverified address"), 'unverified')  # IT042
add('03', _("Declared address"), 'declared')  # IT214
add('04', _("Reference address"), 'reference')


class DataSources(dd.ChoiceList):
    verbose_name = _("Data source")
    verbose_name_plural = _("Data sources")

add = DataSources.add_item
add('01', _("Manually entered"), 'manually')
add('02', _("Read from eID"), 'eid')


class AddressOwner(dd.Model):
    "See :class:`ml.addresses.AddressOwner`."
    class Meta:
        abstract = True

    def get_primary_address(self):
        # Address = dd.modules.addresses.Address
        # AddressTypes = dd.modules.addresses.AddressTypes
        # ADDRESS_FIELDS = dd.modules.addresses.ADDRESS_FIELDS

        kw = dict(partner=self, primary=True)
        try:
            return Address.objects.get(**kw)
        except Address.DoesNotExist:
            kw.update(address_type=AddressTypes.official)
            has_values = False
            for fldname in Address.ADDRESS_FIELDS:
                v = getattr(self, fldname)
                kw[fldname] = v
                if v:
                    has_values = True
            if has_values:
                addr = Address(**kw)
                addr.full_clean()
                addr.save()
                return addr

    def get_overview_elems(self, ar):
        elems = super(AddressOwner, self).get_overview_elems(ar)
        sar = ar.spawn('addresses.AddressesByPartner',
                       master_instance=self)
        # btn = sar.as_button(_("Manage addresses"), icon_name="wrench")
        btn = sar.as_button(_("Manage addresses"))
        # elems.append(E.p(btn, align="right"))
        elems.append(E.p(btn))
        return elems
    
    def sync_primary_address(self, request):
        Address = dd.modules.addresses.Address
        watcher = dd.ChangeWatcher(self)
        kw = dict(partner=self, primary=True)
        try:
            pa = Address.objects.get(**kw)
            for k in Address.ADDRESS_FIELDS:
                setattr(self, k, getattr(pa, k))
        except Address.DoesNotExist:
            pa = None
            for k in Address.ADDRESS_FIELDS:
                fld = self._meta.get_field(k)
                setattr(self, k, fld.get_default())
        self.save()
        watcher.send_update(request)


class Address(AddressLocation):

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")

    data_source = DataSources.field(
        editable=False, default=DataSources.manually)
    address_type = AddressTypes.field(blank=True, null=True)
    partner = dd.ForeignKey(
        'contacts.Partner',
        related_name='addresses_by_partner')
    remark = dd.CharField(_("Remark"), max_length=50, blank=True)

    primary = models.BooleanField(
        _("Primary"),
        default=False,
        help_text=_(
            "Checking this field will automatically uncheck any "
            "previous primary addresses and update "
            "the partner's address data fields."))

    allow_cascaded_delete = ['partner']

    def __unicode__(self):
        return self.address_location(', ')

    def after_ui_save(self, ar):
        super(Address, self).after_ui_save(ar)
        mi = self.partner
        if mi is None:
            return
        if self.primary:
            for o in mi.addresses_by_partner.exclude(id=self.id):
                if o.primary:
                    o.primary = False
                    o.save()
                    ar.set_response(refresh_all=True)
        mi.sync_primary_address(ar.request)


Address.ADDRESS_FIELDS = dd.fields_list(
    Address,
    'street street_no street_box addr1 addr2 zip_code city region country')


@dd.receiver(dd.pre_ui_delete, sender=Address)
def clear_partner_on_delete(sender=None, request=None, **kw):
    self = sender
    mi = self.partner
    if mi:
        mi.sync_primary_address(request)


class Addresses(dd.Table):
    model = 'addresses.Address'
    required = dd.required(user_level='admin')
    column_names = (
        "partner address_type:10 remark:10 "
        "address_column:30 primary data_source *")
    insert_layout = """
    country city
    street street_no street_box
    address_type remark
    """
    detail_layout = dd.FormLayout("""
    country city zip_code
    addr1
    street street_no street_box
    addr2
    address_type remark
    data_source partner
    """, window_size=(60, 'auto'))


class AddressesByPartner(Addresses):
    required = dd.required()
    master_key = 'partner'
    column_names = 'address_type:10 remark:10 address_column:30 primary:5'
    label = _("Addresses")
    auto_fit_column_widths = True
    stay_in_grid = True
    window_size = (80, 20)

    # slave_grid_format = 'summary'

    # @classmethod
    # def get_slave_summary(self, obj, ar):
    #     return obj.get_overview_elems(ar)

config = dd.apps.contacts


def setup_explorer_menu(site, ui, profile, m):
    m = m.add_menu(config.app_label, config.verbose_name)
    m.add_action('addresses.AddressTypes')
    m.add_action('addresses.Addresses')


__all__ = [
    'AddressTypes',
    'DataSources',
    'AddressOwner',
    'Address',
    'Addresses',
    'AddressesByPartner']  # 'ADDRESS_FIELDS']
