from ...models import Job
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Runs all jobs that are due.'
    
    def handle(self, *args, **options):
        try:
            for job in Job.objects.due():
                job.run()
        except:
            import traceback
            traceback.print_exc()
            raise
