import xmlrpclib, os, sys, glob, xmlrpclib, ConfigParser, codecs, time
from settings import note_base, repo, trash_path, run
from subprocess import check_output
from markdown import markdown

CnBlogsFile = os.path.join(note_base, 'cnblogs')

def publish_notes(allnotes=True):
    if not os.path.exists(CnBlogsFile):
        sys.exit('Please create cnblogs file under the repo manually.')

    config = ConfigParser.ConfigParser()
    config.read(CnBlogsFile)
    serviceUrl = config.get('Login', 'url')
    appkey = config.get('Login', 'username')
    username = config.get('Login', 'username')
    password = config.get('Login', 'password')

    if allnotes:
        published = glob.glob(os.path.join(repo, '*.mkd'))
    else:
        cmd = 'find %s -cnewer %s -name "t*.mkd"' %(repo, CnBlogsFile)
        res = check_output(cmd, shell=True)
        if len(res) == 0:
            sys.exit('Nothing new need to update')

        published = res.strip().split('\n')
        if len(published) == 0:
            sys.exit('Nothing new need to update')

    print('There are %d new files to publish.' % len(published))

    failure_cnt = 0
    for afile in published:
        content = codecs.open(afile, encoding='utf-8').readlines()
        title_line = content[0]
        if not title_line.startswith('Title: '):
            sys.exit('Bad note file format: 1st line should start with "Title:"')
        title = title_line[len('Title: '):-1] 

        tags_line = content[1]
        if not tags_line.startswith('Tags: '):
            sys.exit('Bad note file format: 2nd line should start with "Tags:"')
        tags = tags_line[len('Tags: '):-1].replace(';', ',')

        body = markdown('\n'.join(content[7:]))
        post = {'title':title, 'description':body, 'mt_keywords':tags}

        server = xmlrpclib.ServerProxy(serviceUrl)
        try:
            postid = config.get('PostTable', afile)
            server.metaWeblog.editPost(postid, username, password, post, True)
            print('Update success: %s.' % title)
        except ConfigParser.NoOptionError:
            try:
                postid = server.metaWeblog.newPost('', username, password, post, True)
                print('Publish success: %s.' % title)
                config.set('PostTable', afile, postid)
                with open(CnBlogsFile, 'wb') as f:
                    config.write(f)
            except xmlrpclib.Fault:
                failure_cnt = failure_cnt + 1
                if failure_cnt == 20:
                    print('20 failure met. Maybe you have met the maximum number of new posts today, try it tommorrow.')
                    break
                print('Publish failed: %s' % title)
        time.sleep(0.2)
