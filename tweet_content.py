import re
import urllib2
from newspaper import Article

re_urls = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
status_url = re.compile('http[s]?://twitter\.com/.*/status/(\d*)')
MAX_DEPTH = 5

def get_status(api, ids):
    return api.statuses_lookup(ids)

def get_urls(text):
    urls = re.findall(re_urls, text)
    for url in urls:
        text = text.replace(url, '')
    return (text, urls)


def get_content(api, text):
    try:
        return follow_links(api, text, 0, set())
    except:
        return [ ('TWEET', get_urls(text)[0], 0) ]

def follow_links(api, text, depth, followed):
    # Make sure we're not on a wild goose chase
    texts = []
    if depth >= MAX_DEPTH:
        print 'MAX DEPTH REACHED'
        return texts

    (text, urls) = get_urls(text)
    texts.append(('TWEET', text, 0))
    if not urls:
        return texts
    else:
        urls_unwrapped = []

        # Unwrap urls and build set of explored urls
        for url in urls:
            # Unwrap t.co urls
            if 't.co' in urls[0]:
                url = urllib2.urlopen(url).url

            # Stop if you've already been here
            if url in followed:
                continue
            followed.update([url])
            urls_unwrapped.append(url)

        # Get content
        for url in urls_unwrapped:
            # Check if it's a twitter status
            if re.match(status_url, url):
                status_id = long(re.match(status_url, url).groups()[0])

                # print 'Found link to status %s'%status_id
                retrieved_status = get_status(api, [status_id])[0]
                link_text = retrieved_status.text
                sub_texts = follow_links(link_text, depth + 1, followed.copy())
                if sub_texts:
                    texts += sub_texts
            # Otherwise, treat it as a newspaper article
            else:
                a = Article(url)
                a.download()
                a.parse()
                link_text = a.title
                texts.append(('LINK', link_text, url))
                # print 'found link: %s'%link_text
        return [t for t in texts if t[1]]