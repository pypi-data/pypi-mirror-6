#!/usr/bin/env python

from itertools import islice
from urllib import urlretrieve
import os.path
import re

from flickrapi import FlickrAPI


# Creative commons licence ids
LICENCES = (4, 5, 6, 7)


def slugify(value):
    """
    From django: converts to lowercase, removes non-alpha characters, and
    converts spaces to hyphens.
    """
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


class Downloader(FlickrAPI):
    def fetch(self, terms, size='c', number=10, output=None):
        if not terms:
            raise ValueError('Specify some search terms')
        if not output:
            output = slugify('-'.join(terms))
        url_field = 'url_%s' % size.lower()

        # Arguments for the flickr api
        options = {
            'text': ' '.join(terms),
            'sort': 'relevance',
            'license': ','.join(map(str, LICENCES)),
            'content_type': '1',  # no screenshots
            'media': 'photos',    # no videos
            'extras': url_field,
        }
        photos = self.walk(**options)

        # Make the output dir, fail if it already exists
        os.mkdir(output)

        # Skip photos that don't have the size we want
        urls = (photo.attrib[url_field] for photo in photos
                if photo.get(url_field))

        for url in islice(urls, 0, number):
            filename = os.path.basename(url)
            urlretrieve(url, os.path.join(output, filename))
            yield url


def fetch(*args, **kwargs):
    api_key = kwargs.pop('key', None) or os.environ['FLICKR_API_KEY']
    flickr = Downloader(api_key)
    return flickr.fetch(*args, **kwargs)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Download stock photos from flickr')
    parser.add_argument('term', nargs='+', help='search terms')
    parser.add_argument('-s', '--size', choices=('sq', 't', 's', 'q', 'm', 'n',
                                                 'z', 'c', 'l', 'o'),
                        default='c', help='photo size')
    parser.add_argument('-n', '--number', type=int, default=10, help='how many photos')
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-k', '--key', help='flickr api key')
    options = vars(parser.parse_args())
    terms = options.pop('term')

    for url in fetch(terms, **options):
        print(url)
