from encodings.aliases import aliases
import datetime
from lxml import etree
import urllib2
import re
from django.core.urlresolvers import reverse
from django.db import models
from django.dispatch import receiver
from django.utils.feedgenerator import Atom1Feed
import feedparser

PATTERN_CDATA = re.compile('<!\[cdata\[(.*)\]\]>', re.DOTALL)
PATTERN_COMMENT = re.compile('<!--(.*)-->', re.DOTALL)
PATTERN_HTTP_URI_BASE = re.compile('^http[s]?://\w[\.\w]+')

def get_available_charsets():
    charsets = set()
    for i in aliases.values():
        i = i.replace('_', '-')
        charsets.add(i)
    charsets = list(charsets)
    charsets.sort()
    return [(i,i) for i in charsets]

class Feed(models.Model):
    # Purge articles from the database, which are more than 7 days old and are missing
    # from the source feed.
    PURGE_AGE = 7
    
    name = models.CharField(db_index=True,
                        help_text="This name is also used for addressing the fulltext feed through the URL.",
                        max_length=50,
                        verbose_name="Feed name")
    source = models.URLField(
        help_text="The source (remote) RSS feed which should be parsed and handled.",
        verbose_name="Source URL"
    )
    xpath_expression = models.CharField(
        help_text="The XPath query which will be used to extract the text from the site where the RSS feed points to.",
        max_length=254,
        verbose_name="XPath expression"
    )
    article_charset = models.CharField(
        choices=get_available_charsets(),
        default="utf-8",
        help_text="When loading the full-text articles we'll need to know their character set, so you can specifiy it here.",
        max_length=32,
        verbose_name="Source article charset"
    )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("fulltextfeed_show", args=[self.name])

    def get_fulltext_feed(self):
        source = feedparser.parse(self.source)
        
        articles = {}
        for i in self.article_set.all():
            articles[i.link] = i
        pks = []
        
        feed = Atom1Feed(
            title=source.feed.title,
            link=source.feed.link,
            description=source.feed.description
        )
        for entry in source.entries:
            if entry.link not in articles:
                a = Article()
                a.feed = self
                a.link = entry.link
                a.save()
            else:
                a = articles[entry.link]
            pks.append(a.id)                
                
            feed.add_item(
                title=entry.title,
                link=entry.link,
                description=a.text,
                pubdate=datetime.datetime(*entry.published_parsed[:6])
            )
        min_delete_datetime = datetime.datetime.now() - datetime.timedelta(days=self.PURGE_AGE)
        self.article_set.filter(
            added__lt=min_delete_datetime
        ).exclude(
            id__in=pks
        ).delete()
        return feed.writeString('utf-8')
    

class Article(models.Model):
    feed = models.ForeignKey(Feed)
    link = models.URLField(blank=False)
    text = models.TextField(blank=True, editable=False)
    added = models.DateTimeField(auto_now_add=True)

    def _refresh_text(self):
        """
        Reloads the article from the web, applies the appropriate XPath
        query and stores the result in the text field.
        """
        print "loading %s..." %self.link
        uri_base = PATTERN_HTTP_URI_BASE.findall(self.link)[0]
        uri_base += '/'
        response = urllib2.urlopen(self.link).read()
        response = response.decode(self.feed.article_charset)
        tree = etree.HTML(response)
        div = tree.xpath(self.feed.xpath_expression)
        full_text = ""
        for i in div:
            full_text += etree.tostring(i)
            full_text += "\n"
        #@TODO: strip out comments 
        full_text = re.sub(PATTERN_CDATA, '', full_text)
        #full_text = re.sub(PATTERN_COMMENT, '', full_text)
        full_text = full_text.replace('src="/', 'src="'+uri_base)
        full_text = full_text.replace('href="/', 'href="'+uri_base)
        self.text = full_text


@receiver(models.signals.pre_save, sender=Article)
def _handle_new_articles(instance, **kwargs):
    """
    Sets the information for the following fields before adding
    the article to the database:
    
        - text
    """
    instance._refresh_text()
