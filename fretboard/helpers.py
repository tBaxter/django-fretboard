from django.template.defaultfilters import urlizetrunc
from django.utils.html import strip_tags

from re import findall
from html_filter import html_filter
htmlfilter = html_filter()

import markdown


bad_word_replacements = {
	'fuck'   : 	'smurf',
	'FUCK'   :	'SMURF',
	'Fuck'   : 	'Smurf',
	'fucked' : 	'smurfed',
	'fucker' : 	'smurfer',
	'Fucker' : 	'Smurfer',
	'fucking': 	'smurfing',
	'Fucking': 	'Smurfing',
}

formatting_replacements = {
	# smilies
	':-D'   :	'<img src="/media/img/icons/smilies/laugh-18.png" class="smiley" alt=":D">',
	':)'    :	'<img src="/media/img/icons/smilies/grin-18.png" class="smiley" alt=":)">',
	':|'    :	'<img src="/media/img/icons/smilies/whatthe-18.png" class="smiley" alt=":|">',
	':('    :	'<img src="/media/img/icons/smilies/unhappy-18.png" class="smiley" alt=":(">',
	'8-o'   :	'<img src="/media/img/icons/smilies/googly-18.png" class="smiley" alt="8-o">',
	';-)'   : 	'<img src="/media/img/icons/smilies/wink-18.png" class="smiley" alt=";-)" >',
	':-P'   :	'<img src="/media/img/icons/smilies/crazy-18.png" class="smiley" alt=":P">',
	':mad:' :	'<img src="/media/img/icons/smilies/evil-18.png" class="smiley" alt="!#$@%" >',
	'8-)'   :	'<img src="/media/img/icons/smilies/cool-18.png" class="smiley" alt="8-)">',

	# bbcode
	'[b]'      : '<strong>',
	'[/b]'     : '</strong>',
	'[i]'      : '<em>',
	'[/i]'     : '</em>',
	'[quote]'  : '<blockquote>',
	'[/quote]' : '</blockquote>',
	'[url]'    : '',
	'[/url]'   : '',
	'[img]'    : '',
	'[/img]'   : '',
}



def clean_text(value, topic=False):
	""" 
	Clean initial post.
	Strips unacceptable HTML and replaces "profane" words with more suitable ones.
	If topic, strips all tags from topic title.
	Otherwise, uses htmlfilter to strip all but whitelisted html
	Replaces earlier htmlFilter/happy_post functionality, and
	splits functionality for raw post and formatted version.
	""" 	
	for key, val in bad_word_replacements.items():
		value = value.replace(key, val)
	#if topic:
	#	cleaned = strip_tags(value)
	#else:
	cleaned = htmlfilter.check_tags(value)
	return cleaned




def format_post(value):
	"""
	Takes cleaned text from above and creates formatted, web-friendly version.
	Converts bbcode, markdown, smilies, etc. and converts raw links to clickable (and truncated, if necessary)
	TO-DO: convert linebreaks
	"""
	# convert raw urls
	value = urlizetrunc(value, 30)
	# convert attribute-carrying BBcode URL tags
	tags = findall( r'(?xs)\[url=(.*?)\](.*?)\[/url]''', value)
	for i in tags:
		value = value.replace('[url=%s]%s[/url]' % (i[0], i[1]), '<a href="%s">%s</a>' % (i[0], i[1]))
	# convert  attribute-carrying BBcode IMG tags
	tags = findall( r'(?xs)\[img\](.*?)\[/img]''', value)
	tags += findall( r'(?xs)\[IMG\](.*?)\[/IMG]''', value)
	for i in tags:
		if not len(i) < 3 and i[0:4] == 'http':
			value = value.replace('[img]%s[/img]' % i, '<img src="%s" alt="">' % i)
			value = value.replace('[IMG]%s[/IMG]' % i, '<img src="%s" alt="">' % i)
	# handle other replacements
	for key, val in formatting_replacements.items():
		value = value.replace(key, val)
	# and finally, apply markdown
	value = markdown.markdown(value)
	return value