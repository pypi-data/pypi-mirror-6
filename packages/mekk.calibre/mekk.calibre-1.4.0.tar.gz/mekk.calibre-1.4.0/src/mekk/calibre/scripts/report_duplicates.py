# -*- coding: utf-8 -*-

"""
Analyzes calibre database and reports possible duplicates (detected
using both actual books, and author/title matching). Prints the
report. Do not perform any changes, the report can be used to decide
which books to merge or remove using Calibre interface.

With `--html` prints report as HTML.

Example:

    calibre_report_duplicates

or

    calibre_report_duplicates --html > report.html
    firefox report.html

"""
from __future__ import print_function, unicode_literals

import sys
from collections import defaultdict
from argparse import ArgumentParser, FileType
import difflib
import re
from mekk.calibre.calibre_util import find_calibre_books
from mekk.calibre.disk_util import file_size, are_files_identical, file_extension
import six
from simhash import Simhash, SimhashIndex

# Expected similarity ratio for difflib.get_close_matches. Default 0.6
# is a little bit too small
EXPECTED_AUTHOR_SIMILARITY = 0.80
EXPECTED_TITLE_SIMILARITY = 0.75

class Report(object):

    def __init__(self, output):
        if output:
            self.output = output
        else:
            self.output = sys.stdout

    def start(self):
        self.items = dict()  # (id1,id2) => {book1:, book2:, observations:, merge_safe:, similarity_code:}
        self.begin()

    def note_book_pair(self, book1, book2):
        # Textual description of similarities and differences
        observations = []
        # Code description of similarities and differences (used later in report pruning)
        obs_codes = []
        # "Safe" merge means no data will be lost (either we remove binary
        # identical file, or merge differnet formats)
        merge_safe = True

        for author1 in book1.authors:
            for author2 in difflib.get_close_matches(
                author1, book2.authors,
                cutoff=EXPECTED_AUTHOR_SIMILARITY):
                if author1 == author2:
                    observations.append("Identical author %s" % author1)
                    obs_codes.append("A=")
                else:
                    observations.append("Similar authors %s and %s" % (
                            author1, author2))
                    obs_codes.append("A?")

        if book1.title == book2.title:
            observations.append("Identical title")
            obs_codes.append("T=")
        elif difflib.get_close_matches(book1.title, [book2.title],
                                       cutoff=EXPECTED_TITLE_SIMILARITY):
            observations.append("Similar titles")
            obs_codes.append("T?")

        files1 = dict((file_extension(name), name) for name in book1.files)
        files2 = dict((file_extension(name), name) for name in book2.files)
        all_exts = set(files1.keys())
        all_exts.update(files2.keys())

        for ext in all_exts:
            name1 = files1.get(ext)
            name2 = files2.get(ext)
            if name1 is None:
                observations.append("%s only in second book" % ext)
                obs_codes.append(ext + "1")
            elif name2 is None:
                observations.append("%s only in first book" % ext)
                obs_codes.append(ext + "1")
            else:
                size = file_size(name1)
                if size == file_size(name2) \
                        and are_files_identical(name1, name2):
                    observations.append(
                        "%s formats are identical (size %d)" % (
                            ext, size))
                    obs_codes.append(ext + "=")
                else:
                    observations.append(
                        "%s formats DIFFERENT (size %d - %d)" % (
                            ext, size, file_size(name2)))
                    merge_safe = False
                    obs_codes.append(ext + "!")

        similarity_code = ",".join(obs_codes)

        self.items[ tuple(sorted((book1.id, book2.id))) ] = dict(
            book1 = book1,
            book2 = book2,
            observations = observations,
            merge_safe = merge_safe,
            similarity_code = similarity_code,
            )
        #print >> sys.stderr, "%s ~ %s with %s" % (book1.id, book2.id, obs_codes)

    def note_similar_authors(self, group):
        self.authors_item(group)

    def stop(self):

        # Some report pruning is necessary to avoid cases where 10
        # similar books generate 55 similarity notes (for every
        # pair). If we know that a~b and a~c, with the same similarity kind,
        # and we find that b~c also, we can ignore it
        #
        # Checking is done in order of id's to avoid removal of pair we
        # used to deduce
        #

        self.progress("Skipping redundant matches...")

        # First let's make a struct  key => [ list of "later" matching keys
        similarity = defaultdict(lambda: dict())   # key1 => key2 => code
        for (k1, k2), desc in six.iteritems(self.items):
            similarity[k1][k2] = desc['similarity_code']

        # Main search
        skipped_count = 0
        for (k1,k2) in sorted(self.items.keys()):
            if not (k1,k2) in self.items:
                # already dropped
                continue
            code12 = self.items[(k1,k2)]['similarity_code']
            to_prune = []
            for (k3,code23) in six.iteritems(similarity[k2]):
                if code23 == code12:
                    code13 = similarity[k1].get(k3,"")
                    if code13 == code12:
                        to_prune.append(k3)
            for k3 in to_prune:
                # k1 ~ k3, k2 ~ k3, k1 ~ k2. Removing k2 ~ k3
                if (k2,k3) in self.items: # not yet removed
                    #print >> sys.stderr, "Skipping deduced match %s ~ %s (both similar to %s)" % (k2,k3,k1)
                    del self.items[ (k2,k3) ]
                    skipped_count += 1
        
        self.progress("... %d redundant matches dropped" % skipped_count)

        # Values to print
        matches = list(self.items.values())
        matches.sort(key=lambda match:\
                            (not match['merge_safe'], 
                             sorted(set(match['book1'].authors + match['book2'].authors)),
                             match['book1'].title, 
                             match['book2'].title, 
                             match['book1'].id, 
                             match['book2'].id))

        for match in matches:
            self.book_item(match['book1'], match['book2'], match['observations'], match['merge_safe'])

        self.end()

    def write(self, *items):
        print(*items, file=self.output)

    def progress(self, *items):
        print(*items, file=sys.stderr)

