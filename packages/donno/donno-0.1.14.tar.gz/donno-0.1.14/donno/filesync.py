import tarfile, time, os, glob, shutil, sys
from settings import note_base, repo, trash_path, run

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

    all_archives = sorted(glob.glob(os.path.join(note_base, '*.bz2')))
    for old_archive in all_archives[:(-1 * MAX_BACKUPS)]:
        print('Delete old archive file %s.' %old_archive)
        os.remove(old_archive)

    all_archives = sorted(glob.glob('*.bz2'))
    for old_archive in all_archives[:(-1 * MAX_BACKUPS)]:
        print('Delete old archive file %s.' %old_archive)
        os.remove(old_archive)

def restore():
    archives = sorted(glob.glob('*.bz2'))
    if len(archives) == 0:
        msg = 'No archive file found in current directory.'
        sys.exit(msg)

    arcfile = archives[-1]
    ret = run('find %s -cnewer %s | grep mkd' %(note_base, arcfile), False)
    if ret==0:
        rep = raw_input('There are files newer than archive, '\
                'continue restore? [y/n] ')
        if rep != 'y':
            sys.exit('Restore notes canceled by user.')

    confirm = raw_input('Restore notes from %s? [y/n] ' % arcfile)
    if confirm != 'y':
        sys.exit('Restore notes canceled by user.')

    print('Move archive file %s to repository.' %arcfile)
    run('mv %s %s' %(arcfile, note_base))
    repo_archs = sorted(glob.glob(os.path.join(note_base, '*.bz2')))
    restored = repo_archs[-1]

    tmp_extract = os.path.join(note_base, 'tmp')
    run('rm -rf %s; mkdir %s' % (tmp_extract, tmp_extract))
    with tarfile.open(restored, 'r:bz2') as tar:
        tar.extractall(tmp_extract)
    for root, dirs, files in os.walk(tmp_extract):
        for adir in dirs:
            if adir=='repo' or adir=='trash':
                run('rm -rf %s' % repo)
                run('rm -rf %s' % trash_path)
                run('mv %s %s' %(os.path.join(root, adir), note_base))
    run('rm -rf %s' % tmp_extract)

    for old_archive in repo_archs[:(-1 * MAX_BACKUPS)]:
        print('Delete old archive file %s.' %old_archive)
        os.remove(old_archive)
