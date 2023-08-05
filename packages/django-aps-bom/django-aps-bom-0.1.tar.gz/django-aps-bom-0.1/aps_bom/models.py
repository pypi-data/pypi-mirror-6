"""Models for the ``aps_bom`` app."""
import os
from csv import DictWriter

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _

import settings as app_settings


# TODO General note: attributes in docstrings, where it was not entirely clear,
# what they refer to are marked with TODO for further update.

def trunc(data, length=50):  # pragma: nocover
    """Shortcut for truncating strings."""
    return (data[:length] + '..') if len(data) > length else data


class AdditionalText(models.Model):
    """
    Additional text, that can be added to an IPN.

    :ipn: The IPN of what this text is about.
    :text: The actual text, that is attached.

    """
    ipn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('IPN'),
        related_name='additional_texts',
    )

    text = models.CharField(
        verbose_name=_('Text'),
        max_length=100,
    )

    def __unicode__(self):
        return u'Text "{0}" for {1}'.format(trunc(self.text), self.ipn.code)


class BOM(models.Model):
    """
    Bill Of Materials.

    :description: The description of this bill.
    :ipn: The IPN of what is billed.

    reverse relations:
    :bomitems: All the BOMItems on this BOM.

    """
    description = models.CharField(
        verbose_name=_('Description'),
        max_length=128,
    )

    ipn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('IPN'),
        related_name='boms',
        blank=True, null=True,
    )

    def __unicode__(self):
        if self.ipn is not None:
            ipn_code = self.ipn.code
        else:
            ipn_code = None
        return u'BOM "{0}" for {1}'.format(trunc(self.description), ipn_code)


class BOMItem(models.Model):
    """
    Details about an item, that belongs to a BOM.

    :bom: The BOM this item belongs to.
    :ipn: The IPN of this item.
    :position: The position on the list of items.
    :qty: The quantity of this item.
    :unit: The unit, that qty refers to.

    """
    bom = models.ForeignKey(
        'aps_bom.BOM',
        verbose_name=_('BOM'),
        related_name='bomitems',
    )

    ipn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('IPN'),
        related_name='bomitems',
    )

    position = models.CharField(
        verbose_name=_('Position'),
        max_length=5,
    )

    qty = models.FloatField(
        verbose_name=_('Quantity'),
    )

    unit = models.ForeignKey(
        'aps_bom.Unit',
        verbose_name=_('Unit'),
        related_name='bomitems',
    )

    def __unicode__(self):
        return u'{0} {1} of item "{2}" of BOM "{3}"'.format(
            self.qty, self.unit.code, self.ipn.code,
            trunc(self.bom.description))


class CBOM(models.Model):
    """
    Customer Bill Of Materials.

    :customer: The customer this bill belongs to.
    :description: A description of the product.
    :html_link: TODO
    :product: The name of the product.
    :version_date: The date of this version of the bill.

    reverse relations:
    :cbomitems: All the CBOMItems on this BOM

    """
    customer = models.ForeignKey(
        'aps_bom.Company',
        verbose_name=_('Customer'),
        related_name='cboms',
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=128,
    )

    html_link = models.URLField(
        verbose_name=_('HTML link'),
        max_length=256,
        blank=True,
    )

    product = models.CharField(
        verbose_name=_('Product'),
        max_length=100,
    )

    version_date = models.DateField(
        verbose_name=_('Version date'),
    )

    def __unicode__(self):
        return u'{0} from "{1}" ({2})'.format(
            self.product, self.customer.description, self.version_date)

    def get_bom(self):
        """Converts this CBOM into a matching BOM."""
        return BOM(description=self.description)

    def get_bom_csv_file(self):
        """
        Returns the url for a BOM.csv file created from this CBOM instance.

        """
        file_name = 'BOM_{0}.csv'.format(self.id)
        path = os.path.join(settings.MEDIA_ROOT, file_name)
        with open(path, 'w') as f:
            csv_writer = DictWriter(f, app_settings.BOM_CSV_FIELDNAMES)
            csv_writer.writeheader()
            clean_list = []
            # for each bomitem...
            for bomitem in self.get_bom_items():
                # ... create a dictionary
                bomitem_dict = model_to_dict(bomitem)
                # ... clean the values
                clean_dict = {}
                for fieldname in app_settings.BOM_CSV_FIELDNAMES:
                    if fieldname.lower() == 'description':
                        clean_dict.update({fieldname: bomitem.ipn.name})
                    elif fieldname.lower() == 'ipn':
                        clean_dict.update({fieldname: bomitem.ipn.code})
                    elif fieldname.lower() == 'shape':
                        clean_dict.update({fieldname: bomitem.ipn.shape.code})
                    elif fieldname.lower() == 'unit':
                        clean_dict.update({fieldname: bomitem.unit.code})
                    else:
                        clean_dict.update({
                            fieldname: bomitem_dict[fieldname.lower()]})
                # ... append the dict to the list
                clean_list.append(clean_dict)
            #... and write the entire list of dicts to the file
            csv_writer.writerows(clean_list)
        return os.path.join(settings.MEDIA_URL, file_name)

    def get_bom_items(self):
        """Converts all CBOMItems into matching BOMItems."""
        bomitems = []
        bom = self.get_bom()
        for cbomitem in self.cbomitems.all():
            if cbomitem.consign:
                ipn = cbomitem.epn.cpn
            else:
                ipn = cbomitem.epn.ipn
            bomitems.append(BOMItem(bom=bom, ipn=ipn,
                                    position=cbomitem.position,
                                    qty=cbomitem.qty, unit=cbomitem.unit))
        return bomitems


