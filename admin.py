from django.contrib import admin
from bibliotheca.models import Media, Author, MediaAuthor
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from amazonproduct import API
from amazonproduct.errors import AWSError
from django.core.urlresolvers import reverse
import urllib
from django.contrib.auth.decorators import login_required
from django.conf import settings



class AuthorInline(admin.TabularInline):
    model = Media.authors.through

class MediaAdmin(admin.ModelAdmin):
    inlines = (AuthorInline,)

admin.site.register(Author)
admin.site.register(Media, MediaAdmin)
admin.site.register(MediaAuthor)

@login_required(login_url='/admin/')
def isbnsearch_view(request):
    error_message = ''
    isbn = ''
    if 'isbn' in request.POST:
        isbn = request.POST['isbn']
        isbn = isbn.strip()
        try:
            api = API(cfg=settings.AWS_CONFIG)
            result = api.item_lookup(isbn, SearchIndex='Books', IdType='ISBN', ResponseGroup='ItemAttributes,Images, EditorialReview')

            # only take first item
            item = result.Items.Item

            description = ''
            if hasattr(item, 'EditorialReviews') and hasattr(item.EditorialReviews, 'EditorialReview'):
                description = item.EditorialReviews.EditorialReview

            url = reverse('addbookfromamazon')
            parameters = {
                'title' :  item.ItemAttributes.Title,
                'author' : item.ItemAttributes.Author,
                'description' : description,
                'imageurl' : item.MediumImage.URL,
                'contenturl' : 'http://asin.info/a/' + item.ASIN
            }

            # urlencode expects data in str format and doesn't deal well with unicode data
            # since it doesn't provide a way to specify an encoding
            # http://stackoverflow.com/questions/3121186/error-with-urlencode-in-python

            str_parameters = {}
            for k, v in parameters.iteritems():
                # convert the unicode value to utf-8 encoded str
                str_parameters[k] = unicode(v).encode('utf-8')


            url += '?' + urllib.urlencode(str_parameters)
            return HttpResponseRedirect(url)
        except AWSError, e:
            error_message = e.msg
        except AttributeError:
            error_message = 'Amazon did not deliver all information. Please add manually.'


    template = loader.get_template('bibliotheca/admin/isbnsearch.html')
    context = RequestContext(request, {
        'isbn' : isbn,
        'error_message' : error_message
    }, current_app = admin.site.name)
    return HttpResponse(template.render(context))

@login_required(login_url='/admin/')
def addbookfromamazon_view(request):
    if 'save' in request.POST:
        # try to find existing author
        authors = Author.objects.filter(name=request.POST['author'])
        if authors:
             author = authors[0]
        else:
            # add non existing author
            author = Author(name=request.POST['author'])
            author.save()

        # add media
        media = Media(
                title=request.POST['title'],
                description=request.POST['description'],
                imageurl=request.POST['imageurl'],
                contenturl=request.POST['contenturl'],
            )

        media.save()

        # connect media with author
        media_author = MediaAuthor(media=media, author=author)
        media_author.save()

        # redirect to admin
        # fixme: use reverse()
        return HttpResponseRedirect('/admin/bibliotheca/media/' + str(media.pk) + '/')


    template = loader.get_template('bibliotheca/admin/addbookfromamazon.html')
    context = RequestContext(request, {
        'title' : request.GET['title'],
        'author' : request.GET['author'],
        'description' : request.GET['description'],
        'imageurl' : request.GET['imageurl'],
        'contenturl' : request.GET['contenturl']
    }, current_app = admin.site.name)
    return HttpResponse(template.render(context))