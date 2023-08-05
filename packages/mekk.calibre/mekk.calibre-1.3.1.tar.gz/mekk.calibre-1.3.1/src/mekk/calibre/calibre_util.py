# -*- coding: utf-8 -*-

"""
Wrappery dla komend wykonywanych na Calibre
"""
from __future__ import print_function

import os, subprocess, re, time, sys
from lxml import objectify
from collections import namedtuple
from tempfile import NamedTemporaryFile
from shutil import copyfile

from mekk.calibre.config import standard_config, CONFIG_LOCATION
CONFIG = standard_config()

############################################################
# Internal helpers
############################################################

DAY_SECONDS = 24 * 60 * 60  # 24 hours
MAX_CACHE_AGE = 1 * DAY_SECONDS

def calibre_query_files(search=None, use_cache=False):
    """
    Iterates over calibre database, yielding item for each file.
    Starts from newest, apply search criteria if given
    """
    # http://calibre-ebook.com/user_manual/cli/calibredb.html#calibredb-catalog
    options = []
    if search:
        options.extend(["--search", search])
    #if sort_by:
    #    options.extend(["--sort-by", sort_by])
    
    # Does not work in 1.0
    #options.extend(["--sort-by", "id"])
    options.extend(["--sort-by", "timestamp"])

    def return_from_catalog(catalog_file):
        return objectify.parse(open(catalog_file))\
                        .getroot()\
                        .iterchildren(reversed=True)

    def generate_catalog(catalog_file, options):
        try:
            subprocess.check_call(
                [CONFIG.calibredb, "catalog", catalog_file] + options)
        except OSError as err:
            if err.errno == 2:
                raise Exception("""calibredb (configured as %s) not found.
    Install Calibre, or edit %s to set proper path to it.""" % (
                        CONFIG.calibredb, CONFIG_LOCATION))
            else:
                raise

    cached_catalog_file = os.path.join(CONFIG.cache_dir, "catalog.xml")

    # We can use cached copy if (a) we do not search and (b) it exists and (c) it is fresh
    if (search is None) and use_cache:
        if os.path.exists(cached_catalog_file):
            cache_age = time.time() - os.stat(cached_catalog_file).st_mtime
            if cache_age <= MAX_CACHE_AGE:
                print("Reusing cached catalog ({0})".format(cached_catalog_file))
                return return_from_catalog(cached_catalog_file)
            else:
                print("Cached catalog {0} is old ({1} days), generating new copy".format(
                    cached_catalog_file, cache_age//DAY_SECONDS))
    
    temp_catalog_file = NamedTemporaryFile(suffix=".xml", delete=False)
    temp_catalog_file.close()
    temp_catalog_file = temp_catalog_file.name

    try:
        # Generate catalog to temporary file
        generate_catalog(temp_catalog_file, options)

        # If it went OK, and we do not search, preserve catalog for future
        # (whether we wanted to use cache, or not, even if not, in future we may want it)
        if search is None:
            copyfile(temp_catalog_file, cached_catalog_file)

        return return_from_catalog(temp_catalog_file)
    finally:
        os.remove(temp_catalog_file)

############################################################
# Public interface - general functions
############################################################


def find_calibre_file_names(use_cache=False):
    """
    Yields all files registered in Calibre database (just filenames)
    """
    for elem in calibre_query_files(use_cache=use_cache):
        try:
            files = [fmtel.text
                     for fmtel in elem.formats.iterchildren("format")]
            for file_name in files:
                yield file_name
        except AttributeError:
            print("Warning: book %s (%s) has no file associated." % (
                elem.id.text, elem.title.text.encode("utf-8")), file=sys.stderr)


FileItem = namedtuple('FileItem', 'id uuid title isbn files authors series series_idx')


def find_calibre_books(search=None, use_cache=False):
    """
    Yields all books (or all books matching given search, if specified)

    Routine yields objects with fields:
       id,
       uuid,
       title,
       isbn,   # can be None
       files  (list of all book formats/files)
       authors (list of all authors)
       series  (series name or None)
       series_idx (index in series or None)
    """
    for item_no, elem in enumerate(calibre_query_files(search, use_cache=use_cache)):
        if hasattr(elem, "isbn"):
            isbn = elem.isbn.text
        else:
            isbn = None
        try:
            files = [fmtel.text
                     for fmtel in elem.formats.iterchildren("format")]
        except AttributeError:
            files = []
            print("Warning: book %s (%s) has no file associated." % (
                    elem.id.text, elem.title.text.encode("utf-8")), file=sys.stderr)
        try:
            authors = [fmtel.text
                       for fmtel in elem.authors.iterchildren("author")]
        except AttributeError:
            authors = []
            print("Warning: book %s (%s) has no author associated." % (
                    elem.id.text, elem.title.text.encode("utf-8")), file=sys.stderr)
        if hasattr(elem, "series"):
            series = elem.series.text
            series_idx = elem.series.attrib["index"]
        else:
            series, series_idx = None, None

        yield FileItem(id=elem.id.text,
                       uuid=elem.uuid.text,
                       title=elem.title.text,
                       isbn=isbn,
                       files=files,
                       authors=authors,
                       series=series,
                       series_idx=series_idx)


def add_to_calibre(filename, 
                   use_calibre_duplicate_checking = False,
                   force_title = None,
                   force_author = None,
                   force_tags = None):
    """
    Add new book to calibre. filename is a file containing the book
    (which lies outside calibre directory and will be copied).

    If use_calibre_duplicate_checking leaves active Calibre duplicate checking (which
    is based on title only, so often too restrictive).
    """
    print("Importing", filename)
    cmd = [CONFIG.calibredb, "add"]
    if not use_calibre_duplicate_checking:
        cmd.append("--duplicates")
    if force_title:
        cmd.extend(["--title", force_title])
    if force_author:
        cmd.extend(["--authors", force_author])
    if force_tags:
        cmd.extend(["--tags", force_tags])
    cmd.append(filename)
    subprocess.check_call(cmd)
    print(" ... imported")


def add_format_to_calibre(item_id, filename):
    """
    Add new format to existing book. item_id is a calibre book identifier,
    filename is a file containing the new "format" (which lies outside
    calibre directory and will be copied).
    """
    print(" ... importing %s as new format for item %s" % (filename, item_id))
    subprocess.check_call(
        [CONFIG.calibredb, "add_format", item_id, filename])
    print(" ... imported")


DeviceItem = namedtuple('DeviceItem', 'full_path file_name device_dirs')

def _parse_device_lslr_output(output_text):
    current_path = None
    mount_point = None
    dir_re=re.compile("^(/.*):$")
    file_re=re.compile("-(?:[-r][-w][-x]){3} +\d+ +\d{4}-\d{1,2}-\d{1,2} +\d{1,2}:\d{1,2} +(.*)$")
    for line in output_text.split("\n"):
        m = dir_re.match(line)
        if m:  # Directory title
            current_path = m.group(1)
            if mount_point is None:
                mount_point = current_path
        else:
            m = file_re.match(line)
            if m: # Normal file
                name = m.group(1)
                dirs = os.path.dirname(name).replace(mount_point,"").split("/")
                yield DeviceItem(full_path = os.path.join(current_path, name),
                                 file_name = name,
                                 device_dirs = dirs)

def find_device_files():
    """
    Iterates over files on the connected device. For every file yields
    the tuple consisting of:

    - full_path - full path, including mount point, mostly used to read file content etc
    - file_name - short file name (only the file itself)
    - device_dirs - splitted directory path on the device (first item is root directory
      on the device file belongs to, last item is the directory the file belongs to)
    """
    try:
        output = subprocess.Popen(
            [CONFIG.ebook_device, "ls", "-lR", "/"],
            stdout=subprocess.PIPE).communicate()[0]
    except OSError as err:
        if err.errno == 2:
            raise Exception("""calibredb (configured as %s) not found.
Install Calibre, or edit %s to set proper path to it.""" % (
                    CONFIG.calibredb, CONFIG_LOCATION))
        else:
            raise
    
    return _parse_device_lslr_output(output)

############################################################
# Public interface - specific-task functions
############################################################


def save_isbn(item, isbn):
    print("Saving isbn %s to book %s" % (isbn, item))
    opf = subprocess.Popen(
        [CONFIG.calibredb, "show_metadata", item.id, "--as-opf"],
        stdout=subprocess.PIPE).communicate()[0]
    opf = opf.replace(
        "</metadata>",
        """<dc:identifier opf:scheme="ISBN">%s</dc:identifier></metadata>""" \
            % isbn)
    opf_file = NamedTemporaryFile(suffix=".opf", delete=False)
    opf_file.write(opf)
    opf_file.close()
    subprocess.check_call(
        [CONFIG.calibredb, "set_metadata", item.id, opf_file.name])
    os.remove(opf_file.name)