class TextReport(Report):

    def begin(self):
        pass

    def authors_item(self, authors_group):
        self.write('-' * 70)
        for author in sorted(authors_group):
            self.write('| ', author.encode("utf-8"))
        self.write('-' * 70)

    def book_item(self, book1, book2, observations, merge_safe):
        self.write("-" * 70)
        self.write(("| %-10s | %-30s | %-30s |" % (
            book1.id, book1.title.strip()[:30],
            ", ".join(a.strip() for a in book1.authors)[:30])).encode("utf-8"))
        self.write(("| %-10s | %-30s | %-30s |" % (
            book2.id, book2.title.strip()[:30],
            ", ".join(a.strip() for a in book2.authors)[:30])).encode("utf-8"))
        for obs in observations:
            self.write("|", obs.encode("utf-8"))
        self.write("|", merge_safe and "Merging books should be safe" \
                               or "Merging books may loose data")
        self.write("-" * 70)
        self.write()

    def end(self):
        pass


class HTMLReport(Report):

    def __init__(self, output, use_js):
        Report.__init__(self, output)
        self.use_js = use_js

    def begin(self):
        self.write("""<!DOCTYPE html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Calibre duplicates</title>
<style type="text/css">
table {
  width: 100%;
}
.odd.safe {
  background-color: #CFC;
}
.even.safe {
  background-color: #ADA;
}
.odd.unsafe {
  background-color: #FCC;
}
.even.unsafe {
  background-color: #DAA;
}
tr.first td {
  padding: 16px 4px 4px 4px;
}
tr.internal td {
  padding: 4px;
}
tr.last td {
  padding: 4px 4px 16px 4px;
}
</style>
""")
        if self.use_js:
            self.write("""
<script>
function drop_row(button) {
    var parent = button.parentNode;
    while(parent.nodeName != "tr" && parent.nodeName != "TR" && parent != null) {
        /* alert("Name: " + parent.nodeName + " local: " + parent.localName); */
        parent = parent.parentNode;
    }
    while(parent) {
       var nextRow = parent.nextSibling;
       parent.style.display = "none";
       parent = nextRow;
       while(parent && parent.nodeName != "TR" && parent.nodeName != "tr") {
           parent = parent.nextSibling;
       }
       if(parent && parent.className.search("first") != -1) {
          break;
       }
    }
}
</script>
""")
        self.write("""</head>
<body>
""")
        self.inside = None  # 'authors', 'books' lub None

    def _switch_table_if_necessary(self, table_name, lead_text=None):
        if self.inside and self.inside != table_name:
            self.write("</table>")
            self.inside = None
        if not self.inside and table_name:
            if lead_text:
                self.write(lead_text)
            self.write("<table cellspacing='0'>")
            self.inside = table_name
            self.row_number = 0

    def authors_item(self, authors_group):
        self._switch_table_if_necessary('authors', u"<h2>Similar authors</h2>")
        self.row_number += 1
        cls = "safe-odd" if self.row_number % 2 > 0 else "safe-even"
        self.write("<tr class='%s'><td>" % cls)
        for author in authors_group:
            self.write(author.encode("utf-8"))
            self.write("<br/>")
        self.write("</td></tr>")

    def book_item(self, book1, book2, observations, merge_safe):
        self._switch_table_if_necessary('books', u"<h2>Likely duplicate books</h2>")
        self.row_number += 1
        cls = "odd" if self.row_number % 2 > 0 else "even"
        if merge_safe:
            cls = cls + " safe"
        else:
            cls = cls + " unsafe"

        leftcol_items = [book1.id, book1.title] + book1.authors
        rightcol_items = [book2.id, book2.title] + book2.authors
        observations.append(
            merge_safe and "Book merge is safe" or "Book merge can loose data")

        rows = list(map(
            lambda l, c, r: (l or "", c or "", r or ""),
            leftcol_items, observations, rightcol_items))

        def write_row(row_no):
            classes = cls
            if row_no == 0:
                classes += " first"
            if row_no == len(rows) - 1:
                classes += " last"
            if row_no > 0 and row_no < len(rows) - 1:
                classes += " internal"
            left, diag, right = rows[row_no]
            if self.use_js and row_no == 0:
                button = """<td rowspan="{rowcount}">
<button onclick="drop_row(this);">Remove</button>
</td>""".format(rowcount = len(rows))
            else:
                button = ""
            self.write("""
<tr class="{classes}"><td>{left}</td><td>{diag}</td><td>{right}</td>{button}</tr>
""".format(classes=classes, left=left, right=right, diag=diag, button=button).encode("utf-8"))

        for row_no in range(0, len(rows)):
            write_row(row_no)

    def end(self):
        self._switch_table_if_necessary(None)
        self.write("""
</body>
</html>""")


