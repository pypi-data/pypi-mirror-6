"""Settings for the aps_bom app."""
from django.conf import settings

# default for the headlines in the csv file
BOM_CSV_FIELDNAMES = getattr(settings, 'APS_BOM_BOM_CSV_FIELDNAMES',
                             ["Position", "IPN", "Description", "QTY", "Unit",
                              "Shape"])
