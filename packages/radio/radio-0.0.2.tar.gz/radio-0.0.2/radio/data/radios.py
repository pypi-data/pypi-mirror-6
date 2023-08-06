#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import json


here = os.path.dirname(__file__)

radio_list_file = os.path.join(here, 'radios.json') 
f = open(radio_list_file)
rl = json.load(f)
f.close()

def show():
    radio_list = []
    for radio_id in rl:
        if len(radio_id) >= 8:
            tab = '\t'
        else:
            tab = '\t\t'
        radio_list.append('%s%s%s' % (radio_id, tab, rl[radio_id]['name']))
        radio_list.sort()
    for r in radio_list: print(r)

def save():
    f = open(radio_list_file, 'w')
    json.dump(rl, f, indent=4)
    f.close()

def add(radio_id, radio_name, radio_url):
    rl[radio_id] = {'name': radio_name, 'url': radio_url}
    save()

def delete(radio_id):
    del rl[radio_id]
    save()
