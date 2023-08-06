import os, time, glob, shutil, sys, datetime
from dropbox.client import DropboxClient
from dropbox.datastore import (DatastoreManager, Date)
from dropbox.rest import ErrorResponse

import notes

from settings import (note_base, get_passport, repo, lst_file,
                      trash_path)

client = DropboxClient(get_passport())
remote_repo = '/repo/'
TABLE_ID = 'donno'

def _write_lst(delta_cursor):
    '''delta_cursor: str'''
    with open(lst_file, 'w') as f:
        f.write(time.strftime('%Y-%m-%d %H:%M:%S')+'\n')
        f.write(delta_cursor)

def syncfiles(only_upload, only_download):
    lst_exist = os.path.exists(lst_file)
    mroot = client.metadata(remote_repo)
    remote = len(mroot['contents'])
    if not os.path.exists(repo):
        os.makedirs(repo)
    local = len([f for f in os.listdir(repo) if f.endswith('.mkd')])
    if local>0 and (not lst_exist) and remote==0:
        _upload(glob.glob(repo+'*.mkd'))
        result = client.delta()
        _write_lst(result['cursor'])
        return

    if local>0 and (not lst_exist) and remote>0:
        print 'The LST file lost, build it manully.'
        return

    if local>0 and lst_exist and remote==0:
        print 'Error, maybe you can delete LST file and upload all notes to remote server.'
        return

    if local>0 and lst_exist and remote>0:
        if only_upload and only_download:
            sys.exit('You cannot use both these two options')

        if not (only_upload or only_download):
            _sync_with_server()
            return

        if only_upload and (not only_download):
            _upload_new_notes()
            return

        if only_download and (not only_upload):
            _download_new_notes()

    if local==0 and (not lst_exist) and remote==0:
        print 'There is nothing to sync with server. Try creating some notes and run this again.'
        return

    if local==0 and (not lst_exist) and remote>0:
        notepaths = [note['path'] for note in mroot['contents']]
        _download(notepaths, repo)
        result = client.delta()
        _write_lst(result['cursor'])
        return

    if local==0 and lst_exist and remote==0:
        print 'There is nothing to sync with server. Try creating some notes and run this again.'
        os.remove(lst_file)
        return

    if local==0 and lst_exist and remote>0:
        print 'Delete you LST file manually and run this again.'
        return

def _upload(notefiles):
    '''notefiles: [str], full path of uploaded files'''
    counter = 0
    mgr = DatastoreManager(client)
    ds = mgr.open_default_datastore()
    table = ds.get_table(TABLE_ID)
    for note in notefiles:
        with open(note, 'r') as f:
            response = client.put_file(remote_repo + os.path.basename(note),
                                f, overwrite=True)
        updated = os.path.getmtime(note)
        lmt = datetime.datetime.fromtimestamp(updated)
        fname = os.path.basename(note)
        recs = table.query(filename=fname)
        if len(recs) > 0:
            rec = recs.pop()
            rec.set('last_modified', lmt.strftime('%y-%m-%d %H:%M:%S'))
        else: # new note
            table.insert(filename=fname, 
                    last_modified=lmt.strftime('%y-%m-%d %H:%M:%S'))
        counter = counter + 1
        print str(counter), "uploaded:", response['path']
    ds.commit()

def _download(notefiles, dest_local_path):
    '''
    notefiles: [str], full path of downloaded file;
    dest_local_path: str
    '''
    counter = 0
    for notefile in notefiles:
        filename = os.path.basename(notefile)
        local_file_name = dest_local_path + filename
        with open(local_file_name, 'w') as lf:
            print 'Getting', notefile, '...'
            with client.get_file(notefile) as rf:
                lf.write(rf.read())
        mgr = DatastoreManager(client)
        ds = mgr.open_default_datastore()
        table = ds.get_table(TABLE_ID)
        recs = table.query(filename=filename)
        for rec in recs:
            last_modified = rec.get('last_modified')
        t = time.strptime(last_modified, '%y-%m-%d %H:%M:%S')
        lmt = time.mktime(t)
        os.utime(local_file_name, (lmt, lmt))
        counter = counter + 1
        print str(counter), 'download:', local_file_name

