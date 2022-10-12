from dateutil import parser
from django.conf import settings

from django.core.management.base import BaseCommand

from flourish_caregiver.models import LocatorLog, LocatorLogEntry
from django.utils.timezone import make_aware
import pytz
import csv


class Command(BaseCommand):
    help = 'Create caregiver locators'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str,
                            help='Data fine path, csv file')

    def handle(self, *args, **kwargs):
        already_exists = 0
        created = 0
        file_path = kwargs['file_path']
        data = self.data(file_path=file_path)

        for data_item in data:
            options = {}
            for field_name in self.all_model_fields:
                options[field_name] = data_item.get(field_name)

            # Convert date to date objects
            try:
                report_datetime = parser.parse(options.get('report_datetime'))
                report_datetime = make_aware(report_datetime, pytz.timezone(settings.TIME_ZONE))
            except parser.ParserError:
                options.update(report_datetime=None)
            else:
                options.update(report_datetime=report_datetime)

            try:
                date_created = parser.parse(options.get('date_created')).date()
            except parser.ParserError:
                options.update(date_created=None)
            else:
                options.update(date_created=date_created)

            locatorlogentry = LocatorLogEntry.objects.filter(
                locator_log__maternal_dataset__study_maternal_identifier=data_item.get(
                    'study_maternal_identifier'))
            if not locatorlogentry:
                try:
                    locatorlog = LocatorLog.objects.get(
                        maternal_dataset__study_maternal_identifier=data_item.get(
                            'study_maternal_identifier'))
                except LocatorLog.DoesNotExist:
                    pass
                else:
                    options.update(locator_log=locatorlog)
                    locatorlogentry = LocatorLogEntry.objects.create(**options)
                    created += 1
            else:
                already_exists += 1

        self.stdout.write(self.style.SUCCESS(f'A total of {created} have been created'))
        self.stdout.write(self.style.WARNING(f'Total items {already_exists} already existed'))

    def data(self, file_path=None):
        data = []
        total_import = 0
        csv_file = open(file_path, mode='r')
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
            total_import += 1
        self.stdout.write(self.style.SUCCESS(f'Total locators log entries {total_import}'))
        return data

    @property
    def all_model_fields(self):
        """Returns a list of caregiver locator model fields.
        """
        exclude_fields = [
            'created',
            'modified',
            'user_created',
            'user_modified',
            'hostname_created',
            'hostname_modified',
            'revision',
            'device_created',
            'device_modified',
            'locator_log_id',
            'id']
        fields = []
        for field in LocatorLogEntry._meta.get_fields():
            if field.name not in exclude_fields:
                fields.append(field.name)
        return fields
