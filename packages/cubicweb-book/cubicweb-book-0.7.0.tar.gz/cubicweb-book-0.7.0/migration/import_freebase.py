"""
To use this script:
cubicweb-ctl shell appid import_freebase.py number_of_books_to_import

number_of_books_to_import is optionnal, if not provided, all books
will be imported
"""

import freebase

from cubicweb.dataimport import CWImportController, RQLObjectStore

from cubes.book.migration.import_ol import gen_books, to_date
from cubes.book.migration.import_dbpedia import set_isbn, set_pages

def get_books(limit):
    query = {'type': '/book/book_edition', '*': None, 'binding': 'hardcover'}
    if limit:
        query['limit'] = int(limit)
    results = freebase.mqlreaditer(query)
    for book in results:
        try:
            bookinfo = {}
            bookinfo['title'] = unicode(book['book'])
            bookinfo['publish_date'] = to_date(book['publication_date'])
            bookinfo['cwuri'] = u'http://www.freebase.com'
            bookinfo['externaluri'] = unicode('%s/view%s' % (bookinfo['cwuri'], book['id']))
            if book.get('isbn'):
                bookinfo['isbn'] = book['isbn']
            if book.get('number_of_pages'):
                bookinfo['pages'] = book['number_of_pages']
                set_pages(bookinfo)
            bookinfo['authors_name'] = book['author_editor']
            if book.get('publisher'):
                print "publisher", book.get('publisher')
                bookinfo['publisher'] = unicode(book['publisher'])
                print "after"
            set_authors(bookinfo)
            set_isbn(bookinfo)
            yield bookinfo
        except Exception, e:
            print "EXCEPTION in get_books:", e

def set_authors(bookinfo):
    for name in bookinfo['authors_name']:
        query = {'type': '/book/author', 'name': name, '*': None, 'book_editions_published': bookinfo['title']}
        author = freebase.mqlread(query)
        if author:
            author_infos = {}
            author_infos['name'] = unicode(author['name'])
            author_infos['cwuri'] = u'http://www.freebase.com'
            author_infos['externaluri'] = unicode('%s/view%s' % (author_infos['cwuri'], author['id']))
            bookinfo.setdefault('authors', [])
            bookinfo['authors'].append(author_infos)



GENERATORS = []
CHK = []
GENERATORS.append( (gen_books, CHK) )
if __name__ == '__main__':
    import sys
    try:
        limit = sys.argv[4]
    except:
        limit = None

    # create controller
    ctl = CWImportController(RQLObjectStore(session))
    ctl.askerror = 1
    ctl.generators = GENERATORS
    ctl.data['books'] = get_books(limit)
    # run
    ctl.run()
