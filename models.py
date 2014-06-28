from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from elasticsearch import Elasticsearch
from django.conf import settings

class Author(models.Model):
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

class Media(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    imageurl = models.TextField(blank=True)
    contenturl = models.TextField(blank=True)

    BOOK = 'BK'
    AUDIOTALK = 'AT'
    VIDEOTALK = 'VT'
    PODCAST = 'PC'
    MEDIA_TYPES = (
        (BOOK, 'Book'),
        (AUDIOTALK, 'Audiotalk'),
        (VIDEOTALK, 'Videotalk'),
        (PODCAST, 'Podcast'),
    )
    media_type = models.CharField(max_length=2,
                                      choices=MEDIA_TYPES,
                                      default=BOOK)

    authors = models.ManyToManyField(Author, through='MediaAuthor')

    def __unicode__(self):
        return self.title

    def get_authors_as_string(self):
        string = ''
        first = True
        for author in self.authors.all():
            if first:
                first = False
            else:
                string += ', '

            string += author.name
        return string

class MediaAuthor(models.Model):
    author = models.ForeignKey(Author)
    media = models.ForeignKey(Media)

    def __unicode__(self):
        return self.author.name + ' - ' + self.media.title

@receiver(post_save, sender=Media)
def media_post_save_handler(sender, **kwargs):
    media = kwargs['instance']
    update_media_in_elasticsearch(media)

@receiver(post_delete, sender=Media)
def media_post_delete_handler(sender, **kwargs):
    media = kwargs['instance']
    delete_media_in_elasticsearch(media)

@receiver(post_save, sender=MediaAuthor)
def media_author_post_save_handler(sender, **kwargs):
    media_author = kwargs['instance']
    update_media_in_elasticsearch(media_author.media)

def update_media_in_elasticsearch(media):
    es = Elasticsearch()

    doc = {
        'title' : media.title,
        'description' : media.description,
        'imageurl' : media.imageurl,
        'contenturl' : media.contenturl,
        'media_type' : media.media_type,
        'authors' : media.get_authors_as_string(),
    }
    res = es.index(index=settings.ELASTICSEARCH['index'], doc_type='media', id=media.pk, body=doc)
    es.indices.refresh(index=settings.ELASTICSEARCH['index'])

def delete_media_in_elasticsearch(media):
    es = Elasticsearch()
    es.delete(index=settings.ELASTICSEARCH['index'], doc_type='media', id=media.pk)
    es.indices.refresh(index=settings.ELASTICSEARCH['index'])