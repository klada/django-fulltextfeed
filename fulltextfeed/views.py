from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from models import Feed

def show_feed(request, name):
    feed = get_object_or_404(Feed, name=name)
    return HttpResponse(feed.get_fulltext_feed(), "application/atom+xml; charset=utf-8")