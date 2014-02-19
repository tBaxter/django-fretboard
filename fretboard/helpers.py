import re
import time
import urlparse

from datetime import datetime


import bleach
import markdown

from django.template.defaultfilters import urlizetrunc, linebreaks
from django.utils.encoding import force_text
from django.utils.safestring import SafeData, mark_safe
from django.utils.html import TRAILING_PUNCTUATION, WRAPPING_PUNCTUATION, \
    escape, word_split_re, simple_url_re, simple_url_2_re, smart_urlquote, simple_email_re


# These are based on defaults from bleach.
ALLOWED_TAGS = (
    'a',
    'b',
    'blockquote',
    'br',
    'em',
    'i',
    'img',
    'li',
    'ol',
    'strong',
    'ul',
    'hr',
    'p',
    'h3',
    'video',
    'span',
    'iframe'
)

ALLOWED_ATTRIBUTES = {
    'a':   ('href', 'title', 'rel'),
    'img': ('src', 'alt'),
    'iframe': ('src', 'height', 'width'),
    '*':   ('class',),
}


bad_word_replacements = (
    ('fuck',    'smurf'),
    ('FUCK',    'SMURF'),
    ('Fuck',    'Smurf'),
    ('fucked',  'smurfed'),
    ('fucker',  'smurfer'),
    ('Fucker',  'Smurfer'),
    ('fucking', 'smurfing'),
    ('Fucking', 'Smurfing'),
)

bbcode_replacements = (
    (r'\[url\](.+?)\[/url\]',       r'\[link\]\(\1\)'),
    (r'\[url=(.+?)\](.+?)\[/url\]', r'\[\2\]\(\1\)'),
    (r'\[img\](.+?)\[/img\]',       r'\1'),
    (r'\[IMG\](.+?)\[/IMG\]',       r'\1'),
    (r'\[img=(.+?)\](.+?)\[/img\]', r'\1'),
    (r'\[b\](.+?)\[/b\]',           r'**\1**'),
    (r'\[i\](.+?)\[/i\]',           r'*\1*'),
    (r'\[quote\](.+?)\[/quote\]',   r'<blockquote>\1</blockquote>'),
)

emoticon_replacements = (
    (' :) ',       'happy'),
    (':-)',        'happy'),
    (':smile:',    'happy'),
    (' :( ',       'unhappy'),
    (':-(',        'unhappy'),
    (':sad:',      'unhappy'),
    (' ;) ',       'wink2'),
    (';-)',        'wink2'),
    (':wink:',     'wink2'),
    (' :P ',       'tongue'),
    (':-P',        'tongue'),
    (':razz:',     'tongue'),
    (' x( ',       'angry'),
    ('x-(',        'angry'),
    (':angry:',    'angry'),
    (' :x ',       'angry'),
    (':-x',        'angry'),
    (':mad:',      'angry'),
    (' 8) ',       'cool'),
    ('8-)',        'cool'),
    (' B) ',       'cool'),
    ('B-)',        'cool'),
    (':cool:',     'cool'),
    (' :D ',       'grin'),
    (':-D',        'grin'),
    (':grin:',     'grin'),
    ('8-o',        'surprised'),
    (' :o ',       'surprised'),
    (':-0',        'surprised'),
    ('8-0:',       'surprised'),
    (':shock:',    'surprised'),
    (':eek:',      'surprised'),
    (':|',         'displeased'),
    (' :/ ',       'displeased'),
    (':-/',        'displeased'),
    (':thumbs:',   'thumbsup'),
    (':thumbsup:', 'thumbsup'),
    (':devil:',    'devil'),
    (':twisted:',  'devil'),
    (':beer:',     'beer'),
    (':cry:',      'cry'),
    (":'(",        'cry'),
    (":'-(",       'cry'),
    (':laugh:',    'laugh'),
    (':lol:',      'laugh'),
    ('^^',         'laugh'),
    ('^_^',        'laugh'),
)


def clean_text(value, topic=False):
    """
    Replaces "profane" words with more suitable ones.
    Uses bleach to strip all but whitelisted html.
    Converts bbcode to Markdown
    """
    # Clean bad words
    for x in bad_word_replacements:
        value = value.replace(x[0], x[1])
    # Convert BBCode to markdown
    for bbset in bbcode_replacements:
        p = re.compile(bbset[0], re.DOTALL)
        value = p.sub(bbset[1], value)
    bleached = bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    # because we want to retain markdown quotes, 
    # and we'll be running bleach again in format_post.
    bleached = bleached.replace('&gt;', '>').replace('&amp;', '&')
    return bleached


