class ClientUI
    constructor: () ->
        @root = $('#root')
        @goDirectoryList()

        # DEBUG
        @currentDirectoryId = 1
        #@goBrowse('/home/eugeny/source/P2-dvcpro25/CONTENTS/VIDEO/')
        @goBrowse('/home/eugeny/source/P2-dvcpro25/CONTENTS/VIDEO/000000.MXF ')

    replace_view: (html) ->
        @root.html(html)

    go: (url, callback) ->
        $.get(
            '/media/ajax/' + url,
            (html) =>
                @replace_view(html)
                callback()
        )

    goDirectory: (id) ->
        @currentDirectoryId = id
        @goBrowse('/')
        return
        @go "directory/#{id}", () =>
            @root.find('#go-back').click () =>
                @goDirectoryList()
            @root.find('#go-browse').click () =>
                @goBrowse('/')

    goDirectoryList: () ->
        @go 'directory-list', () =>
            @root.find('a').each (i, e) =>
                $(e).click () =>
                    @goDirectory($(e).attr('data-id'))

    reloadComments: () ->
        $.get(
            "/media/ajax/browse/#{@currentDirectoryId}/#{@currentPath}?comments"
            (html) =>
                $('#comments').html(html)
        )
        
    goBrowse: (path) ->
        @currentPath = path
        @go "browse/#{@currentDirectoryId}/#{path}", () =>
            if path == '/'
                @root.find('#go-up').hide()
                path = ''
            else
                @root.find('#go-up').click () =>
                    components = path.split('/')
                    components = components.splice(0, components.length - 1)
                    path = components.join('/')
                    @goBrowse(path)

            @root.find('a.browse-item').each (i, e) =>
                $(e).click () =>
                    path = path + '/' + $(e).attr('data-id')
                    @goBrowse(path)

            if $('video')
                video = $('video')[0]
                video.addEventListener 'timeupdate', () =>
                    ts = video.currentTime
                    h = Math.floor(ts / 3600)
                    m = Math.floor(ts / 60 % 60)
                    s = Math.floor(ts % 60)
                    ms = Math.floor(ts * 1000 % 1000)

                    ts = h + ':' + (if m < 10 then '0' else '') + m + ':' + (if s < 10 then '0' else '') + s + '.' +
                                (if ms < 100 then '0' else '') + (if ms < 10 then '0' else '') + ms

                    $('.timestamp').text(ts)

                $('a[data-time]').click () ->
                    t = parseFloat($(this).attr('data-time'))
                    video.currentTime = t

                @reloadComments()

                $('.comment-form a').click () =>
                    text = $('.comment-form input').val()
                    $('.comment-form input').val('')

                    $.post "/media/ajax/browse/#{@currentDirectoryId}/#{path}", {comment: text, time: video.currentTime}, (e) =>
                        @reloadComments()
                        e.preventDefault()


$ () ->
    new ClientUI()
