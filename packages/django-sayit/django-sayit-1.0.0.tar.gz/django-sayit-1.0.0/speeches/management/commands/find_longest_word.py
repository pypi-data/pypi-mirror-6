import string
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from speeches.models import Speaker
from instances.models import Instance

class Command(BaseCommand):
    help = 'Find the longest word per speaker'
    option_list = BaseCommand.option_list + (
        make_option('--commit', action='store_true', help='Whether to commit to the database or not'),
        make_option('--instance', action='store', help='Label of instance to query'),
    )

    def make(self, cls, **kwargs):
        s = cls(instance=self.instance, **kwargs)
        if self.commit:
            s.save()
        elif s.title:
            print s.title
        return s

    def handle(self, *args, **options):
        try:
            self.instance = Instance.objects.get(label=options['instance'])
        except:
            raise CommandError("Instance not specified, or not found")

        self.commit = options['commit']

        for speaker in Speaker.objects.for_instance(self.instance):
            longest = ''
            for speech in speaker.speech_set.all():
                words = [ w.strip(string.punctuation) for w in speech.text.split() ]
                longest_word = max(words, key=len)
                if not longest or len(longest) < len(longest_word):
                    longest = longest_word
            print speaker, longest
