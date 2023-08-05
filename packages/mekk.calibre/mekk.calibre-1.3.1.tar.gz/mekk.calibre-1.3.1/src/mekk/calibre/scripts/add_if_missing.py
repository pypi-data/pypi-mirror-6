# -*- coding: utf-8 -*-

"""
Scans given directory, adds to calibre all books which are not yet
present there. Duplicate checking is done solely on file content
comparison (file name may differ).  Used to double-check whether some
dir items were added to calibre, or not fully.

Example:

    calibre_add_if_missing /home/jan/OldBooks

(and later remove OldBooks if everything is OK).

Can be also used to add individual files, for example:

    calibre_add_if_missing *.pdf *.djvu subdir/*.pdf

There are also some useful options, run --help to see them.

"""
from __future__ import print_function

import shutil
import re
import os.path
from collections import defaultdict
from mekk.calibre.calibre_util import \
    find_calibre_file_names, add_to_calibre
from mekk.calibre.disk_util import \
    find_disk_files, file_size, are_files_equivalent
# TODO: migrate to argparse some day
from optparse import OptionParser

def process_options():
    usage = "Usage: %prog [options] file-or-dir-1 file-or-dir-2 ..."
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--dry-run",
                      action="store_true", default=False, dest="dry_run",
                      help="Do not add anything (and do not move files), just print what I would do.")
    parser.add_option("-c", "--cache",
                      action="store_true", default=False, dest="cache",
                      help="Use cached calibre catalog from previous run to speed up things.")
    parser.add_option("-x", "--tag",
                      action="store", type="string", dest="tag",
                      help="Tag added files with given tag(s). Can be comma-separated.")
    parser.add_option("-a", "--author",
                      action="store", type="string", dest="author",
                      help="Force given author name.")
    parser.add_option("-m", "--move",
                      action="store", type="string", dest="move",
                      help="Move source files to given directory after adding them")
    parser.add_option("-n", "--title-from-name",
                      action="store_true", default=False, dest="title_from_name",
                      help="Always use file name as book title (by default we use file name for doc/rtf/txt, but embedded matadata for pdf, epub, mobi and other formats).")
    (options, args) = parser.parse_args()
    if not args:
        parser.error("""No file or directory specified. Execute with:
    calibre_add_if_missing  /some/dire/ctory/name"
or
    calibre_add_if_missing  file.name otherfile.name dir.name
""")
    if options.move:
        if not os.path.isdir(options.move):
            parser.error("Parameter given for --move ('%s') is not a directory!" % options.move)
    return (options, args)


def run():
    """
    Run calibre_add_if_missing script
    """
    options, args = process_options()

    files_to_check = []
    for param in args:
        if os.path.isdir(param):
            files_to_check.extend(find_disk_files(param))
        else:
            files_to_check.append(param)

    # Preliminary grouping. We look for files with approximately the
    # same size (initially the script looked for identical files, but
    # .epub's are easily modified by calibre bookmarks and such)

    print("Loading calibre database contents")

    # Size of individual „chunk” (how big difference can still mean the
    # same file)
    CHUNK_SIZE = 1024  # 1kB, dodanie bookmarksów zwykle dorzuca 200-400 bajtów

    # size/CHUNK_SIZE (zaokrąglone w obie strony) -> set of files with that size
    known_by_calibre = defaultdict(lambda: set())

    for file_name in find_calibre_file_names(use_cache=options.cache):
        try:
            chunk = file_size(file_name) // CHUNK_SIZE
        except OSError as e:
            print("File {0} does not exist or can't be read, skipping from analysis.\n    Error details: {1}".format(file_name, str(e)))
            continue
        known_by_calibre[chunk].add(file_name)
        known_by_calibre[chunk+1].add(file_name)

    print("Checking books")

    added_count = 0
    skipped_count = 0
    for file_name in files_to_check:
        chunk = file_size(file_name) // CHUNK_SIZE
        candidates = known_by_calibre[chunk].union(known_by_calibre[chunk+1]).union(known_by_calibre[chunk-1])
        #print("Checking {0} (base chunk {1}) against {2}".format(file_name, chunk, ", ".join(candidates)))
        for c in candidates:
            if are_files_equivalent(file_name, c):
                print("Already present: %s (stored as %s)" % (file_name, c))
                skipped_count += 1
                break
        else:
            print("Not registered by calibre, adding:", file_name)
            if options.dry_run:
                continue

            # doc, rtf and txt files are notoriously bad at metadata extraction, better
            # force filename into the title to know what is the book about.
            # TODO: make this behaviour an option
            base_file_name = os.path.basename(file_name)
            m = re.match("^(.*)\.([a-z]+)$", base_file_name)
            #m = re.match("^(.*)\.(rtf|docx?|txt)$", base_file_name)
            force_title = None
            if m:
                if options.title_from_name  or ( m.group(2) in ['txt', 'doc', 'docx', 'rtf'] ):
                    force_title = m.group(1)

            add_to_calibre(file_name,
                           force_title=force_title,
                           force_tags=options.tag,
                           force_author=options.author)
            added_count += 1

        if options.move:
            if not options.dry_run: # we should not be here but better be safe than sorry
                shutil.move(file_name, options.move)

    print()
    print("%d files already present, %d added" % (skipped_count, added_count))
