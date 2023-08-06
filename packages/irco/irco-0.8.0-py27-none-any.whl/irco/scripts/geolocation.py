import argparse
import collections
import re

import pycountry

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from irco import models, utils
from irco.logging import get_logger


def prep_name(name):
    name = re.sub(r'[.\'-]+', '', name.lower())
    name = re.sub(r'[^a-zA-Z0-9]+', ' ', name.lower())
    return re.split(r'\s+', name)


def main():
    log = get_logger()

    argparser = argparse.ArgumentParser('irco-geolocate')
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('database')
    argparser.add_argument('institution', nargs='*', type=int)

    args = argparser.parse_args()

    log.info('arguments_parsed', args=args)

    engine = create_engine(args.database, echo=args.verbose)
    Session = sessionmaker(bind=engine)
    session = Session()

    words = collections.Counter()
    country_words = set()
    words_to_country = {}

    for country in pycountry.countries.objects:
        ws = set(country.name.lower().split())
        for w in ws:
            if len(w) > 3:
                words_to_country.setdefault(w, []).append(country)
        country_words |= ws

    for institution, in session.query(models.Institution.name):
        words.update(w for w in prep_name(institution) if len(w) > 3)

    for w in country_words:
        try:
            del words[w]
        except KeyError:
            pass

    common = set()
    for w, freq in words.most_common(20):
        print '{:5}: {}'.format(freq, w)
        common.add(w)

    print

    import nltk
    import pprint
    import requests
    for institution_id in args.institution:
        institution = session.query(models.Institution).get(institution_id)
        print institution.name
        print

        name = set(prep_name(institution.name))
        name -= common
        countries = collections.Counter()
        for word in name:
            if word in words_to_country:
                for c in words_to_country[word]:
                    countries[c] += 1. / len(c.name.split())
                #country_candidates.extend(words_to_country[word])
        for w, freq in countries.most_common(10):
            print '{:5}: {}'.format(freq, w.name)

        print

        payload = {
            'query': institution.name,
            'sensor': 'false',
            'key': 'AIzaSyCLG_ILPIr6mauKBDk5nNiLhCJ9VHb2t4E',
        }
        r1 = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json', params=payload)

        j = r1.json()

        if j['status'] == 'ZERO_RESULTS':
            print 'Not found'
            continue

        print j

        payload = {
            'reference': r1.json()['results'][0]['reference'],
            'sensor': 'false',
            'key': 'AIzaSyCLG_ILPIr6mauKBDk5nNiLhCJ9VHb2t4E',
        }
        r2 = requests.get('https://maps.googleapis.com/maps/api/place/details/json', params=payload)

        res = r2.json()['result']
        print res['name']
        pprint.pprint(res['address_components'])


        #tokens = nltk.word_tokenize(institution.name)
        #print tokens
        #tagged = nltk.pos_tag(tokens)
        #print tagged
        #entities = nltk.chunk.ne_chunk(tagged)
        #print entities
