from django.core.management.base import NoArgsCommand
from fulltextfeed.models import Feed

class Command(NoArgsCommand):
    help = "Loads new articles for all feeds"

    def handle_noargs(self, **options):
        for feed in Feed.objects.all():
            self.stdout.write("Updating %s" %feed)
            feed.get_fulltext_feed()