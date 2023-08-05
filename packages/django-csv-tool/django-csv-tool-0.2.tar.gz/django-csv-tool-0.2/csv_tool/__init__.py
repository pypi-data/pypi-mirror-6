from django.utils.datastructures import SortedDict
import csv


class CsvSkipException(Exception):
    pass


class CsvImportTool(object):
    model = None
    fields = []
    aliases = {}

    errors = []
    count = 0

    def register_aliases(self, name, aliases):
        for alias in aliases:
            self.aliases[alias] = name

    def get_or_create(self, values):
        return self.model.objects.create()

    def save_model(self, instance, values):
        instance.save()

    def finished(self, instance, values):
        pass

    def import_from_file(self, file_object):
        self.count = 0
        self.errors = []
        for idx, row in enumerate(csv.reader(file_object)):
            if idx == 0:
                headers = []
                for header in row:
                    header = header.strip().replace(" ", "_")
                    headers.append(self.aliases.get(header, header))
            else:
                for idx, value in enumerate(row):
                    row[idx] = value.strip()
                values = dict(zip(headers, row))

                try:
                    instance = self.get_or_create(values)

                    # before save
                    for header in headers:
                        if header in self.fields:
                            func = self._import_property
                        else:
                            func = getattr(self, "import_%s" % header, None)

                        if func:
                            func(instance, values, header)

                    self.save_model(instance, values)

                    for header in headers:
                        func = getattr(self, "import_%s_after" % header, None)

                        if func:
                            func(instance, values, header)

                    self.finished(instance, values)
                    self.count_row(instance, values)
                except CsvSkipException:
                    pass

    def count_row(self, instance, values):
        self.count += 1

    # import functions
    def _import_property(self, instance, values, name):
        setattr(instance, name, values[name])


class CsvExportTool(object):
    fields = ["id", "__unicode__"]

    def export(self, queryset):
        self.errors = []

        rows = []

        # add headers
        headers = []
        for field in self.fields:
            if "." in field:
                headers.append(field.rsplit(".", 1)[-1])
            else:
                headers.append(field)
        rows.append(headers)

        # add records
        for instance in queryset:
            row = []
            self.cache = {}
            for field in self.fields:
                attr = getattr(self, "export_%s" % field, None)
                if attr:
                    attr = attr(instance)
                else:
                    attr = instance
                    for bit in field.split("."):
                        attr = getattr(attr, bit, None)
                        if not attr:
                            break

                if callable(attr):
                    attr = attr()

                row.append(attr)
            rows.append(row)

        # clean out unicode:
        from django.utils.encoding import smart_str
        for i, row in enumerate(rows):
            for j, cell in enumerate(row):
                row[j] = smart_str(cell)
            rows[i] = row
        return rows

    def export_file(self, queryset, fileh):
        writer = csv.writer(fileh)
        writer.writerows(self.export(queryset))
