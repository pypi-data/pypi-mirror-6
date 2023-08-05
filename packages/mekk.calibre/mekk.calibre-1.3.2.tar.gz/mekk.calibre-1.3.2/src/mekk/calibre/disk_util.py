# -*- coding: utf-8 -*-

import os.path
import os
import filecmp
import zipfile

def dir_depth(root_dir, checked_dir):
    """
    Calculates directory depth (= level of subdirectory belonging) of checked_dir under root_dir.
    For example:

    >>> dir_depth("/some/dir", "/some/dir")
    0
    >>> dir_depth("/some/dir", "/some/dir/subdir")
    1
    >>> dir_depth("/some/dir", "/some/dir/subdir/another/yet_another")
    3
    >>> dir_depth("/some/dir", "/some/other/dir")
    Traceback...
    Exception: Directory /some is not subdirectory of /some/dir
    """
    if len(root_dir) >= len(checked_dir):
        if root_dir == checked_dir:
            return 0
        else:
            raise Exception("Directory %s is not subdirectory of %s" % (checked_dir, root_dir))
    lead, rest = os.path.split(checked_dir)
    return 1 + dir_depth(root_dir, lead)

def find_disk_files(root,
                    ignored_names=("metadata.db", "metadata.opf"),
                    ignored_extensions=(".jpg", ".gif"),
                    min_level = 0,
                    max_level = 9999999):
    """
    Locates and returns all disk files under directory root, ignoring
    those unnecessary. Yields all files found (full names).

    root - the root directory for files beeing looked up
    ignored_names - the list of (short) filenames to ignore
    ignored_extensions - the list of file extensions (suffixes) to ignore
    min_level - minimum count of directories between root and file (0 means any file, 1 skips top-level files, etc)
    max_level - maximum count of directories between root and file
    """
    for dirname, subdirs, files in os.walk(root, topdown = True):
        depth = dir_depth(root, dirname)
        if depth == max_level:
            subdirs[:] = []
        if depth < min_level:
            pass
        elif depth <= max_level:
            for short_name in files:
                if short_name in ignored_names:
                    continue
                if any(short_name.endswith(ext) for ext in ignored_extensions):
                    continue
                full_name = os.path.join(dirname, short_name)
                yield full_name

def file_size(filename):
    """
    Returns file size in bytes.
    """
    stat = os.stat(filename)
    return stat.st_size


def file_extension(file_path):
    """
    Returns bare extension for given file. The extension starts with .
    and is always lowercase - so example return values are ".pdf" or ".doc".
    """
    return os.path.splitext(file_path)[1].lower()


def are_files_identical(filename1, filename2):
    """
    Checks whether two files are binary identical 
    """
    if filecmp.cmp(filename1, filename2, False):
        return True
    else:
        return False

def are_epubs_equivalent(filename1, filename2):
    """
    Checks whether two epub files are equivalent (identical or almost identical with respect
    to content)
    """
    items1 = zipfile.ZipFile(filename1).infolist()
    items2 = zipfile.ZipFile(filename2).infolist()
    items1.sort(key = lambda item: item.filename)
    items2.sort(key = lambda item: item.filename)

    # Przeczesujemy rozdzielając na pliki identyczne, różne i istniejące tylko z jednej strony
    identical, different, left_only, right_only = [], [], [], []

    while items1 and items2:
        if items1[0].filename == items2[0].filename:
            f1 = items1.pop(0)
            f2 = items2.pop(0)
            if f1.CRC == f2.CRC and f1.file_size == f2.file_size:
                identical.append(f1.filename)
            else:
                different.append(f1.filename)
        elif items1[0].filename < items2[0].filename:
            f1 = items1.pop(0)
            left_only.append(f1.filename)
        else:
            f2 = items2.pop(0)
            right_only.append(f2.filename)
    if items1:
        left_only.extend(x.filename for x in items1)
    if items2:
        right_only.extend(x.filename for x in items2)

    # Remove fonts, universal CSS-s and similar things from identical to avoid reporting them
    identical = [x for x in identical
                 if not x.endswith(".otf") and not x.endswith(".ttf") \
                    and not x.endswith(".css") \
                    and not x.endswith("container.xml") \
                    and not x == "mimetype" ]

    if len(identical) < 3:  # let's have something
        #print("Assuming epubs {0} and {1} are different as they have no or almost no common content".format(
        #    filename1, filename2))
        return False

    if not (different or left_only or right_only):
        print("Epubs {0} and {1} are practically identical as they have identical content".format(
            filename1, filename2))
        return True

    # Dropping files we do not care that much
    def ignore(fname):
        return fname in ["META-INF/calibre_bookmarks.txt"]

    left_only = [ x for x in left_only if not ignore(x) ]
    right_only = [ x for x in right_only if not ignore(x) ]
    different = [ x for x in different if not ignore(x) ]
        
    if not (different or left_only or right_only):
        print("Epubs {0} and {1} are practically identical as they have almost identical content (not counting calibre_bookmarks and such)".format(
            filename1, filename2))
        return True

    print("Epubs {0} and {1} are different as they have content differences (different: {2}, left only: {3}, right only: {4}, identical: {5} files)".format(
        filename1, filename2, ", ".join(different), ", ".join(left_only), ", ".join(right_only), len(identical)))
    return False

def are_files_equivalent(filename1, filename2):
    """
    Checks whether two files are binary identical OR the only differences
    are non-important from the ebook point of view (like the same zip packed
    with different compression or with calibre_bookmarks added)
    """
    if are_files_identical(filename1, filename2):
        return True
    #print "--{0},{1},{2},{3}--".format(filename1, filename2, file_extension(filename1), file_extension(filename2))
    if (file_extension(filename1) == ".epub") and (file_extension(filename2) == ".epub"):
        if are_epubs_equivalent(filename1, filename2):
            return True
    return False
