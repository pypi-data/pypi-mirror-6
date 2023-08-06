import argparse, sys
import notes

def addnote(args):
    note = notes.Note(nb=args.notebook)
    note.create_new_note()

def listnotes(args):
    ns = notes.Notes(args.listcnt)
    print ns.listnotes()

def simple_search(args):
    ns = notes.Notes()
    print ns.simple_search(args.targets, args.incremental)

def complex_search(args):
    ns = notes.Notes()
    print ns.complex_search(args.titles, args.tags, args.contents, args.notebook)

def viewnote(args):
    note = notes.Note()
    note.view_note(args.listno)

def editnote(args):
    note = notes.Note()
    note.edit_note(args.listno)

def deletenote(args):
    note = notes.Note()
    note.delete_note(args.listno)
    
def importnotes(args):
    import evernote
    evernote.importnotes(args.evernote_file, args.notebook)

def sync_notes(args):
    import filesync
    if args.restore:
        filesync.restore()
        return
    if args.cloud:
        import cloudsync
        cloudsync.syncfiles(False, False)
        return
    filesync.backup(args.upload)

def def_parser():
    parser = argparse.ArgumentParser(prog='an',
            epilog='Use "dn <cmd> -h" for the exact help of <cmd>.',
            description='Donno is a personal CLI note-taking app.')
    subparsers = parser.add_subparsers()
    parser_addnote = subparsers.add_parser('a', help='Add note')
    parser_addnote.add_argument('notebook', nargs='?', default='j',
            help='create the note in which notebook?')
    parser_addnote.set_defaults(func=addnote)

    parser_listnote = subparsers.add_parser('l',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            help='List recent modified notes')
    parser_listnote.add_argument('listcnt', nargs='?', type=int, default=5,
            help='how many notes in output list?')
    parser_listnote.set_defaults(func=listnotes)

    parser_searchnote = subparsers.add_parser('s', help='Simple search')
    parser_searchnote.add_argument('targets', nargs='+',
            help='the search targets in all text.')
    parser_searchnote.add_argument('-i', '--incremental', action='store_true',
            help='search in the previous search result')
    parser_searchnote.set_defaults(func=simple_search)

    parser_complexsearch= subparsers.add_parser('sc', help='Complex search')
    parser_complexsearch.add_argument('-t', '--titles', nargs='*',
            help='search in the note titles')
    parser_complexsearch.add_argument('-g', '--tags', nargs='*',
            help='search in the note tags')
    parser_complexsearch.add_argument('-c', '--contents', nargs='*',
            help='search in the note content')
    parser_complexsearch.add_argument('-b', '--notebook', nargs='?', 
            help='in which notebook?')
    parser_complexsearch.set_defaults(func=complex_search)

    parser_viewnote = subparsers.add_parser('v', help='View the note')
    parser_viewnote.add_argument('listno', nargs='?', type=int, default=1,
            help='the order in the last note list by list or search command')
    parser_viewnote.set_defaults(func=viewnote)

    parser_editnote = subparsers.add_parser('e', help='Edit the note')
    parser_editnote.add_argument('listno', nargs='?', type=int, default=1,
            help='the order in the last note list by list or search command')
    parser_editnote.set_defaults(func=editnote)

    parser_deletenote = subparsers.add_parser('del', help='Delete the note')
    parser_deletenote.add_argument('listno', nargs='?', type=int, default=1,
            help='the order in the last note list by list or search command')
    parser_deletenote.set_defaults(func=deletenote)

    parser_importnotes = subparsers.add_parser('import', help='Import notes')
    parser_importnotes.add_argument('evernote_file',
            help='the .enex file exported from evernote')
    parser_importnotes.add_argument('notebook',
            help='the destination notebook')
    parser_importnotes.set_defaults(func=importnotes)

    parser_syncnote = subparsers.add_parser('y',
            help='Backup notes to archive file')
    group = parser_syncnote.add_mutually_exclusive_group()
    group.add_argument('-u', '--upload', action='store_true',
            help='Upload archive file to cloud server')
    group.add_argument('-r', '--restore', action='store_true',
            help='restore from local archive')
    group.add_argument('-c', '--cloud', action='store_true',
            help='sync with files on dropbox server')
    parser_syncnote.set_defaults(func=sync_notes)
    return parser

def main():
    parser = def_parser()
    args = parser.parse_args()
    args.func(args)
