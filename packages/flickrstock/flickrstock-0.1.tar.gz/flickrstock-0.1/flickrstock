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
    def fetch(self, tags, size='c', number=10, output=None):
        if not tags:
            raise ValueError('Specify some tags to search for')
        if not output:
            output = slugify('-'.join(tags))
        url_field = 'url_%s' % size.lower()

        # Arguments for the flickr api
        options = {
            'tags': ','.join(tags),
            'tag_mode': 'all',
            'license': ','.join(map(str, LICENCES)),
            'content_type': '1',  # no screenshots
            'media': 'photos',    # no videos
            'extras': url_field,
        }
        photos = self.walk(**options)

        # Make the output dir, fail if it already exists
        os.mkdir(output)

        for photo in islice(photos, 0, number):
            url = photo.attrib[url_field]
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
    parser.add_argument('tag', nargs='+', help='tags to search for')
    parser.add_argument('-s', '--size', choices=('sq', 't', 's', 'q', 'm', 'n',
                                                 'z', 'c', 'l', 'o'),
                        default='c', help='photo size')
    parser.add_argument('-n', '--number', type=int, default=10, help='how many photos')
    parser.add_argument('-o', '--output', help='output directory')
    parser.add_argument('-k', '--key', help='flickr api key')
    options = vars(parser.parse_args())
    tags = options.pop('tag')

    for url in fetch(tags, **options):
        print(url)
