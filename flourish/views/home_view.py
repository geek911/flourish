from django.apps import apps as django_apps
from django.db.models import Q
from django.views.generic import TemplateView
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcBaseViewMixin, NavbarViewMixin, TemplateView):
    template_name = 'flourish/home.html'
    navbar_name = 'flourish'
    navbar_selected_item = 'home'

    subject_consent_model = 'flourish_caregiver.subjectconsent'

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    maternal_dataset_model = 'flourish_caregiver.maternaldataset'

    caregiver_offstudy_model = 'flourish_prn.caregiveroffStudy'

    child_offstudy_model = 'flourish_prn.childoffstudy'

    antenatal_enrollment_model = 'flourish_caregiver.antenatalenrollment'

    maternal_delivery_model = 'flourish_caregiver.maternaldelivery'

    @property
    def maternal_delivery_cls(self):
        return django_apps.get_model(self.maternal_delivery_model)

    @property
    def antenatal_enrollment_cls(self):
        return django_apps.get_model(self.antenatal_enrollment_model)

    @property
    def child_offstudy_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def caregiver_offstudy_cls(self):
        return django_apps.get_model(self.caregiver_offstudy_model)

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    @property
    def subject_consent_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    @property
    def maternal_dataset_cls(self):
        return django_apps.get_model(self.maternal_dataset_model)

    @property
    def total_flourish_consents(self):
        """Returns flourish consents.
        """
        return self.subject_consent_cls.objects.values_list('subject_identifier').distinct().count()

    @property
    def total_child_assents(self):
        child_assent_cls = django_apps.get_model('flourish_child.childassent')
        return child_assent_cls.objects.values_list('subject_identifier').distinct().count()

    @property
    def total_child_consents(self):
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')
        return child_consent_cls.objects.values_list('subject_identifier').distinct().count()

    @property
    def total_continued_consents(self):
        continued_consent_cls = django_apps.get_model(
            'flourish_child.childcontinuedconsent')
        return continued_consent_cls.objects.values_list('subject_identifier').distinct().count()

    @property
    def total_caregiver_prev_study(self):
        """
        Caregivers from previous BHP studies Currently on-Study
        """
        metadataset_screening_identifier = self.maternal_dataset_cls.objects.values_list(
            'screening_identifier', flat=True).distinct()

        caregiver_offstudy_subject_identifier = self.caregiver_offstudy_cls.objects.values_list(
            'subject_identifier', flat=True)

        subject_consents = self.subject_consent_cls.objects.filter(
            Q(screening_identifier__in=metadataset_screening_identifier) & ~Q(
                subject_identifier__in=caregiver_offstudy_subject_identifier)).values_list(
            'subject_identifier', flat=True).distinct().count()
        return subject_consents

    @property
    def total_child_prev(self):
        """
        Children from previous BHP studies Currently on-Study
        """
        child_offstudy_subject_identifiers = self.child_offstudy_cls.objects.values_list(
            'subject_identifier', flat=True).distinct()

        total_children = self.caregiver_child_consent_cls.objects.filter(
            Q(study_child_identifier__isnull=False) & ~Q(
                subject_identifier__in=child_offstudy_subject_identifiers)).count()

        return total_children

    @property
    def total_all_preg_women(self):
        """
        All women who consented when pregnant (on and off study)
        """

        return self.antenatal_enrollment_cls.objects.values_list(
            'subject_identifier').distinct().count()

    @property
    def total_consented_pregnant_women(self):
        """
        All women who consented when pregnant – Currently ON- study
        """

        maternal_offstudy_subject_identifiers = self.caregiver_offstudy_cls.objects.values_list(
            'subject_identifier', flat=True).distinct()

        all_consented_women = self.antenatal_enrollment_cls.objects.exclude(
            subject_identifier__in=maternal_offstudy_subject_identifiers).values_list(
                'subject_identifier', flat=True).distinct().count()
        return all_consented_women

    @property
    def total_currently_pregnant_women(self):
        """
        Currently Pregnant Women On-Study
        """

        maternal_offstudy_subject_identifiers = self.caregiver_offstudy_cls.objects.values_list(
            'subject_identifier', flat=True).distinct()

        maternal_delivery_subject_identifiers = self.maternal_delivery_cls.objects.values_list(
            'subject_identifier', flat=True).distinct()

        currently_preg = self.antenatal_enrollment_cls.objects.exclude(
            Q(subject_identifier__in=maternal_offstudy_subject_identifiers) |
            Q(subject_identifier__in=maternal_delivery_subject_identifiers)).values_list(
                'subject_identifier', flat=True).distinct().count()

        return currently_preg

    @property
    def total_maternal_delivery(self):
        """
        Newly recruited (not from previous BHP studies) women enrolled in pregnancy who
         gave birth who are currently On-Study
        """

        return self.maternal_delivery_cls.objects.values_list('subject_identifier',
                                                              flat=True).distinct().count()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            flourish_consents=self.total_flourish_consents,
            flourish_assents=self.total_child_assents,
            child_consents=self.total_child_consents,
            continued_consents=self.total_continued_consents,
            total_caregiver_prev_study=self.total_caregiver_prev_study,
            total_child_prev=self.total_child_prev,
            total_all_preg_women=self.total_all_preg_women,
            total_consented_pregnant_women=self.total_consented_pregnant_women,
            total_currently_pregnant_women=self.total_currently_pregnant_women,
            total_maternal_delivery=self.total_maternal_delivery
        )
        return context
