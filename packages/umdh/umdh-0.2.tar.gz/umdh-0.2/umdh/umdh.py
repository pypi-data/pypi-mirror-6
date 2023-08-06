#! /usr/bin/env python

import requests
import argparse
import json


BASEURL = 'http://www.housing.umich.edu/files/helper_files/js/xml2print.php?location={}&date=today&output=json'
dining_halls = {
        'barbour': BASEURL.format('BARBOUR%20DINING%20HALL'),
        'bursley': BASEURL.format('BURSLEY%20DINING%20HALL'),
        'east-quad': BASEURL.format('BARBOUR%20DINING%20HALL'),
        'markley': BASEURL.format('MARKLEY%20DINING%20HALL'),
        'south-quad': BASEURL.format('SOUTH%20QUAD%20DINING%20HALL'),
        'west-quad': BASEURL.format('WEST%20QUAD%20DINING%20HALL'),
        'marketplace': BASEURL.format('MARKETPLACE'),
        'north-quad': BASEURL.format('North%20Quad%20Dining%20Hall'),
        'twigs-at-oxford': BASEURL.format('Twigs%20at%20Oxford'),
}


# Todo: Add support for returning the meal that has the food
# Also: Removing quad for-loop would be fantastic
def search_menu_for(menu, food):
    if not isinstance(menu, dict):
        # something isn't right
        # maybe throw here?
        #print 'SOMETHING WRONG'
        return False

    results = []

    for meal in menu['menu']['meal']:
        if isinstance(meal['course'], dict):  # some notice
            #print meal['course']['name'], meal['course']['menuitem']['name']
            continue

        for course in meal['course']:
            if isinstance(course, list):
                continue

            if isinstance(course, str):
                continue

            if isinstance(course['menuitem'], dict):
                menuitem = course['menuitem']
                if food.lower() in menuitem['name'].strip().lower():
                    results.append(meal['name'].lower())
                continue

            for menuitem in course['menuitem']:
                if food.lower() in menuitem['name'].strip().lower():
                    results.append(meal['name'].lower())

    return results

def get_menu(url):
    r = requests.get(url)
    return json.loads(r.text)


def search_all_menus(food):
    results = {}
    for key, url in dining_halls.iteritems():
        r = search_menu_for(get_menu(url), food)
        if r:
            results[key] = r
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Checks for your favorite food in the dining hall')
    parser.add_argument(
        'food',
        help='Food to check for. Try "Chicken Broccoli Bake"'
        'or "Chocolate Chip Cookies"')
    args = parser.parse_args()

    search_results = search_all_menus(args.food)

    if not search_results:
        print 'Sorry, no {} today! :('.format(args.food)
        exit()

    print args.food, 'is at:'
    for i in search_results.items():
        print i
