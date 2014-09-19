bibliotheca = {
    MAX_TEXT_LENGTH : 470,
    currentPage : 1,
    pages : 0
}
bibliotheca.media_types = {
    selected : function(){
        types = ''
        $("#search-options input").each(function(key, element){
            if ($(element).is(':checked')){
                types += $(element).val() + ','
            }
        })
        return types
    },
    to_glyphicon : function(media_type){
        switch(media_type){
            case 'BK':
                return 'glyphicon-book'
            case 'AT':
                return 'glyphicon-headphones'
            case 'VT':
                return 'glyphicon-play-circle'
            case 'PC':
                return 'glyphicon-bullhorn'
            case 'MV':
                return 'glyphicon-facetime-video'
        }
        return ''
    },
    to_image_url : function(media_type){
        switch(media_type){
            case 'BK':
                return IMG_BK_URL
            case 'AT':
                return IMG_AT_URL
            case 'VT':
                return IMG_VT_URL
            case 'PC':
                return IMG_PC_URL
            case 'MV':
                return IMG_MV_URL
        }
        return ''
    }
}

bibliotheca.media_query = {
    last_query : {},
    get : function(search, media_types){
        if (search!=''){
            this.by_query(search, 1, media_types)
        }
        else {
            this.all(1, media_types)
        }
    },
    all : function(page, media_types){
        $.getJSON("api/get-all/" + page, {
            'media_types' : media_types
        }, this.handle_request)

        this.last_query = {
            'type' : 'get-all',
            'page' : page,
            'media_types' : media_types
        }
    },
    by_query : function(q, page, media_types){
        $.getJSON("api/find/" + page, {
            'q' : q,
            'media_types' : media_types
        }, this.handle_request)

        this.last_query = {
            'type' : 'find',
            'page' : page,
            'q' : q,
            'media_types' : media_types
        }
    },
    handle_request : function(data){
        bibliotheca.media.show_medias(data.items)
        bibliotheca.currentPage = data.current_page
        bibliotheca.pages = data.pages
        bibliotheca.pagination.create()
        bibliotheca.result_message.update(data.pages, data.total_items)
    },
    rerun_with_different_page : function(page){
        if (page > 0 && page <= bibliotheca.pages && this.last_query != {}){
            if(this.last_query.page != page){
                if (this.last_query.type=='get-all'){
                    this.all(page)
                }
                if (this.last_query.type=='find'){
                    this.by_query(this.last_query.q,page, this.last_query.media_types)
                }
            }
        }
    }
}
bibliotheca.media = {
    show_medias : function(medias){
         // clear list
        $('#medias.media-list li').remove()

        $.each(medias, function(i, media){
            $media_html = bibliotheca.media.prepare_html(media)
            $media_html.appendTo('#medias.media-list')
        })
    },
    prepare_html : function(media){
        $media_html = $('#template-media .media').clone()
        $media_html.find('.media-body .media-heading').html(media.title)

        media_tags = media.tags.split(',')
        media_tags_string =  media_tags.join(' #')
        if(media_tags_string != ''){
            media_tags_string = '#' + media_tags_string
        }

        media_subheader = media.authors + ' ' + media_tags_string + ' <span class="glyphicon ' + bibliotheca.media_types.to_glyphicon(media.media_type) +'"></span>'
        $media_html.find('.media-body small').html(media_subheader)

        media_description = media.description
        media_description = media_description.replace(/\r\n/g, '<br />')
        if(media_description.length > bibliotheca.MAX_TEXT_LENGTH){
            beginning = media_description.slice(0, bibliotheca.MAX_TEXT_LENGTH)
            ending = media_description.slice(bibliotheca.MAX_TEXT_LENGTH)
            middle = '<a class="media-text-show-full" href="#">[...]</a><span style="display:none" class="media-text-full">'
            very_ending = '</span>'
            media_description = beginning + middle + ending + very_ending
        }


        $media_html.find('.media-body p').html(media_description)
        $media_html.find('.media-body p .media-text-show-full').click(function(e){
            e.preventDefault()
            $(this).hide()
            $(this).parents('.media-body').find('.media-text-full').show()
        })

        imageurl = media.imageurl
        if(imageurl==''){
           imageurl = bibliotheca.media_types.to_image_url(media.media_type)
        }

        $media_html.find('.media-object').attr('src', imageurl)

        contenturl = media.contenturl
        if(contenturl==''){
            contenturl = 'javascript:;'
        }
        $media_html.find('a.pull-left').attr('href', contenturl)

        return $media_html
    }
}
bibliotheca.pagination = {
    $pagination : null,
    $page_template : $('#template-pagination .page'),
    init : function(){
        this.$pagination = $('#pagination')
        this.$page_template = $('#template-pagination .page')

        this.$pagination.find('li').first().click(function(e){
            e.preventDefault()
            bibliotheca.media_query.rerun_with_different_page(bibliotheca.currentPage - 1)
        })

        this.$pagination.find('li').last().click(function(e){
            e.preventDefault()
            bibliotheca.media_query.rerun_with_different_page(bibliotheca.currentPage + 1)
        })
    },
    create : function(){

        if(bibliotheca.pages > 1){
            this.$pagination.show()
        }
        else {
            this.$pagination.hide()
        }
        // remove all old pages
        this.$pagination.find('.page').remove()

        for (var page = 1; page <= bibliotheca.pages; page++) {
            this.add_page(page)
        }
        if(bibliotheca.currentPage == 1){
            this.$pagination.find('li').first().addClass('disabled')
        }
        else {
            this.$pagination.find('li').first().removeClass('disabled')
        }
        if(bibliotheca.currentPage == bibliotheca.pages){
            this.$pagination.find('li').last().addClass('disabled')
        }
        else {
            this.$pagination.find('li').last().removeClass('disabled')
        }
    },
    add_page : function(page){
        $page = this.$page_template.clone()
        $page.find('a').html(page)

        if(bibliotheca.currentPage == page){
            $page.addClass('active')
        }

        $page.click(function(e){
            e.preventDefault()
            bibliotheca.media_query.rerun_with_different_page(page)
        })

        // append the $page before the last li (which is the 'next' pointer)
        this.$pagination.find('li').last().before($page)
    }
}

