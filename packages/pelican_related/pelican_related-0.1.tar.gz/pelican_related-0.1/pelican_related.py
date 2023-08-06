import random
from collections import Counter

from pelican import signals


def add_related_posts(generator):
    posts_limit = generator.settings.get('RELATED_POSTS_LIMIT', 5)
    from_category = generator.settings.get('RELATED_POSTS_FROM_CATEGORY', True)
    from_tags = generator.settings.get('RELATED_POSTS_FROM_TAGS', True)
    shuffle = generator.settings.get('RELATED_POSTS_SHUFFLE', True)
    not_enough = generator.settings.get('RELATED_POSTS_NOT_ENOUGH', 'shuffle')
    posts_min= generator.settings.get('RELATED_POSTS_MIN', 3)

    for article in generator.articles:
        related_posts = []
        if hasattr(article,'related_posts'):
            related_posts = article.related_posts.split(',')
            for slug in related_posts:
                for a in generator.articles:
                    if a.slug == slug:
                        related_posts.append(a)
        else:
            scores = Counter()

            if from_tags and hasattr(article, 'tags'):
                for tag in article.tags:
                    scores += Counter(generator.tags[tag])

            if from_category and hasattr(article, 'category'):
                categories = dict(generator.categories)
                scores += Counter(categories[article.category])

            if scores:
                scores.pop(article)

            related_posts = [other for other, count in scores.most_common(posts_limit)]

            if len(related_posts) < posts_min:
                less = posts_min - len(related_posts)
                if not_enough == 'shuffle':
                    shuffled_articles = list(generator.articles)
                    random.shuffle(shuffled_articles)
                    related_posts += shuffled_articles[:less]
                elif not_enough == 'new':
                    related_posts += generator.articles[:less]

        if shuffle:
            random.shuffle(related_posts)

        article.related_posts = related_posts[:posts_limit]

def register():
    signals.article_generator_finalized.connect(add_related_posts)
