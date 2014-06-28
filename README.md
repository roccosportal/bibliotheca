## python dependencies

available via pip
* `python-amazon-product-api`
* `lxml`
* `elasticsearch`

## other dependencies

* `django`
* `elasticsearch`

## elasticsearch

`curl -XPUT 'localhost:9200/bibliotheca/' -d '{json}'`

```json
{
    "settings" : {
        "number_of_shards": 1,
        "analysis" : {
            "filter":{
                "compoundngram_filter": {
                    "type":     "ngram",
                    "min_gram": 5,
                    "max_gram": 5
                }

            },
            "analyzer": {
                "compoundngram": {
                    "type":      "custom",
                    "tokenizer": "standard",
                    "filter":   [
                        "lowercase",
                        "compoundngram_filter"
                    ]
                }
            }

        }
    },
    "mappings" : {
        "media" : {
            "properties" : {
                "contenturl": {
                    "type": "string",
                    "index" : "no"
                },
                "imageurl": {
                    "type": "string",
                    "index" : "no"
                },
                "media_type" : {
                    "type" : "string",
                    "index" : "not_analyzed"
                },
                "description" : {
                    "type" : "string",
                    "analyzer" : "german",
                    "fields" : {
                        "compoundngram" : {
                            "type" : "string",
                            "analyzer" : "compoundngram"
                        }
                    }
                },
                "title" : {
                    "type" : "string",
                    "analyzer" : "german",
                    "fields" : {
                        "compoundngram" : {
                            "type" : "string",
                            "analyzer" : "compoundngram"
                        }
                    }
                }
            }
        }
    }
}
```

## django

settings.py

```python
AWS_CONFIG = {
    'access_key': 'access_key',
    'secret_key': 'secret_key',
    'associate_tag': 'none',
    'locale': 'de'
}

MAX_ITEM_COUNT = 3

ELASTICSEARCH = {
    'index' : 'bibliotheca'
}

INSTALLED_APPS = (
    'bibliotheca',
)

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]
```

urls.py
```python
from bibliotheca.admin import isbnsearch_view, addbookfromamazon_view

from bibliotheca import views

# ...

urlpatterns = patterns('',
    url(r'^$', views.index, name = 'index'),
    url(r'^api/get-all/(?P<page>\d+)', views.api_get_all),
    url(r'^api/find/(?P<page>\d+)', views.api_find),
    url(r'^admin/search-book-by-isbn/', isbnsearch_view, name = 'isbnsearch'),
    url(r'^admin/add-book-from-amazon/', addbookfromamazon_view, name = 'addbookfromamazon'),
    url(r'^admin/', include(admin.site.urls))
)
```
