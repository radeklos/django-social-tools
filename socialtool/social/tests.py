import pickle

from django.core.management import call_command
from django.test import TestCase
from mock import Mock, patch
from socialtool.loading import get_class, get_model
from socialtool.social.facades import TwitterPost
from socialtool.social.management.commands import sync
from socialtool.social.management.utils import get_containing_words


class ManagementUtilsTest(TestCase):

    def setUp(self):
        self.words = ['dog', 'cat', 'dragon']

    def test_contains_cat_and_dog(self):
        text = """
               Dogs bite a blue small Cat.
               """
        self.assertEqual(set(['dog', 'cat']),
                         get_containing_words(self.words, text))

    def test_contains_nothing(self):
        text = """
               A Gecko bites a blue small fly.
               """
        self.assertEqual(set(),
                         get_containing_words(self.words, text))


class ManagementCommandsSyncTest(TestCase):

    def setUp(self):
        get_model('social', 'forbiddenword')(word='fuck', level=0).save()
        get_model('social', 'forbiddenword')(word='hell', level=1).save()
        get_model('social', 'searchterm')(term='Fuck off', active=True).save()
        get_model('social', 'marketaccount')(type='twitter').save()

        self.pickle_patcher = patch.object(pickle, 'dumps')
        post1_mock = self.pickle_patcher.start()
        post1_mock.return_value = None

    def tearDown(self):
        self.pickle_patcher.stop()

    @patch('socialtool.social.facades.SocialSearchFacade.search')
    def test_contains_some_swearword(self, search_mock):
        search_mock.return_value = [
            Mock(
                content='fuck off hell',
                created_at='2014-08-16 12:39',
                user_joined='2000-08-16 12:39',
                followers=10,
                handle=[],
                uid='840234'
            )
        ]
        call_command('sync')
        post = get_model('social', 'socialpost').objects \
            .filter(content='fuck off hell')[0]
        self.assertEqual(0, post.swearword_level)

    @patch('socialtool.social.facades.SocialSearchFacade.search')
    def test_doesnt_contain_some_swearword(self, search_mock):
        search_mock.return_value = [
            Mock(
                content='I love unicorns',
                created_at='2014-08-16 12:39',
                user_joined='2000-08-16 12:39',
                followers=10,
                handle=[],
                uid='840234'
            )
        ]
        call_command('sync')
        post = get_model('social', 'socialpost').objects \
            .filter(content='I love unicorns')[0]
        self.assertEqual(None, post.swearword_level)
