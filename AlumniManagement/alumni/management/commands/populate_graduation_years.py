from django.core.management.base import BaseCommand
from alumni.models import Alumni, GraduationYear

class Command(BaseCommand):
    help = 'Populate GraduationYear table with unique graduation years from Alumni'

    def handle(self, *args, **kwargs):
        unique_years = Alumni.objects.values_list('graduation_year', flat=True).distinct()
        for year in unique_years:
            GraduationYear.objects.get_or_create(year=year)
        self.stdout.write(self.style.SUCCESS('GraduationYear table populated successfully.'))
