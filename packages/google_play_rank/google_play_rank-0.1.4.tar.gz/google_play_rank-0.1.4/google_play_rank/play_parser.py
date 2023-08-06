# -*- encoding: utf-8 -*-
import requests
import bs4
import re
import argparse


def parseCategory(category, isFree, start):
    url = 'https://play.google.com/store/apps/category/%s/collection/topselling_' % (category)
    if isFree:
        url += 'free'
    else:
        url += 'paid'

    data = {
        'start': start * 60,
        'num': 60,
        'ipf': 1,
        'xhr': 1,
    }

    response = requests.post(url, data=data)
    soup = bs4.BeautifulSoup(response.content)
    card = soup.find('div', class_='card-list')
    if card:
        divs = card.find_all('div', class_='card')
        for div in divs:
            app = {}

            # get package name and link
            app['package_name'] = div.get('data-docid')
            app['link'] = 'https://play.google.com/store/apps/details?id=%s' % (app['package_name'])

            # get large and small cover image
            img = div.find('img', class_='cover-image')
            if img:
                app['cover_lage'] = img.get('data-cover-large')
                app['cover_small'] = img.get('data-cover-small')

            detail = div.find('div', class_='details')
            if detail:
                # get title
                title = detail.find('a', class_='title')
                if title:
                    app['title'] = title.get_text().strip()

                # get subtitle
                subtitle = detail.find('a', class_='subtitle')
                if subtitle:
                    app['subtitle'] = subtitle.get_text().strip()

            reason = div.find('div', class_='reason-set')
            if reason:
                # get ranking in width of css style
                rating = reason.find('div', class_='current-rating')
                if rating:
                    style = rating.get('style')
                    match = re.match('width: (.*?)%;', style)
                    if match:
                        app['rating'] = float(match.group(1))

                # get price
                price = reason.find('button', class_='price')
                if price:
                    app['price'] = price.get_text().strip()

            yield app


def get_app_rank(package_name, category, isFree=True):

    rank = 0
    counter = 1
    while True:
        if rank > 1000:
            print 'Abort! Ranking more than 1000.'
            return
        for app in parseCategory(category, isFree, counter):
            # print app['package_name']
            rank += 1
            if app['package_name'] == package_name:
                print rank
                return
        counter += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('package', help='Android package name')
    parser.add_argument('category', help='App category')

    args = parser.parse_args()

    get_app_rank(args.package, args.category.upper(), True)

if __name__ == '__main__':
    main()