def process_options():
    parser = ArgumentParser(description=u'Find possible duplicates in calibre database')
    parser.add_argument("-f", "--format",
                        required=True,
                        choices=['txt', 'html', 'js'],
                        help="Output format (plain text, plain html, or html with buttons to remove rows)")
    parser.add_argument("-o", "--output",
                        dest="output",
                        type=FileType('wb', 4096),
                        help="Save results to given file (instead of printing report to stdout)")
    parser.add_argument("-c", "--cache", 
                        action="store_true", default=False,
                        help="Use cached manifest to speed up")
    options = parser.parse_args()
    return options

_letter_regexp = re.compile(r'\w', re.UNICODE) # Crucial to match Russian letters etc
def make_simhash(text):
    return Simhash(text, reg=_letter_regexp)
    # Original is ur'[\w\u4e00-\u9fff]+' which does not match russian letters for example

def run():
    """
    Run calibre_report_duplicates
    """
    options = process_options()

    if options.format == "html":
        report = HTMLReport(options.output, use_js=False)
    elif options.format == "js":
        report = HTMLReport(options.output, use_js=True)
    elif options.format == "txt":
        report = TextReport(options.output)
    else:
        raise Exception("Unknown format: {0}".format(options.format))


    # (binary dupes detection helper) Mapping
    #     size -> [  (filename, book), (filename, book), ... ]
    # where filename points actual file of this size, and book is full
    # book info (id, uuid, title, isbn, files)
    books_of_size = defaultdict(lambda: [])

    # (author/title dupes detection helper) Mapping
    #     author -> [ book, book, ... ]
    books_by_author = defaultdict(lambda: [])

    # id -> book
    books_by_id = dict()

    report.progress("Loading books info...")

    for book in find_calibre_books(use_cache=options.cache):
        books_by_id[book.id] = book
        for file_name in book.files:
            size = file_size(file_name)
            books_of_size[size].append((file_name, book))
        for author in book.authors:
            books_by_author[author].append(book)

    report.progress("... book list loaded")

    likely_identical = set()  # pary id

    report.progress("Looking for identical files...")

    for size, items in six.iteritems(books_of_size):
        if len(items) <= 1:
            continue
        for first_idx in range(0, len(items)-1):
            first_file, first_book = items[first_idx]
            for second_idx in range(first_idx + 1, len(items)):
                second_file, second_book = items[second_idx]
                if are_files_identical(first_file, second_file):
                    likely_identical.add((min(first_book.id, second_book.id),
                                          max(first_book.id, second_book.id)))

    identical_count = len(likely_identical)
    report.progress("... analyzed, %d possible pairs found" % identical_count)

    report.progress("Loading and grouping authors...")

    author_index = SimhashIndex([])
    for author in books_by_author.keys():
        author_index.add(author, make_simhash(author))

    # List of sets of similar authors
    similar_authors_groups = []
    # Author -> [position(s) on the list above]
    authors_having_similar = defaultdict(lambda: [])

    for author in books_by_author.keys():
        ndp = author_index.get_near_dups(make_simhash(author))
        if ndp and len(ndp) > 1:
            ndpset = set(ndp)
            # Maybe we already mentioned this author, if so, maybe one
            # of the groups overlaps with this one
            identical_group = None
            for pos in authors_having_similar.get(author, []):
                if similar_authors_groups[pos] == ndpset:
                    identical_group = pos
                    break
            if not identical_group:
                identical_group = len(similar_authors_groups)
                similar_authors_groups.append(ndpset)
                for ia in ndpset:
                    authors_having_similar[ia].append(identical_group)
            #print("Author {0} similar to {1}".format(author, ", ".join(
            #    x for x in ndp if x != author)))

    report.progress("... analyzed, %d groups found, %d authors have similars" % (
        len(similar_authors_groups), len(authors_having_similar)))

    report.progress("Looking for matching authors and titles...")

    # Przeglądamy grupami wdg. autora ale łączymy podobnych autorów 
    processed_authors = set()

    for author, author_books in six.iteritems(books_by_author):
        # Maybe we handled him as similar to sb else
        if author in processed_authors:
            continue

        # Calculating group (if any)
        author_group = set([author])
        for grp in authors_having_similar.get(author, []):
            author_group.update(similar_authors_groups[grp])

        processed_authors.update(author_group)

        # Calculating books
        if len(author_group) > 1:
            books = sum((books_by_author[author_name]
                         for author_name in author_group), [])
            # duplicate pruning (book can have many authors)
            books = [books_by_id[id]
                     for id in set(book.id for book in books)]
        else:
            books = author_books
        if len(books) <= 1:
            continue

        # Looking for identical or similar titles
        all_titles = [book.title for book in books]
        per_title_count = {}                 # For identical titles guessing, SimhashIndex dedupes
        title_index = SimhashIndex([])   # For similarity guessing
        for curr_title in all_titles:
            title_index.add(curr_title, make_simhash(curr_title))
            per_title_count[curr_title] = 1 + per_title_count.get(curr_title, 0)

        for base_book in books:
            similar_titles = title_index.get_near_dups(make_simhash(base_book.title))
            has_identical = (per_title_count[base_book.title] > 1)
            #difflib.get_close_matches(
            #    base_book.title, all_titles,
            #    n=5, cutoff=EXPECTED_TITLE_SIMILARITY)
            if len(similar_titles) <= 1 and not has_identical:
                continue
            similar_books = [
                book
                for book in books
                if (book.title == base_book.title) or (book.title in similar_titles)
            ]
            for idx1 in range(0, len(similar_books)-1):
                book1 = similar_books[idx1]
                for idx2 in range(idx1 + 1, len(similar_books)):
                    book2 = similar_books[idx2]
                    # Skipping if books belong to the same series with different number
                    if book1.series and book2.series \
                            and (book1.series == book2.series) \
                            and (book1.series_idx != book2.series_idx):
                        continue
                    likely_identical.add((min(book1.id, book2.id),
                                          max(book1.id, book2.id)))

    report.progress("... analyzed, %d new pairs found" % (
        len(likely_identical) - identical_count))

    report.progress("Generating report.")

    report.start()

    for ag in similar_authors_groups:
        report.note_similar_authors(ag)

    for b1, b2 in likely_identical:
        report.note_book_pair(books_by_id[b1], books_by_id[b2])

    report.stop()
