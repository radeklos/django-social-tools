from django.contrib import admin
from django.utils.safestring import mark_safe
from models import Tweet, SearchTerm, Message, MarketAccount
from filters import TwitterImageFilter, TweetStatusFilter, TongueGraphicFilter

# Register your models here.

def mark_deleted(modeladmin, request, queryset):
    queryset.update(deleted=True)
mark_deleted.short_description = 'Hide selected tweets'

def mark_approved(modeladmin, request, queryset):
    queryset.update(approved=True)
mark_approved.short_description = 'Mark selected tweets as approved'


class BaseAdmin(admin.ModelAdmin):

    class Media:
        js = ('js/tweet_admin.js', )
        css = {
            'all': ('css/adi051.css', )
        }


class MessageAdmin(BaseAdmin):
    list_display = ('account', 'type', 'copy')


class TweetAdmin(BaseAdmin):
    search_fields = ('handle', 'content',)
    list_display = ('created_at', 'get_handle', 'account', 'get_image', 'get_autophotoshop', 'get_photoshop', 'content', 'messages', 'tweeted_by', 'artworker', 'notes')
    list_filter = ('account', TweetStatusFilter, TwitterImageFilter, TongueGraphicFilter)
    list_editable = ('notes', )

    actions = [mark_deleted, ]

    fieldsets = (
        ('Attach your photoshop', {
            'fields': ('photoshop', ),
        }),
        ('View/change autophotoshop', {
            'classes': ('collapse', ),
            'fields': ('auto_photoshop', ),
        }),
        ('Tweet data', {
            'classes': ('collapse', ),
            'fields': ('created_at', 'handle', 'account', 'content', 'image_url', 'notes', )
        }),
        ('Sent data', {
            'classes': ('collapse', ),
            'fields': ('artworker', 'tweeted_by', 'tweeted_at', 'tweet_id', 'sent_tweet', )
        }),
    )

    def get_image(self, obj):
        if obj.image_url:
            if 'twitpic' in obj.image_url:
                url = 'http://twitpic.com/show/thumb/{}'.format(obj.image_url.split('/')[-1])
            else:
                url = obj.image_url

            return mark_safe('<a href="{0}" target="_blank"><img src="{1}" width=100 /></a>'.format(obj.image_url, url))
        else:
            return "N/A"
    get_image.short_description = 'Original Image'

    def get_handle(self, obj):
        return mark_safe("""
            <p><a href="http://twitter.com/{0}" target="_blank">{0}</a></p>
            <p><em>({1} Followers)
        """.format(obj.handle.encode('utf-8'), obj.followers))
    get_handle.short_description = 'User\'s Handle'

    def messages(self, obj):
        return mark_safe("""
            <ul class="message-btns">
                <li><a class="btn btn-danger send_tweet" data-msgtype="tryagain">Image doesn't work</a></li>
                <li><a class="btn btn-success send_tweet" data-msgtype="imagelink">Tweet tongue graphic</a></li>
            </ul>
        """)
    messages.short_description = 'Tweet back to user'

    def get_photoshop(self, obj):
        if obj.photoshop:
            return mark_safe('<a href="{0}" target="_blank"><img src={0} width=100 /></a>'.format(obj.photoshop.url))
        else:
            return mark_safe('<a class="btn btn-warning" href="/tweets/tweet/{}">Upload</a>'.format(obj.id))
    get_photoshop.short_description = 'Tongue Graphic'

    def get_autophotoshop(self, obj):
        if obj.auto_photoshop:
            return mark_safe('<a href="{0}" target="_blank"><img src={0} width=100 /></a>'.format(obj.auto_photoshop.url))
        else:
            return mark_safe('N/A')
    get_autophotoshop.short_description = 'Automatic Graphic'

    def save_model(self, request, obj, form, change):
        obj.artworker = request.user
        obj.save()

    def get_actions(self, request):
        actions = super(TweetAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(Tweet, TweetAdmin)
admin.site.register(SearchTerm, BaseAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(MarketAccount, BaseAdmin)
