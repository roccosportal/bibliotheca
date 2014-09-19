from django.shortcuts import render
import json
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from bibliotheca.models import Media
from django.conf import settings

def index(request):
    return render(request, 'bibliotheca/index.html', {})

def api_get_all(request, page):
    page = int(page)

    es = Elasticsearch()
    allowed_media_types = [Media.BOOK, Media.AUDIOTALK, Media.VIDEOTALK, Media.PODCAST, Media.MOVIE]
    if 'media_types' in request.GET:
        # split string "BK,AT," into array at "," and remove empty itemes
        allowed_media_types = filter(None,request.GET['media_types'].split(','))
    body = {
        "from" : (page - 1) * settings.MAX_ITEM_COUNT,
        "size" : settings.MAX_ITEM_COUNT,
        # "query": {
        #     "match_all": {}
        # }
        "query" : {
            "filtered" : {
                "query" : {
                    "match_all" : {}
                },
                "filter" : {
                        "terms" : { "media_type" : allowed_media_types}
                }
            }
        }
    }
    res = es.search(index='bibliotheca', body=body)
    response_data = prepare_search_response(res, page)


    return HttpResponse(json.dumps(response_data), content_type="application/json")

def api_find(request, page):
    page = int(page)

    response_data = {}
    response_data['error'] = True

    if not 'q' in request.GET:
        response_data['message'] = 'Parameter "q" missing'
    else:
        q = request.GET['q']

        allowed_media_types = [Media.BOOK, Media.AUDIOTALK, Media.VIDEOTALK, Media.MOVIE]
        if 'media_types' in request.GET:
            # split string "BK,AT," into array at "," and remove empty itemes
            allowed_media_types = filter(None,request.GET['media_types'].split(','))

        es = Elasticsearch()
        body = {
            "from" : (page - 1) * settings.MAX_ITEM_COUNT,
            "size" : settings.MAX_ITEM_COUNT,
            # "query": {
            #     "dis_max": {
            #         "queries": [
            #             { "match": { "authors": q }},
            #             { "match": { "title":  q }},
            #             { "match": { "description":  q }}
            #         ],
            #         "tie_breaker": 0.3
            #     }
            # }

            "query": {

                "filtered" : {
                    "query" : {
                        # "fuzzy_like_this" : {
                        #     "fields" : ["authors", "title", "description"],
                        #     "like_text" : q,
                        #     "max_query_terms" : 12
                        # }

                        # "query_string": {
                        #     "query" :  q
                        # }


                        "multi_match" : {
                            "query" : q,
                            #"fuzziness" :     1,
                            #"type": "cross_fields",
                            #"type": "phrase",
                            "fields" : ["authors^2", "title^4", "tags^4", "description^2", "description.compoundngram", "title.compoundngram", "tags.compoundngram"],
                            "tie_breaker" : 0.3,
                            #"minimum_should_match": "80%",
                            #"operator":   "or"

                        }
                    },
                    "filter" : {
                        "terms" : { "media_type" : allowed_media_types}
                    }
                }
                # "multi_match" : {
                #     "query" : q,
                #     "type": "phrase_prefix",
                #     "fields" : ["authors", "title^2", "description"],
                #     "tie_breaker" : 0.3
                # }
            }
        }
        res = es.search(index='bibliotheca', body=body)
        response_data = prepare_search_response(res,page)
        #response_data = res

    return HttpResponse(json.dumps(response_data), content_type="application/json")

def prepare_search_response(search_res, page):
    response_data = {}
    response_data['total_items'] = search_res['hits']['total'];
    response_data['pages'] = search_res['hits']['total'] / settings.MAX_ITEM_COUNT

    # add one page for items that do not fill a whole page
    if search_res['hits']['total'] % settings.MAX_ITEM_COUNT:
        response_data['pages'] += 1

    response_data['current_page'] = page

    response_data['items'] = []
    for media in search_res['hits']['hits']:
        media_src =  media["_source"]
        media_src['id'] = media["_id"]
        response_data['items'].append(media_src)

    response_data['error'] = False

    return response_data
