import os

note_base = os.path.expanduser('~/.donno/')
repo = note_base + 'repo/'
lst_file = note_base + '.last-sync-time'
trash_path = note_base + 'trash/'

notebooks = {'t': 'Tech', 'j': 'Jobs', 'o': 'Other', 'y': 'YiYang', 'c': 'Cached'}

def valid_nb(nb_name):
    return nb_name in notebooks.keys()

invalid_nb = "Invalid notebook name[t/j/o/y/c]"

def get_passport():
    if os.path.exists(note_base+'.my-key'):
        with open(note_base+'.my-key', 'r') as f:
            passport = f.read().strip()
    else:
        if not os.path.exists(note_base):
            os.makedirs(note_base)
        passport = raw_input("Now passport file found. Please input it: ")
        while len(passport)!=64:
            passport = raw_input("Now passport file found. Please input it: ")
        with open(note_base+'.my-key', 'w') as f:
            f.write(passport)
    return passport