class CBOMItem(models.Model):
    """
    Details about the items, that belong to a CBOM.

    :bom: The CBOM this item belongs to.
    :consign: Whether to use the IPN or CPN, when translating it into BOMItem.
      True means use CPN, False therefore uses the IPN of the EPN.
    :epn: The external part number of of this item.
    :position: The position of this item on th CBOM list of items.
    :qty: The quantity of this item on the list.
    :unit: The unit qty refers to.

    """

    bom = models.ForeignKey(
        'aps_bom.CBOM',
        verbose_name=_('CBOM'),
        related_name='cbomitems',
    )

    consign = models.BooleanField(
        verbose_name=_('Consign'),
        default=True,
    )

    epn = models.ForeignKey(
        'aps_bom.EPN',
        verbose_name=_('EPN'),
        related_name='cbomitems',
    )

    position = models.CharField(
        verbose_name=_('Position'),
        max_length=5,
    )

    qty = models.FloatField(
        verbose_name=_('Quantity'),
    )

    unit = models.ForeignKey(
        'aps_bom.Unit',
        verbose_name=_('Unit'),
        related_name='cbomitems',
    )

    def __unicode__(self):
        return u'{0} {1} of item "{2}" of CBOM "{3}"'.format(
            self.qty, self.unit.code, self.epn, trunc(self.bom.description))


class Company(models.Model):
    """
    Holds basic information about a company.

    :country: The country, this company is in.
    :code: A short identifier for this company.
    :description: Full company description (name).

    reverse relations:
    :cboms: All the CBOMs related to this company.
    :epns: All the EPNs from this country.

    """
    country = models.ForeignKey(
        'aps_bom.Country',
        verbose_name=_('Country'),
        related_name='companies',
    )

    code = models.CharField(
        verbose_name=_('Code'),
        max_length=10,
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=128,
    )

    def __unicode__(self):
        return u'Customer "{0}"'.format(self.description)


class Country(models.Model):
    """
    Information about a country.

    :code: Country code.
    :description: Full country description (name).

    reverse relations:
    :companies: All the companies in this country.

    """
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=2,
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=128,
    )

    def __unicode__(self):
        return self.description


