from dateutil import parser
from django.conf import settings

from django.core.management.base import BaseCommand

from flourish_caregiver.models import CaregiverLocator, MaternalDataset, LocatorLog, LocatorLogEntry
from django.utils.timezone import make_aware
import pytz
import csv
from edc_base.utils import get_utcnow


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
                report_datetime = get_utcnow()
                # report_datetime = make_aware(report_datetime, pytz.timezone(settings.TIME_ZONE))
            except parser.ParserError:
                options.update(report_datetime=None)
            else:
                options.update(report_datetime=report_datetime)

            try:
                locator_date = parser.parse(options.get('locator_date')).date()
            except parser.ParserError:
                options.update(locator_date=None)
            else:
                options.update(locator_date=locator_date)

            locator = None
            try:
                locator = CaregiverLocator.objects.get(
                    study_maternal_identifier=data_item.get('study_maternal_identifier'))
            except CaregiverLocator.DoesNotExist:
                options.update(user_created='imosweu')
                locator = CaregiverLocator.objects.create(**options)
                created += 1
            else:
                for (key, value) in options.items():
                    setattr(locator, key, value)
                locator.save()
                already_exists += 1

            try:
                dataset = MaternalDataset.objects.get(
                    study_maternal_identifier=data_item.get('study_maternal_identifier'))
            except MaternalDataset.DoesNotExist:
                pass
            else:
                screening_identifier = getattr(dataset, 'screening_identifier')
                setattr(locator, 'screening_identifier', screening_identifier)
                locator.save()

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
        self.stdout.write(self.style.SUCCESS(f'Total locators {total_import}'))
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
            'id',
            'site',
            'site_id',
            'slug',
            'screening_identifier',
            'action_identifier',
            'tracking_identifier',
            'related_tracking_identifier',
            'parent_tracking_identifier',
            'subject_identifier']
        fields = []
        for field in CaregiverLocator._meta.get_fields():
            if field.name not in exclude_fields:
                fields.append(field.name)
        return fields
