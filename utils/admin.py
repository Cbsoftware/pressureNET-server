import csv

from django.http import HttpResponse
from django.template.defaultfilters import slugify


class CSVAdminMixin(object):
    """
    Adds a CSV export action to an admin view.
    """
    
    # This is the maximum number of records that will be written.
    # Exporting massive numbers of records should be done asynchronously.
    csv_record_limit = 1000
    
    extra_csv_fields = ()
    
    def get_actions(self, request):
        actions = self.actions if hasattr(self, 'actions') else []
        actions.append('csv_export')
        actions = super(CSVAdminMixin, self).get_actions(request)
        return actions
    
    def get_extra_csv_fields(self, request):
        return self.extra_csv_fields
    
    def csv_export(self, request, qs=None, *args, **kwargs):

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' \
            % slugify(self.model.__name__)
        headers = list(self.list_display) + list(self.get_extra_csv_fields(request))
        writer = csv.DictWriter(response, headers)
        
        # Write header.
        header_data = {}
        for name in headers:
            if hasattr(self, name) \
            and hasattr(getattr(self, name), 'short_description'):
                header_data[name] = getattr(
                    getattr(self, name), 'short_description')
            else:
                field = self.model._meta.get_field_by_name(name)
                if field and field[0].verbose_name:
                    header_data[name] = field[0].verbose_name
                else:
                    header_data[name] = name
            header_data[name] = header_data[name].title()
        writer.writerow(header_data)
        
        # Write records.
        for r in qs[:self.csv_record_limit]:
            data = {}
            for name in headers:
                if hasattr(r, name):
                    data[name] = getattr(r, name)
                elif hasattr(self, name):
                    data[name] = getattr(self, name)(r)
                else:
                    raise Exception, 'Unknown field: %s' % (name,)
                    
                if callable(data[name]):
                    data[name] = data[name]()
            writer.writerow(data)
        return response
    csv_export.short_description = \
        'Export selected %(verbose_name_plural)s as CSV'
