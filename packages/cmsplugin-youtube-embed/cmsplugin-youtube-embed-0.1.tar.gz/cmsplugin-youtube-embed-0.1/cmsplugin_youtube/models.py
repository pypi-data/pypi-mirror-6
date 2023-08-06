from cms.models.pluginmodel import CMSPlugin
from django.db import models

class YoutubeVideo(CMSPlugin):
    video_name = models.CharField(max_length=50, default='Title', null=True, blank=True)
    video_link = models.CharField(max_length=255)
