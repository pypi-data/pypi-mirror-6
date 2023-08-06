import tarfile, time, os, glob, shutil, sys
from settings import note_base, repo, trash_path

MAX_BACKUPS = 3 # only save last 3 archives

def backup(upload):
    filename = time.strftime('notes%y-%m-%d-%H.%M.%S.bz2')
    fullpath = note_base + filename
    with tarfile.open(fullpath, 'w:bz2') as tar:
        tar.add(repo)
        tar.add(trash_path)

    with tarfile.open(fullpath, 'r:bz2') as tar:
        print 'Create archive', filename, 'with size:',\
            os.path.getsize(fullpath), 'file number:',\
            str(len(tar.getmembers()))

    if upload:
        from dropbox.client import DropboxClient
        from settings import get_passport
        client = DropboxClient(get_passport())
        remote_repo = '/backup/'
        with open(fullpath, 'rb') as f:
            res = client.put_file(remote_repo + filename, f)
            print 'uploaded:', res
        return

    shutil.copyfile(fullpath, os.path.join(os.getcwd(), filename))

    all_archives = glob.glob(os.path.join(note_base, '*.bz2'))
    for old_archive in all_archives[:(-1 * MAX_BACKUPS)]:
        os.remove(old_archive)

    all_archives = glob.glob('*.bz2')
    for old_archive in all_archives[:(-1 * MAX_BACKUPS)]:
        os.remove(old_archive)

def restore():
    archives = glob.glob('*.bz2')
    if len(archives) == 0:
        msg = 'No archive file found in current directory.'
        sys.exit(msg)

    arcfile = sorted(archives)[-1]
    ret = os.system('find ' + note_base + ' -cnewer ' + arcfile +\
            '|grep mkd')
    if ret==0:
        rep = raw_input('There are files newer than archive, '\
                'continue restore? [y/n] ')
        if rep != 'y':
            sys.exit('Restore notes canceled by user.')

    confirm = raw_input('Restore notes from ' + arcfile + '? [y/n] ')
    if confirm != 'y':
        sys.exit('Restore notes canceled by user.')

    tmp_extract = note_base + 'tmp'
    os.system('rm -rf ' + tmp_extract)
    os.makedirs(tmp_extract)
    with tarfile.open(arcfile, 'r:bz2') as tar:
        tar.extractall(tmp_extract)
    for root, dirs, files in os.walk(tmp_extract):
        for adir in dirs:
            if adir=='repo' or adir=='trash':
                os.system('rm -rf ' + repo)
                os.system('rm -rf ' + trash_path)
                os.system(' '.join(['mv', os.path.join(root, adir), note_base]))
    os.system('rm -rf ' + tmp_extract)
    os.system('cp ' + arcfile + ' ' + note_base)

    all_archives = glob.glob(os.path.join(note_base, '*.bz2'))
    for old_archive in all_archives[:(-1 * MAX_BACKUPS)]:
        os.remove(old_archive)
