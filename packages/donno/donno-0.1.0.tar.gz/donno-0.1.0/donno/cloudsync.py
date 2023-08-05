import os, time, glob

import settings
import dropbox

lst_file = settings.note_base + '.last-sync-time'
client = dropbox.client.DropboxClient(settings.passport)

def syncfiles():
    lst = os.path.exists(lst_file)
    mroot = client.metadata('/')
    remote = len(mroot['contents'])
    local = len([f for f in os.listdir(settings.repo) if f.endswith('.mkd')])
    if local>0 and remote==0 and (not lst):
        _upload(glob.glob(settings.repo+'*.mkd'))
        with open(lst_file, 'w') as f:
            f.write(time.strftime('%Y-%m-%d %H:%M:%S'))

def _upload(notefiles):
    counter = 0
    for note in notefiles:
        with open(note, 'r') as f:
            response = client.put_file(os.path.basename(note), f)
            counter = counter + 1
            print str(counter), "uploaded:", response['path']

