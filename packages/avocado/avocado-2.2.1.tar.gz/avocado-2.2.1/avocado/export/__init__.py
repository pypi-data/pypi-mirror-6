from avocado.core import loader
from avocado.conf import OPTIONAL_DEPS
from _csv import CSVExporter
from _sas import SASExporter
from _r import RExporter
from _json import JSONExporter
from _html import HTMLExporter      # noqa

registry = loader.Registry(register_instance=False)

registry.register(CSVExporter, 'csv')
registry.register(SASExporter, 'sas')
registry.register(RExporter, 'r')
registry.register(JSONExporter, 'json')
# registry.register(HTMLExporter, 'html')

if OPTIONAL_DEPS['openpyxl']:
    from _excel import ExcelExporter
    registry.register(ExcelExporter, 'excel')

loader.autodiscover('exporters')
