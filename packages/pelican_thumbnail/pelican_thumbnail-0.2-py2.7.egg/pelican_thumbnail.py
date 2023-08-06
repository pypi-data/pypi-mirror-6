from pelican import signals


def youtube_thumbnail(youtube, type):
    return 'http://i1.ytimg.com/vi/%s/%s.jpg' % (youtube, type)


def add_thumbnails(generator):
    for article in generator.articles:
        if not getattr(article, 'thumbnail', None):
            if hasattr(article, 'youtube'):
                youtube_id = article.youtube
                article.thumbnail = youtube_thumbnail(youtube_id, 'hqdefault')
                article.thumbnail_hq = youtube_thumbnail(youtube_id, 'hqdefault')
                article.thumbnail_mq = youtube_thumbnail(youtube_id, 'mqdefault')
                article.thumbnail_sq = youtube_thumbnail(youtube_id, 'sqdefault')
                article.thumbnail_maxres = youtube_thumbnail(youtube_id, 'maxresdefault')
            if hasattr(article, 'niconico'):
                article.thumbnail = 'http://tn-skr4.smilevideo.jp/smile?i=%s' % article.niconico.replace('sm', '')


def register():
    signals.article_generator_finalized.connect(add_thumbnails)