class EPN(models.Model):
    """
    External Part Number.

    :company: The company this EPN is belongs to.
    :cpn: Cosign Part Number.
    :description: The part description
    :epn: The actual part number as string.
    :ipn: Internal Part Number.

    reverse relations:
    :cbomitems: All the CBOM items, that have this EPN.

    """
    company = models.ForeignKey(
        Company,
        verbose_name=_('Company'),
        related_name='epns',
    )

    cpn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('CPN'),
        related_name='cpns',
        blank=True, null=True,
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=128,
    )

    epn = models.CharField(
        verbose_name=_('EPN'),
        max_length=50,
    )

    ipn = models.ForeignKey(
        'aps_bom.IPN',
        verbose_name=_('IPN'),
        related_name='ipns',
        blank=True, null=True,
    )

    def __unicode__(self):
        if self.ipn is not None:
            code = self.ipn.code
        else:
            code = None
        return u'EPN "{0}" from "{1}" (IPN: {2})'.format(
            self.epn, self.company.description, code)


class IPN(models.Model):
    """
    Internal Part Number.

    :code: The actual part number.
    :name: A name for this IPN.
    :price_group: The price group, this IPN is in.
    :shape: TODO
    :price_max: The maximum price.

    reverse relations:
    :additional_texts: The list of AdditionalText objects attached.
    :boms: The BOM objects this is part of.
    :cpns: The EPN objects this was assigned as a CPN.
    :ipns: The EPN objects this was assigned as an IPN.
    :price_markers: All the price markers of this IPN.

    """
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=50,
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=128,
    )

    price_group = models.ForeignKey(
        'aps_bom.PriceGroup',
        verbose_name=_('Price group'),
        related_name='ipns',
    )

    shape = models.ForeignKey(
        'aps_bom.Shape',
        verbose_name=_('Shape'),
        related_name='ipns',
    )

    price_max = models.DecimalField(
        verbose_name=_('Price max'),
        max_digits=11,
        decimal_places=3,
    )

    def __unicode__(self):
        return u'{0} - IPN: {1}'.format(self.name, self.code)


class PriceGroup(models.Model):
    """
    The price group of a part.

    :add: The fixed price addition, that applies to this price group.
    :code: A single character representing the price group.
    :rate: A decimal representing the rate to multiply with the
      IPN.price_marker. TODO

    reverse relations:
    :ipns: All the IPNs that have this price group.

    """
    add = models.DecimalField(
        verbose_name=_('Add'),
        max_digits=10,
        decimal_places=5,
        default=Decimal('0.00000'),
    )

    code = models.CharField(
        verbose_name=_('Code'),
        max_length=1,
    )

    rate = models.DecimalField(
        verbose_name=_('Rate'),
        max_digits=10,
        decimal_places=5,
        default=Decimal('1.00000'),
    )

    def __unicode__(self):
        return u'{0} - Rate: {1} - Add: {1}'.format(
            self.code, self.rate, self.add)


class PriceMarker(models.Model):
    """
    TODO

    :ipn: The IPN this price marker belongs to.
    :price: The price this marker defines.
    :date: The date when/from/until this is valid. TODO

    """
    ipn = models.ForeignKey(
        IPN,
        verbose_name=_('Ipn'),
        related_name='price_markers',
    )

    price = models.DecimalField(
        verbose_name=_('Price'),
        max_digits=10,
        decimal_places=5,
    )

    date = models.DateField(
        verbose_name=_('Date'),
    )

    def __unicode__(self):
        return u'{0} - IPN: {1} - Date: {2}'.format(
            self.price, self.ipn.code, self.date)


class Shape(models.Model):
    """
    TODO

    :code: The code of this shape.
    :name: The name/description of this shape.

    reverse relations:
    :ipns: All the IPNs that have this shape.

    """

    code = models.CharField(
        verbose_name=_('Code'),
        max_length=10,
    )

    name = models.CharField(
        verbose_name=_('Name'),
        max_length=200,
    )

    def __unicode__(self):
        return u'Shape: {0}'.format(self.name)


class Unit(models.Model):
    """
    The unit a qty can be in. (see e.g. BOMItem)

    :code: The code of this unit.
    :description: The descriptive name of this unit.

    related:
    :cbomitems: All the CBOMItems, that have this unit.
    :bomitems: All the BOMItems, that have this unit.

    """
    code = models.CharField(
        verbose_name=_('Code'),
        max_length=5,
    )

    description = models.CharField(
        verbose_name=_('Description'),
        max_length=20,
    )

    def __unicode__(self):
        return u'Unit: {0} ({1})'.format(self.code, self.description)
