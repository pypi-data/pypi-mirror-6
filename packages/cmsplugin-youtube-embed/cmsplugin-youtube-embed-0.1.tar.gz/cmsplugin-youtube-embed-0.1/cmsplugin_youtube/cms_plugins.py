from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.models.pluginmodel import CMSPlugin

from models import YoutubeVideo

class YoutubeEmbedPlugin(CMSPluginBase):
    model = YoutubeVideo
    name = "Youtube Embed Plugin"
    render_template = "embed_video.html"

    def render(self, context, instance, placeholder):
        v = instance.video_link.split("=")
        instance.code = v[1]
        context.update({
            'placeholder': placeholder,
            'object': instance
        })
        return context

plugin_pool.register_plugin(YoutubeEmbedPlugin)
