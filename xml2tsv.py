#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import os
from os import listdir

DEFAULT_STRING_PATH = 'res/values/strings.xml'

DEFAULT_STRING_FILENAME = DEFAULT_STRING_PATH[DEFAULT_STRING_PATH.rfind('/') + 1:]
BASE_DIR = DEFAULT_STRING_PATH[:DEFAULT_STRING_PATH.rfind('/') + 1] + '../'
OUTPUT_FILENAME = DEFAULT_STRING_FILENAME + '.tsv'

print("Default String File: " + DEFAULT_STRING_PATH)
print("Resource Directory : " + BASE_DIR)
print("Languages : ")

def read_xml(path, lang):
    f = open(path)
    content = f.read()
    
    if lang == '':
        # <string name="aaa" translatable="false">bbb</string>
        content = re.sub(r'^\s*<string name="(\w+)"\s+translatable="(\w+)".*?>(.*?)</string>\s*$', r'\1\t\2\t\t\3\n', content, flags=re.MULTILINE|re.DOTALL)
        # <string name="aaa" formatted="true">bbb</string>
        content = re.sub(r'^\s*<string name="(\w+)"\s+formatted="(\w+)".*?>(.*?)</string>\s*$', r'\1\t\t\2\t\3\n', content, flags=re.MULTILINE|re.DOTALL)
        # <string name="aaa">bbb</string>
        content = re.sub(r'^\s*<string name="(\w+)".*?>(.*?)</string>\s*$', r'\1\t\t\t\2\n', content, flags=re.MULTILINE|re.DOTALL)
    else:
        content = re.sub(r'^\s*<string name="(\w+)".*?>(.*?)</string>\s*$', r'\1\t\2\n', content, flags=re.MULTILINE|re.DOTALL)
    # <!-- ccc -->
    content = re.sub(r'^\s*<!--.*?-->\s*$', '', content, flags=re.MULTILINE|re.DOTALL)
    # <add-resource type="string" name="aaa" />
    content = re.sub(r'^\s*<add-resource .*?>\s*$', '', content, flags=re.MULTILINE|re.DOTALL)
    # <?xml version="1.0" encoding="utf-8"?>
    content = re.sub(r'^\s*<\?xml.*?>\s*$', '', content, flags=re.MULTILINE)
    # <skip />
    content = re.sub(r'^\s*<skip.*?>\s*$', '', content, flags=re.MULTILINE)
    # <resources xmlns:xliff="urn:oasis:names:tc:xliff:document:1.2">
    content = re.sub(r'^\s*</?resources.*?>', '', content, flags=re.MULTILINE|re.DOTALL)

    content = re.sub(r'^\n', '', content, flags=re.MULTILINE)
    content = re.sub(r'\n^\s+', ' ', content, flags=re.MULTILINE)
    
    if lang == '':
        content = 'name\ttranslatable\tformatted\tdefault\n' + content
    else:
        content = 'name\t' + lang + '\n' + content
    
    lines = content.split('\n')
    while '' in lines:
        lines.remove('')
    table = []
    for i in range(len(lines)):
        table.append(lines[i].split('\t'))
    return table

def merge_table(table1, table2, lang):
    is_first_row = True
    table2_dict = dict(table2)
    for row in table1:
        if is_first_row:
            row.append(lang)
            is_first_row = False
        else:
            if row[0] in table2_dict:
                row.append(table2_dict[row[0]])
            else:
                row.append('#N/A')

base_table = read_xml(DEFAULT_STRING_PATH, '')
language_dirs = [f for f in listdir(BASE_DIR) if f != 'values' and f.startswith('values')]

for i in language_dirs:
    file_path = BASE_DIR + i + '/' + DEFAULT_STRING_FILENAME
    if os.path.exists(file_path):
        lang = i[i.find('-') + 1:]
        print(" " + lang)
        merge_table(base_table, read_xml(file_path, lang), lang)

result_file = open(OUTPUT_FILENAME, 'w')
result_lines = []
for i in base_table:
    result_lines.append('\t'.join(i))
result = '\n'.join(result_lines)
result_file.write(result)
result_file.close()

print("Output File : " + OUTPUT_FILENAME)
