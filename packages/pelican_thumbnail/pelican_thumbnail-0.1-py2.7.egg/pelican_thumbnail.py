from pelican import signals


def add_thumbnails(generator):
    for article in generator.articles:
        if not getattr(article, 'thumbnail', None):
            if hasattr(article, 'youtube'):
                thumbnail_url = 'http://i1.ytimg.com/vi/%s/hqdefault.jpg' % article.youtube
            if hasattr(article, 'niconico'):
                thumbnail_url = 'http://tn-skr4.smilevideo.jp/smile?i=%s' % article.niconico.replace('sm', '')

            article.thumbnail = thumbnail_url


def register():
    signals.article_generator_finalized.connect(add_thumbnails)
