from __future__ import print_function
import os
from bs4 import BeautifulSoup
import requests
import sys
import pkgutil
import pprint


def parse(content, no_request):
    soup = BeautifulSoup(content, 'lxml')
    data = {'global': {
               'title': '',
               'desc': '',
               'picture_url': '',
               'picture_width': '',
               'picture_height': '',
               'video_url': '',
               'video_width': '',
               'video_height': ''
           }}

    pkgpath = os.path.join(os.path.dirname(__file__), 'backends')

    for _, name, _ in pkgutil.iter_modules([pkgpath]):
        mod = __import__(".".join(['embeder.backends', name]),
                         fromlist=['parse', 'MAPPING'])
        data[name] = {}
        backend_data = mod.parse(soup, no_request)
        data[name] = backend_data

        for key, value in backend_data.items():
            if key in data['global']:
                data['global'][key] = value

        if hasattr(mod, 'MAPPING'):
            for global_key, backend_key in mod.MAPPING.items():
                if backend_key in backend_data:
                    data['global'][global_key] = backend_data[backend_key]

    return data


def get(link, no_request=False):
    response = requests.get(link)
    return parse(response.text, no_request)


if __name__ == '__main__':
    try:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(get(sys.argv[1]))
    except IndexError:
        print("USAGE: python", __file__, "<url>", file=sys.stderr)
