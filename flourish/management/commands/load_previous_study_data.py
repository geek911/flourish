from django.core.management.base import BaseCommand
from flourish_reports.classes import GenerateStudyData


class Command(BaseCommand):
    help = 'Create dataset reports'

    def handle(self, *args, **kwargs):
        study_data = GenerateStudyData()
        study_data.populate_previous_study_data()
