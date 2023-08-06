from media_tree.contrib.cms_plugins.media_tree_slideshow.models import MediaTreeSlideshow, MediaTreeSlideshowItem
from media_tree.contrib.cms_plugins.media_tree_listing.cms_plugins import MediaTreeListingPlugin
from media_tree.contrib.cms_plugins.media_tree_listing.models import MediaTreeListing
from media_tree.contrib.cms_plugins.forms import MediaTreePluginFormInlinePositioningBase
from media_tree.contrib.views.listing import LISTING_MERGED
from media_tree import media_types
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin


class MediaTreeSlideshowPluginForm(MediaTreePluginFormInlinePositioningBase):
    class Meta:
        model = MediaTreeSlideshow


class MediaTreeSlideshowItemInline(admin.StackedInline):
    model = MediaTreeSlideshowItem
    extra = 0
    fieldsets = [
        ('', {
            'fields': ['position', 'node']
        }),
        (_('Link'), {
            'fields': ['link_type', 'link_url', 'link_page', 'link_target'],
            'classes': ['collapse'],
        }),
    ]


class MediaTreeSlideshowPlugin(MediaTreeListingPlugin):
    model = MediaTreeSlideshow
    module = _('Media Tree')
    name = _('Slideshow')
    admin_preview = False
    render_template = 'cms/plugins/media_tree_slideshow.html'
    form = MediaTreeSlideshowPluginForm
    inlines = [MediaTreeSlideshowItemInline]
    fieldsets = [
        (_('Settings'), {
            'fields': form().fields.keys(),
            'classes': ['collapse']
        }),
    ]

    list_type = 'M'
    list_filter_media_types = (media_types.SUPPORTED_IMAGE,)

    class PluginMedia:
        js = [
            'lib/jquery.cycle/jquery.cycle.all.min.js',
        ]

    def render(self, context, instance, placeholder):
        context = super(MediaTreeSlideshowPlugin, self).render(context, instance, placeholder)
        context.update({
            'timeout': instance.timeout,
            'fx': instance.fx,
            'speed': instance.speed,
        })
        if instance.width or instance.height:
            w = instance.width or instance.height
            h = instance.height or instance.width
            context.update({'thumbnail_size': (w, h)})

        return context


plugin_pool.register_plugin(MediaTreeSlideshowPlugin)
