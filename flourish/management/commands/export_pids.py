import csv

from django.core.management import BaseCommand
from flourish_caregiver.models import *


class Command(BaseCommand):
    help = '''\
    Used to extract all the subject identifiers,
    from both the caregiver and the child
    '''

    # constants that will be used as choices
    CHILD_PIDS = 'child'
    CAREGIVER_PIDS = 'caregiver'

    def add_arguments(self, parser):
        # were the user will specify the path including the name e.g. ~/example
        parser.add_argument('--path',
                            type=str,
                            required=True,
                            help='Specify export path')

        # to store the type of pids which should be extracted
        parser.add_argument('--type',
                            type=str,
                            choices=(self.CHILD_PIDS, self.CAREGIVER_PIDS),
                            required=True,
                            help='choose either caregiver or child')

    def handle(self, *args, **options):

        # path of the csv
        file_path = options['path']

        # type of the csv, child or caregiver
        subject_identifier_type = options['type']

        # hold of subject identifier
        subject_identifiers = []

        if subject_identifier_type == self.CHILD_PIDS:

            subject_identifiers = CaregiverChildConsent.objects.values_list(
                'subject_identifier', flat=True).distinct()

        else:

            subject_identifiers = SubjectConsent.objects.values_list(
                'subject_identifier', flat=True).distinct()

        Command.file_writer(file_path, subject_identifiers)

    @staticmethod
    def file_writer(file_path, subject_identifiers):

        with open(file_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(['subject_identifier_pk'])
            for subject_identifier in subject_identifiers:
                writer.writerow([subject_identifier])
