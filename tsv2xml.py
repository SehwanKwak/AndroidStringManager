#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os
import sys
import shutil

try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except NameError:
    pass

from lxml import etree

try:
    from html import escape  # python3
except ImportError:
    from cgi import escape  # python2

try:
    from html.parser import HTMLParser  # python3
except ImportError:
    from HTMLParser import HTMLParser  # python2

from urllib2 import urlopen

unescape = HTMLParser().unescape

# constants
DEFAULT_STRING_PATH = 'res/values/strings.xml'
DEFAULT_TSV_PATH = 'strings.xml.tsv'
#DEFAULT_TSV_PATH = 'https://spreadsheets.google.com/feeds/download/spreadsheets/Export?key=1kDosVFhHhuT1HrG0-3f6M6vMazVHpTYn-S_Xy4yv_JU&exportFormat=tsv'

IS_SAVE_BACKUP_FILE = False

DEFAULT_STRING_FILENAME = DEFAULT_STRING_PATH[DEFAULT_STRING_PATH.rfind('/') + 1:]
BASE_DIR = DEFAULT_STRING_PATH[:DEFAULT_STRING_PATH.rfind('/') + 1] + '../'

KEY_FIELD = 0

default_keys = set()

def save_xml(xml_path, lang_index, lang):
    tree = etree.parse(xml_path)
    root = tree.getroot()

    # add nodes
    if lang != 'default':
        needed_keys = default_keys.copy()
        for child in root.iter('string'):
            name = child.attrib.get('name')
            if name in needed_keys:
                needed_keys.remove(child.attrib.get('name'))

        for i in needed_keys.copy():
            if dict_strings[i][lang_index].decode('utf-8') == '#N/A':
                needed_keys.remove(i)

        for i in needed_keys:
            new_node = etree.Element("string")
            new_node.set("name", i)
            new_node.tail = '\n'
            root.append(new_node)

    # modify or remove nodes
    for child in root:
        if child.tag != 'string':
            continue
        name = child.attrib.get('name')
        if name is None or name not in dict_strings:
            continue

        if lang == 'default':
            default_keys.add(name)

        remove_nodes = []
        for child_sub in child.iter():
            if child_sub.tag != 'string':
                remove_nodes.append(child_sub)
        for i in remove_nodes:
            child.remove(i)

        if name in dict_strings:
            new_text = dict_strings[name][lang_index].decode('utf-8')
            if new_text == '#N/A':
                root.remove(child)
            else:
                child.text = new_text

    new_content = etree.tostring(tree, xml_declaration=True, encoding="utf-8", method='xml')

    if IS_SAVE_BACKUP_FILE:
        shutil.move(xml_path, xml_path + '.bak')

    new_file = open(xml_path, 'w')
    new_content = unescape(new_content)
    new_content = new_content.replace("<?xml version='1.0' encoding='UTF-8'?>",
                                      '<?xml version="1.0" encoding="utf-8"?>')
    new_content = new_content.replace("<?xml version='1.0' encoding='utf-8'?>",
                                      '<?xml version="1.0" encoding="utf-8"?>')
    new_content = new_content.replace('--><resources xmlns:',
                                      '-->\n\n<resources xmlns:')
    new_content = new_content.replace('/>', ' />')
    new_file.write(new_content)
    new_file.close()

print("Default String File: " + DEFAULT_STRING_PATH)
print("Resource Directory : " + BASE_DIR)

# Loading Language Table
dict_strings = {}

if DEFAULT_TSV_PATH.startswith('http'):
    csv_stream = urlopen(DEFAULT_TSV_PATH)
else:
    csv_stream = open(DEFAULT_TSV_PATH)
csv_data = csv.reader(csv_stream, delimiter='\t', quoting=csv.QUOTE_NONE)
row_num = 0

load_languages = []
for row in csv_data:
    if row_num == 0:
        for col in row:
            if row[KEY_FIELD] not in dict_strings:
                dict_strings[row[KEY_FIELD]] = []
            else:
                dict_strings[row[KEY_FIELD]].append(col)
                load_languages.append(col)

        row_num += 1
        continue
    else:
        for col in row:
            if row[KEY_FIELD] not in dict_strings:
                dict_strings[row[KEY_FIELD]] = []
            else:
                dict_strings[row[KEY_FIELD]].append(col)
        row_num += 1

print("Load Languages : ")
print(load_languages)

# Modify language strings
language_dirs = [f for f in os.listdir(BASE_DIR) if f.startswith('values')]
print('Save Languages :')
for i in language_dirs:
    file_path = BASE_DIR + i + '/' + DEFAULT_STRING_FILENAME

    if os.path.exists(file_path):
        lang = i[i.find('-') + 1:]
        if lang == 'values':
            lang = 'default'
        if lang in load_languages:
            sys.stdout.write(" " + "'" + lang + "', ")
            save_xml(file_path, load_languages.index(lang), lang)
print

