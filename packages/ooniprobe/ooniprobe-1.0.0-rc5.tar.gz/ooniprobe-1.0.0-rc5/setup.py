#!/usr/bin/env python
#-*- coding: utf-8 -*-

from ooni import __version__
import urllib2
import os
import gzip
from os.path import join as pj
import sys
from setuptools import setup

def download_geoip_files():
    urls = [
        'http://www.maxmind.com/download/geoip/database/asnum/GeoIPASNum.dat.gz',
        'http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz',
        'http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz'
    ]
    for url in urls:
        target_gz_file = pj('data', os.path.basename(url))
        target_file = target_gz_file.replace('.gz', '')

        if os.path.isfile(target_file):
            print "%s already exists. Skipping." % target_file
            continue

        print "Downloading %s" % url
        response = urllib2.urlopen(url)

        with open(target_gz_file, 'w+') as f:
            f.write(response.read())
        
        with open(target_file, 'w+') as f:
            gf = gzip.open(target_gz_file, 'rb')
            f.write(gf.read())
            gf.close()

        os.unlink(target_gz_file)

download_geoip_files()

dependency_links = [
    'https://people.torproject.org/~ioerror/src/mirrors/ooniprobe'
]

usr_share_path = '/usr/share/ooni'
# If this is true then it means we are in a virtualenv
if hasattr(sys, 'real_prefix'):
    usr_share_path = pj(sys.prefix, 'share', 'ooni')
    with open(pj('data', 'ooniprobe.conf.sample.new'), 'w+') as w:
        with open(pj('data', 'ooniprobe.conf.sample')) as f:
            for line in f:
                if line.startswith('    data_dir: /usr/share/ooni'):
                    w.write('    data_dir: %s\n' % usr_share_path)
                else:
                    w.write(line)
    os.rename(pj('data', 'ooniprobe.conf.sample.new'),
              pj('data', 'ooniprobe.conf.sample'))

data_files = []
for root, dirs, file_names in os.walk('data/'):
    files = []
    for file_name in file_names:
        if file_name.endswith('.pyc'):
            continue
        elif file_name.endswith('.dat') and \
                file_name.startswith('Geo'):
            continue
        files.append(pj(root, file_name))
    data_files.append([pj(usr_share_path, root.replace('data/', '')), files])

data_files.append(['/usr/share/geoip/', 
    [
        'data/GeoIP.dat',
        'data/GeoIPASNum.dat',
        'data/GeoLiteCity.dat'
    ]
])

print data_files

install_requires = []
with open('requirements.txt') as f:
    for line in f:
        if line.startswith("#") or line.startswith('http'):
            continue
        install_requires.append(line)

setup(
    name="ooniprobe",
    version=__version__,
    author="Open Observatory of Network Interference",
    author_email = "ooni-dev@torproject.org",
    url="https://ooni.torproject.org/",
    package_dir={'ooni': 'ooni'},
    data_files=data_files,
    packages=['ooni', 'ooni.api', 'ooni.kit', 
        'ooni.nettests', 'ooni.nettests.manipulation', 
        'ooni.nettests.experimental', 'ooni.nettests.scanning',
        'ooni.nettests.blocking',
        'ooni.nettests.third_party',
        'ooni.templates', 'ooni.tests', 'ooni.utils'],

    scripts=["bin/ooniprobe"],
    dependency_links=dependency_links,
    install_requires=install_requires
)
