from django.core.management.base import BaseCommand, CommandError
from bibliotheca.models import Media
from elasticsearch import Elasticsearch
from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = 'Refreshes the elastic search index'

    def handle(self, *args, **options):
        medias = Media.objects.all()
        es = Elasticsearch()
        for media in medias:


            self.stdout.write('Refreshing %s' % media.title)

            doc = {
                'title' : media.title,
                'description' : media.description,
                'imageurl' : media.imageurl,
                'contenturl' : media.contenturl,
                'media_type' : media.media_type,
                'tags' : media.tags,
                'authors' : media.get_authors_as_string(),
            }
            res = es.index(index=settings.ELASTICSEARCH['index'], doc_type='media', id=media.pk, body=doc)

        es.indices.refresh(index=settings.ELASTICSEARCH['index'])

        self.stdout.write('Successfully refreshed')
