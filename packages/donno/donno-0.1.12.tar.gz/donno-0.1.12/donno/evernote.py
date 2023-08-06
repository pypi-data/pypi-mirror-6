import os, sys, time
from datetime import datetime
from datetime import timedelta
from xml.etree import ElementTree as ET
import nltk
import settings

def convert_time(src):
    normal_time = datetime.strptime(src, '%Y%m%dT%H%M%SZ') 
    local_time = normal_time + timedelta(hours=8)
    return local_time

def convert_created_time(src):
    local_cre_time = convert_time(src)
    created = local_cre_time.strftime('%Y-%m-%d %H:%M:%S')
    created_file = local_cre_time.strftime('%y%m%d%H%M%S')
    return {'filename': created_file+'.mkd', 'content': created}

def convert_modified_time(src):
    local_mod_time = convert_time(src)
    return time.mktime(local_mod_time.timetuple())

def convert_content(src):
    '''Did not treat the leading spaces problem. Fix it in vim manually'''
    intstr = src.replace('<div>', '\n')
    intstr = intstr.replace('</div>', '\n')
    intstr = nltk.clean_html(intstr)
    intstr = intstr.replace('&quot;', '"')
    intstr = intstr.replace('&apos;', "'")
    intstr = intstr.replace('&amp;', '&')
    intstr = intstr.replace('&lt;', '<')
    intstr = intstr.replace('&gt;', '>')
    return intstr


def importnotes(source_file, dest_nb):
    if not os.path.exists(source_file):
        sys.exit("Source file does not exist")
    if not settings.valid_nb(dest_nb):
        sys.exit(settings.invalid_nb)
    tree = ET.parse(source_file)
    root = tree.getroot()
    for note in root:
        for t in note.iter('title'):
            title = t.text
        tags = []
        for t in note.iter('tag'):
            tags.append(t.text)
        alltags = ';'.join(tags)
        for c in note.iter('content'):
            raw = c.text
        for c in note.iter('created'):
            created = c.text
        for u in note.iter('updated'):
            updated = u.text
        file_name = dest_nb + convert_created_time(created)['filename']
        with open(settings.repo + file_name, 'w') as f:
            f.write('Title: ' + title.encode('utf8') + '\n')
            f.write('Tags: ' + alltags.encode('utf8') + '\n')
            f.write('Notebook: ' + dest_nb + '[t/j/o/y/c]\n')
            f.write('Created: ' + convert_created_time(created)['content'] + '\n')
            f.write('\n------\n\n')
            f.write(convert_content(raw).encode('utf8'))
        last_modif = convert_modified_time(updated)
        os.utime(settings.repo + file_name, (last_modif, last_modif))
