# -*- coding: utf-8 -*-

import pickle
from optparse import make_option

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db.utils import DataError, IntegrityError
from socialtool.loading import get_class, get_model
from socialtool.social.management.utils import get_containing_words

SocialSearchFacade = get_class('social.facades', 'SocialSearchFacade')


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option(
            '-c', '--count', action='store', dest='post_count', type='int',
            help='Posts to import per network', default=10,
        ),
    )

    def __init__(self):
        super(Command, self).__init__()
        self.accounts = get_model('social', 'marketaccount').objects.all()

    def disable(self, post, reason='Unknown'):
        post.deleted = True
        post.entry_allowed = False
        post.disallowed_reason = reason
        post.save()

    def handle(self, *args, **kwargs):
        """
            Import for the first stored search term.
        """

        terms = get_model('social', 'searchterm').objects.filter(active=True)
        forbidden_words = get_model('social', 'forbiddenword') \
            .objects.all().values('word', 'level')
        forbidden_words = {w['word']: w['level'] for w in forbidden_words}

        for term in terms:

            for account in self.accounts:

                self.stdout.write("\nImporting %s posts on %s for account %s" % (term.term, account.type, account.handle))

                api = SocialSearchFacade(account)
                search = api.search(term.term, count=kwargs.get('post_count'))

                for post in search:

                    swearwords = get_containing_words(forbidden_words.keys(),
                                                      post.content)
                    swearword_level = None
                    if swearwords:
                        swearwords = {word: forbidden_words[word] for word
                                      in swearwords}
                        swearword_level = min(swearwords.values())

                    obj = get_model('social', 'socialpost')(
                        account=account,
                        content=post.content,
                        created_at=post.created_at,
                        followers=post.followers,
                        handle=post.handle,
                        image_url=post.image_url,
                        post_url=post.post_url,
                        uid=post.uid,
                        user_joined=post.user_joined,
                        profile_image=post.profile_image,
                        post_source=post.post_source,
                        raw_object=pickle.dumps(post._obj),
                        search_term=term,
                        swearword_level=swearword_level,
                    )

                    try:
                        post = get_model('social', 'socialpost').everything.get(uid=obj.uid)
                    except ObjectDoesNotExist:
                        obj.save()
                        self.stdout.write("Added %s (%d %s)" % (obj.uid, obj.id, obj.handle))

                        entry_count = obj.entry_count
                        if entry_count > settings.MAX_ENTRIES:
                            self.disable(obj, reason='Already entered max times (%d)' % entry_count)
                            continue
                    else:
                        self.stdout.write("Post already exists %s (%d %s)" % (post.uid, post.id, post.handle))
