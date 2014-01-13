import twitter
from datetime import datetime
from django.views.generic import TemplateView
from rest_framework import viewsets
from models import Message, MarketAccount, Tweet
from serializers import MessageSerializer, MarketAccountSerializer

class TweetUserView(TemplateView):
    template_name = 'tweet_user.html'

    def send_tweet(self):
        tweet_pk = self.request.GET['tweet_pk']
        msg = self.request.GET['msg']

        tweet = Tweet.objects.get(pk=tweet_pk)

        try:
            api = twitter.Api(
                consumer_key='aJsLPnXasjoWXW99cbG0lg',
                consumer_secret='DxW4hggyUqiwGhGfnzldX57BgBcx7RIpB8fBUDRoM',
                access_token_key='2272873393-Ig34VvEWmD4HN66bgNlZrRE7JfFmcndZvxzB116',
                access_token_secret='ZqMNHKhNQNLfikntnbP6MevM7I1aftHeBtBR0W2Rkibrx',
            )

            # If we have an included media file then attach and send that
            # otherwise we post a regular Update instead - that is we're
            # not going by the message content!
            if tweet.photoshop:
                status = api.PostMedia('{!s}'.format(msg), tweet.photoshop.file.name)
            else:
                status = api.PostUpdate('{!s}'.format(msg))

            # Update the tweet itself now
            tweet.tweeted = True
            tweet.tweet_id = status.id
            tweet.sent_tweet = msg
            tweet.tweeted_by = self.request.user
            tweet.tweeted_at = datetime.now()
            tweet.save()

        except twitter.TwitterError:
            status = None

        return status

    def get_context_data(self, **kwargs):
        context = super(TweetUserView, self).get_context_data(**kwargs)
        context['tweet'] = self.send_tweet()
        return context

    def get(self, *args, **kwargs):
        return super(TweetUserView, self).get(*args, **kwargs)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_fields = ('type', 'account',)

class MarketAccountViewSet(viewsets.ModelViewSet):
    queryset = MarketAccount.objects.all()
    serializer_class = MarketAccountSerializer
