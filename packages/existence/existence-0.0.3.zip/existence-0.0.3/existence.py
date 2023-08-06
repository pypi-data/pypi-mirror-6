import argparse
import grequests
import lxml.html
import os


def directory_get_urls(dir):
    urls = []

    for root, subFolders, files in os.walk(dir):
        for f in files:
            with open(os.path.join(root, f), 'r+') as fin:
                urls.append(parse_html_urls(f, fin.read()))

    return urls


def bad_url_exception_handler(request, exception):
    broken_link_exception(request.kwargs["file_name"], request.kwargs["line_number"], request.url)


def broken_link_exception(file_name, line_number, href):
    raise Exception("Broken link found in file %s on line %s linking to %s" % (file_name, line_number, href))


def parse_html_urls(file_name, html_data):
    '''
    Should return the line # where the
    '''
    urls = []
    html = lxml.html.fromstring(html_data)
    anchor_tags = html.cssselect('a')

    for a in anchor_tags:
        if not 'href' in a.attrib or a.attrib['href'] == '':
            broken_link_exception(file_name, a.sourceline, a)

        url = a.attrib['href']

        if url[0] != '#':
            urls.append((url, file_name, a.sourceline))

    return urls

def check_urls(urls):
    '''
    expected format of urls is tuple (url, file name, source line) i.e. ("google.com", "index.html", 32)
    '''
    requests = (grequests.get(u[0], file_name=u[1], line_number=u[2]) for u in urls)
    grequests.map(requests, exception_handler=bad_url_exception_handler)


def check_directory(dir):
    urls = directory_get_urls(dir)
    check_urls(urls)
