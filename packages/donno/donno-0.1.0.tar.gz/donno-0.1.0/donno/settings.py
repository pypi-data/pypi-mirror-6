import os

note_base = os.path.expanduser('~/.donno/')
repo = note_base + 'repo/'

notebooks = {'t': 'Tech', 'j': 'Jobs', 'o': 'Other', 'y': 'YiYang', 'c': 'Cached'}

def valid_nb(nb_name):
    return nb_name in notebooks.keys()

invalid_nb = "Invalid notebook name[t/j/o/y/c]"

if os.path.exists(note_base+'.my-key'):
    with open(note_base+'.my-key', 'r') as f:
        passport = f.read().strip()
