import sys, time, shutil, os, glob, datetime, subprocess
from settings import note_base, lst_file, notebooks, valid_nb, invalid_nb, repo

cache_file = note_base + '.last-result'

class Notes:
    def __init__(self, cnt=None):
        self.listcnt = cnt

    def post_process(self, paths):
        '''Save result to cache file and create user-friendly report'''
        with open(cache_file, 'w') as f:
            f.write(paths)
        return self.create_report(paths)

    def create_report(self, paths):
        if len(paths)==0:
            return 'Nothing'
        report = [Note.title_line]
        listno = 1
        for path in paths.split(): 
            note = Note(path=path)
            report.append(str(listno) + '. ' + ' '.join(note.listAttr()))
            listno = listno + 1
        return '\n'.join(report)


    def listnotes(self):
        if not os.path.exists(repo):
            sys.exit("Note repo does not exist")
        list_res = subprocess.Popen(['ls', '-t'] + glob.glob(repo 
                + '*.mkd'), stdout=subprocess.PIPE)
        recent = subprocess.Popen(('head -'+str(self.listcnt)).split(),
                               stdin=list_res.stdout, stdout=subprocess.PIPE)
        most_recent = recent.communicate()[0]
        return self.post_process(most_recent)

    def nonincr_search(self, targets):
        first_cmd = subprocess.Popen(['grep', '-i', '-l', targets.pop(0)] + \
                 glob.glob(repo+'*.mkd'), stdout=subprocess.PIPE)
        cmd_queue = [first_cmd]
        while len(targets)>0:
            cmd = subprocess.Popen(['xargs','grep','-i','-l',targets.pop(0)],
                 stdin=cmd_queue[-1].stdout, stdout=subprocess.PIPE)
            cmd_queue.append(cmd)
        notes = cmd_queue[-1].communicate()[0]
        result = self.post_process(notes)
        return result

    def simple_search(self, targets, incremental):
        if incremental and os.path.exists(cache_file):
            first_cmd = subprocess.Popen(
                    ['xargs', 'grep', '-i', '-l', targets.pop(0)],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
            cmd_queue = [first_cmd]
            while len(targets)>0:
                cmd = subprocess.Popen(['xargs','grep','-i','-l',targets.pop(0)],
                         stdin=cmd_queue[-1].stdout, stdout=subprocess.PIPE)
                cmd_queue.append(cmd)
            with open(cache_file, 'r') as f:
                files = f.readlines()
            scope = ''.join(files)
            result = cmd_queue[-1].communicate(input=scope)[0]
            final_res = self.post_process(result)
            return final_res
        else:
            return self.nonincr_search(targets)

class Note:
    def __init__(self, nb=None, path=None):
        self.notebook = nb
        self.path = path

    def create_new_note(self):
        if not valid_nb(self.notebook):
            sys.exit(invalid_nb)
        tmp_note = note_base + 'newnote.tmp.mkd'
        created = time.strftime('%Y-%m-%d %H:%M:%S')
        created_file = time.strftime('%y%m%d%H%M%S')
        note_template = 'Title: \nTags: \nNotebook: %s [t/j/o/y/c]\n'\
                        'Created: %s\n\n------\n\n' % (self.notebook, created)
        with open(tmp_note, 'w') as f:
            f.write(note_template)
        os.system('vi ' + tmp_note)
        self.path = tmp_note
        note_attr = self.listAttr()
        if len(note_attr[1])==0:
           sys.exit('Cancel note creattion for empty title')
        if not os.path.exists(repo):
            os.makedirs(repo)
        shutil.move(tmp_note, repo + self.notebook + created_file + '.mkd')

    title_line = 'No. Updated, Title, Tags, Notebook, Created, Sync?'

    def listAttr(self):
        attr = []
        updated = os.path.getmtime(self.path)
        lmt = datetime.datetime.fromtimestamp(updated)
        attr.append(lmt.strftime('%y-%m-%d %H:%M'))
        with open(self.path, 'r') as f:
            content = f.readlines()

        title_line = content[0]
        if not title_line.startswith('Title: '):
            sys.exit('Bad note file format: 1st line should start with "Title:"')
        title = title_line[len('Title: '):-1] 
        attr.append(title)

        tags_line = content[1]
        if not tags_line.startswith('Tags: '):
            sys.exit('Bad note file format: 2nd line should start with "Tags:"')
        tags = '[' + tags_line[len('Tags: '):-1] + ']'
        attr.append(tags)

        nb_line = content[2]
        if not nb_line.startswith('Notebook: '):
            sys.exit('Bad note file format: 3rd line should start with "Notebook:"')
        nb_name = notebooks[nb_line[10]] 
        attr.append(nb_name)

        created_raw = os.path.basename(self.path)[1:11]
        created = created_raw[0:2]+'-'+created_raw[2:4]+'-'+created_raw[4:6]\
                +' '+created_raw[6:8]+':'+created_raw[8:10]

        attr.append(created)
        with open(lst_file) as f:
            last_sync_time = f.readline().strip()
        lst = time.mktime(datetime.datetime.strptime(last_sync_time,
                '%Y-%m-%d %H:%M:%S').timetuple())
        if updated>lst: attr.append('*')

        return attr

    def edit_note(self, listno):
        with open(cache_file, 'r') as f:
            content = f.readlines()
        notepath = content[listno-1].strip()
        shutil.copyfile(notepath, notepath+'.bak')
        os.system('vi ' + notepath)

    def view_note(self, listno):
        with open(cache_file, 'r') as f:
            content = f.readlines()
        notepath = content[listno-1].strip()
        shutil.copyfile(notepath, notepath+'.bak')
        os.system('vi -R ' + notepath)