bibliotheca.result_message = {
    $result_message : null,
    result_message_template : 'Seite {page} von {itemCount} Ergebnissen',
    init : function(){
        this.$result_message = $('.result-message')
    },
    update : function(pages, itemCount){
        if(pages < 2){
            this.$result_message.hide()
        }
        else {
            result_message = this.result_message_template.replace('{page}', bibliotheca.currentPage).replace('{itemCount}', itemCount)
            this.$result_message.html(result_message)
            this.$result_message.show()
        }
    }
}

bibliotheca.search_input = {
    $search : null,
    init : function(){
        $search = $("#search")
        $search.keypress(function(event){
            var keycode = (event.keyCode ? event.keyCode : event.which)
            if(keycode == '13'){
                bibliotheca.media_query.get($search.val(), bibliotheca.media_types.selected())
            }
        })
        $("#search-options input").change(function(){
            // get medias again
            bibliotheca.media_query.get($search.val(), bibliotheca.media_types.selected())
        })
        $('.extended-search-toggle').click(function(e){
            e.preventDefault()
            if($('.extended-search-toggle .glyphicon').hasClass('glyphicon-chevron-down')){
                $('.extended-search-toggle .glyphicon').removeClass('glyphicon-chevron-down')
                $('.extended-search-toggle .glyphicon').addClass('glyphicon-chevron-up')
            }
            else {
                $('.extended-search-toggle .glyphicon').removeClass('glyphicon-chevron-up')
                $('.extended-search-toggle .glyphicon').addClass('glyphicon-chevron-down')
            }

            $('.extended-search').toggle()
        })
    }
}

bibliotheca.init = function(){
    bibliotheca.search_input.init()
    bibliotheca.pagination.init()
    bibliotheca.result_message.init()
    bibliotheca.media_query.all(1)
}