def format_post(value):
    """
    Takes cleaned text from above and creates HTML-formatted, web-friendly version.
    - converts links to images and video to actual media objects.
    - Make raw links clickable (and truncated, if necessary).
    - Converts smilies and markdown to valid HTML.
    _ Bleaches output (again) to catch any stray HTML inserted by markdown.

    TO-DO: convert linebreaks
    """
    # convert media links
    value = convert_links(value)
    value = urlizetrunc(value, 30)

    for x in emoticon_replacements:
        value = value.replace(x[0], '<span class="emoticon-%s"></span>' % x[1])

    markedup = markdown.markdown(value).replace('</p>\n<p>', '</p><p>')
    with_linebreaks = linebreaks(markedup)
    bleached = bleach.clean(with_linebreaks, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    return mark_safe(bleached)


def update_post_relations(user, topic, deleting=False):
    """
    helper function to update user post count and parent topic post_count.
    """
    if deleting:
        user.post_count = user.post_count - 1
    else:
        user.post_count += 1
    user.save(update_fields=['post_count'])

    topic.modified     = datetime.now()
    topic.modified_int = time.time()
    topic.save(update_fields=['modified', 'modified_int'])


def convert_links(text, trim_url_limit=None, nofollow=False, autoescape=False):
    """
    Finds URLs in text and attempts to handle correctly.
    Heavily based on django.utils.html.urlize
    With the additions of attempting to embed media links, particularly images.

    Works on http://, https://, www. links, and also on links ending in one of
    the original seven gTLDs (.com, .edu, .gov, .int, .mil, .net, and .org).

    Links can have trailing punctuation (periods, commas, close-parens) and
    leading punctuation (opening parens) and it'll still do the right thing.

    """

    safe_input = isinstance(text, SafeData)
    words = word_split_re.split(force_text(text))
    for i, word in enumerate(words):
        if '.' in word or ':' in word:
            # Deal with punctuation.
            lead, middle, trail = '', word, ''
            for punctuation in TRAILING_PUNCTUATION:
                if middle.endswith(punctuation):
                    middle = middle[:-len(punctuation)]
                    trail = punctuation + trail
            for opening, closing in WRAPPING_PUNCTUATION:
                if middle.startswith(opening):
                    middle = middle[len(opening):]
                    lead = lead + opening
                # Keep parentheses at the end only if they're balanced.
                if (middle.endswith(closing)
                    and middle.count(closing) == middle.count(opening) + 1):
                    middle = middle[:-len(closing)]
                    trail = closing + trail

            # Make URL we want to point to.
            url = None
            if simple_url_re.match(middle):
                url = smart_urlquote(middle)
            elif simple_url_2_re.match(middle):
                url = smart_urlquote('http://%s' % middle)
            elif not ':' in middle and simple_email_re.match(middle):
                local, domain = middle.rsplit('@', 1)
                try:
                    domain = domain.encode('idna').decode('ascii')
                except UnicodeError:
                    continue
            if url:
                u = url.lower()
                if autoescape and not safe_input:
                    lead, trail = escape(lead), escape(trail)
                    url = escape(url)

                # Photos
                if u.endswith('.jpg') or u.endswith('.gif') or u.endswith('.png'):
                    middle = '<img src="%s">' % url

                # Youtube
                #'https://www.youtube.com/watch?v=gkqXgaUuxZg'
                elif 'youtube.com/watch' in url:
                    parsed = urlparse.urlsplit(url)
                    query  = urlparse.parse_qs(parsed.query)
                    token  = query.get('v')
                    if token and len(token) > 0:
                        middle = '<iframe src="http://www.youtube.com/embed/%s" height="320" width="100%%"></iframe>' % token[0]
                    else:
                        middle = url
                elif 'youtu.be/' in url:
                    try:
                        token = url.rsplit('/', 1)[1]
                        middle = '<iframe src="http://www.youtube.com/embed/' + token + '" height="320" width="100%%"></iframe>'
                    except IndexError:
                        middle = url

                words[i] = mark_safe('%s%s%s' % (lead, middle, trail))
            else:
                if safe_input:
                    words[i] = mark_safe(word)
                elif autoescape:
                    words[i] = escape(word)
        elif safe_input:
            words[i] = mark_safe(word)
        elif autoescape:
            words[i] = escape(word)
    return ''.join(words)


def embed_video(url):
    return '<iframe width="100%" height="320" src="%s" frameborder="0" allowfullscreen></iframe>' % url
