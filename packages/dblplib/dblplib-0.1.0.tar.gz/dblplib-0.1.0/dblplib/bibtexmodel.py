FIELDS = ['mdate', 'key', 'title', 'author', 'editor', 'year', 'ee', 'url',
    'crossref', 'abstract', 'note', 'cdrom', 'cite', 'pages', 'volume',
    'number', 'journal', 'publisher', 'booktitle', 'isbn', 'series', 'school',
    'type']

class Person(object):
    first_name = ''
    last_name = ''
    complete_name = ''
    
    def __unicode__(self):
        return self.complete_name

class Author(Person):
    def __init__(self):
        super(Author, self).__init__()

class Editor(Person):
    def __init__(self):
        super(Editor, self).__init__()

class Document(object):
    def __init__(self, mdate='', key=''):
        for field in FIELDS:
            self.__setattr__(field, '')
        self.mdate = mdate
        self.key = key
        self.authors = []
        self.editors = []
        
    def __str__(self):
        s = "Key: %s\nTitle: %s\nYear: %s\nEE: %s\nURL: %s" % (self.key, self.title, 
                                                               self.year, self.ee, self.url)
        for i, a in enumerate(self.authors):
            s += '\nAuthor %d: %s' % (i+1, unicode(a))
        for i, e in enumerate(self.editors):
            s += '\nEditor %d: %s' % (i+1, unicode(e))
            
        return s