def _conflicted(local_set, remote_set):
    conflicts = {}
    conflicts['add'] = set(local_set['add']) & set(remote_set['add'])
    conflicts['del'] = set(local_set['del']) & set(remote_set['del'])
    return conflicts

def _download_new_notes():
    pass

def _upload_new_notes():
    with open(lst_file) as f:
        last_sync_time = f.readline().strip()
    local_changes = os.popen('find ' + repo + ' -newermt "' \
            + last_sync_time + '" -name "*.mkd"').read().split()
    print 'Local Changes:\n' + notes.Notes().create_report('\n'.join(local_changes))
    dosync = raw_input('Sync above notes?[y/n] ')
    if dosync!='y':
        print 'Cancel notes synchronization.'
        return
    _upload(local_changes)
    _write_lst(client.delta()['cursor'])

def _local_to_remote(local_changes):
    _upload(local_changes['add'])
    for note in local_changes['del']:
        fname = os.path.basename(note)
        try:
            client.file_delete(remote_repo + fname)
            print 'Note', fname, 'deleted on server'
        except ErrorResponse:
            print fname + ' not exists on server'
    # the record in datastore need to be deleted too

def _remote_to_local(remote_changes):
    local_cache = note_base + 'local-cache/'
    os.system('rm -rf ' + local_cache)
    os.makedirs(local_cache)
    _download(remote_changes['add'], local_cache)
    if len(glob.glob(local_cache + '*.mkd')) > 0:
        os.system('cp ' + local_cache + '*.mkd ' + repo)
    for note in remote_changes['del']:
        fname = os.path.basename(note)
        if os.path.exists(repo + fname):
            shutil.move(repo + fname, trash_path + fname)
            print 'Move note', fname, 'to trash'

def _sync_with_server():
    with open(lst_file) as f:
        last_sync_time = f.readline().strip()
        last_sync_cursor = f.readline().strip()

    local_changes = {}
    local_changes['add'] = os.popen('find ' + repo + ' -newermt "' \
            + last_sync_time + '" -name "*.mkd"').read().split()
    local_changes['del'] = os.popen('find ' + trash_path + ' -newermt "' \
            + last_sync_time + '" -name "*.mkd"').read().split()
    print 'local_changes--------', local_changes

    remote_changes = {'add':[], 'del':[]}
    remote_delta = client.delta(last_sync_cursor)
    mgr = DatastoreManager(client)
    ds = mgr.open_default_datastore()
    table = ds.get_table(TABLE_ID)
    change_entries = remote_delta['entries']
    print 'remote_change_entries-------------', change_entries
    while True:
        for remote_change in change_entries:
            print 'remote_change-------------', remote_change
            fullname = remote_change[0]
            fname = os.path.basename(fullname)
            if remote_change[1] == None:
                remote_changes['del'].append(fname)
            else:
                recs = table.query(filename=fname)
                for rec in recs:
                    last_modified = rec.get('last_modified')
                    lmt = time.strptime(last_modified, '%y-%m-%d %H:%M:%S')
                    lst = time.strptime(last_sync_time, '%Y-%m-%d %H:%M:%S')
                    if lmt > lst:
                        remote_changes['add'].append(fullname)
            print 'remote_changes-------------', remote_changes
        if not remote_delta['has_more']:
            break

    conflicts = _conflicted(local_changes, remote_changes)
    if len(conflicts['add']) > 0 or len(conflicts['del']) > 0:
        print 'Find conflicts:', conflicts
        return

    _local_to_remote(local_changes)
    _remote_to_local(remote_changes)
    _write_lst(remote_delta['cursor'])
