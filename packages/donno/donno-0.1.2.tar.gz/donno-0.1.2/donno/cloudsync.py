import os, time, glob, shutil, sys
import dropbox

import notes

from settings import note_base, passport, repo, lst_file

local_cache = note_base + 'local_cache/'
client = dropbox.client.DropboxClient(passport)

def _write_lst(delta):
    with open(lst_file, 'w') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S')+'\n')
        f.write(delta)

def syncfiles():
    lst_exist = os.path.exists(lst_file)
    mroot = client.metadata('/')
    remote = len(mroot['contents'])
    local = len([f for f in os.listdir(repo) if f.endswith('.mkd')])
    if local>0 and (not lst_exist) and remote==0:
        _upload(glob.glob(repo+'*.mkd'))
        result = client.delta()
        _write_lst(result)
        return

    if local>0 and (not lst_exist) and remote>0:
        print 'The LST file lost, build it manully.'
        return

    if local>0 and lst_exist and remote==0:
        print 'Error, maybe you can delete LST file and upload all notes to remote server.'
        return

    if local>0 and lst_exist and remote>0:
        _sync_with_server()
        return

    if local==0 and (not lst_exist) and remote==0:
        print 'There is nothing to sync with server. Try creating some notes and run this again.'
        return

    if local==0 and (not lst_exist) and remote>0:
        _download(mroot['contents'], repo)
        result = client.delta()
        _write_lst(result)
        return

    if local==0 and lst_exist and remote==0:
        print 'There is nothing to sync with server. Try creating some notes and run this again.'
        os.remove(lst_file)
        return

    if local==0 and lst_exist and remote>0:
        print 'Delete you LST file manually and run this again.'
        return

def _upload(notefiles):
    counter = 0
    for note in notefiles:
        with open(note, 'r') as f:
            response = client.put_file(os.path.basename(note), f, overwrite=True)
        counter = counter + 1
        print str(counter), "uploaded:", response['path']

def _download(notefiles, dest_local_path):
    counter = 0
    for notefile in notefiles:
        #filename = os.path.basename(notefile['path'])
        filename = os.path.basename(notefile)
        local_file_name = dest_local_path + filename
        with open(local_file_name, 'w') as lf:
            with client.get_file(notefile) as rf:
                lf.write(rf.read())
        counter = counter + 1
        print str(counter), 'download:', local_file_name

def _get_remote_changes(last_sync_time, last_cursor):
    remote_changes = []
    while True:
        if len(last_cursor)==0:
            print 'last sync curor is none, changes on server could be overwritten by that on local.'
            result = client.delta()
            return notes.Notes().create_report(''), result['cursor']
        else:
            result = client.delta(last_cursor)
        for remote_change in result['entries']:
            last_modified = remote_change[1]['client_mtime']
            lmt = time.strptime(last_modified, '%a, %d %b %Y %H:%M:%S +0000')
            lst = time.strptime(last_sync_time, '%Y-%m-%d %H:%M:%S')
            if lmt > lst:
                remote_changes.append(remote_change[0])
        if not result['has_more']:
            break
    if len(remote_changes)==0:
        return notes.Notes().create_report(''),\
                    result['cursor']
    os.system('rm -rf ' + local_cache)
    os.makedirs(local_cache)
    _download(remote_changes, local_cache)
    remote_files = glob.glob(local_cache + '*')
    return notes.Notes().create_report('\n'.join(remote_files)),\
                    result['cursor']

def _conflicted(local_set, remote_set):
    return []

def _sync_with_server():
    with open(lst_file) as f:
        last_sync_time = f.readline().strip()
        last_sync_cursor = f.readline().strip()
    local_changes = os.popen('find ' + repo + ' -newermt "' \
            + last_sync_time + '" -name "*.mkd"').read().split()

    remote_changes, sync_cursor = _get_remote_changes(last_sync_time, last_sync_cursor)
    conflicts = _conflicted(local_changes, remote_changes)
    if len(conflicts) > 0:
        print 'Find conflicts:', conflicts
        return

    print 'Remote Changes:\n' + remote_changes
    print 'Local Changes:\n' + notes.Notes().create_report('\n'.join(local_changes))

    dosync = raw_input('Sync above notes?[y/n] ')
    if dosync!='y':
        print 'Cancel notes synchronization.'
        return
    if not remote_changes.endswith('Nothing'):
        ret = os.system('cp ' + local_cache + '*.mkd ' + repo)
        if ret!=0:
            print 'ret of cp mkd files in local_cache to repo is:', str(ret)
            sys.exit('There are errors in copy downloaded notes to note repo')
        os.system('rm -rf ' + local_cache)
    _upload(local_changes)
    _write_lst(sync_cursor)
