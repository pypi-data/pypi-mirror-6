'''
Created on Dec 2, 2010

@author: yguarata
'''
import xml.parsers.expat
import HTMLParser
import ir
import db
from StringIO import StringIO
from bibtexmodel import *

unescape = HTMLParser.HTMLParser().unescape

entry_names = set(["article", "inproceedings", "proceedings", "mastersthesis", 
	"phdthesis", "book", "incollection"])

def parse_file(path, *args, **kargs):
    """Parses the file pointed by 'path' containing the DBLP bibtex entries 
    and stores the entries."""
    print 'Parsing %s...' % path
    return DBLPXMLParser(*args, **kargs).parse_file(open(path, 'r'))
    
def parse(xml_content, *args, **kargs):
    """Parses the 'xml_content' containing the DBLP bibtex entries 
    and stores the entries."""
    return DBLPXMLParser(*args, **kargs).parse(xml_content)

class DBLPXMLParser:
    
    def __init__(self, *args, **kargs):
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.CharacterDataHandler = self.handleCharData
        self.parser.StartElementHandler = self.handleStartElement
        self.parser.EndElementHandler = self.handleEndElement
        self.line_count = None
        self.xml_content = None
        self.file = None
        self.doc_temp = None
        self.chars = ''
    
    def init(self):
        print "Initiating..."
        self.line_count = self.__count_lines()
    
    def __count_lines(self):
        # Get total line number
        if self.file != None:
            for i, l in enumerate(self.file):
                pass
            self.file.seek(0)
            return i + 1
        elif self.xml_content != None:
            for i, l in enumerate(self.xml_content.split('\n')):
                pass
            return i + 1
    
    def get_progress(self):
        current_line = self.parser.CurrentLineNumber
        return float(current_line)/float(self.line_count)
    
    def parse(self, xml_content):
        self.xml_content = unescape(xml_content).encode('utf-8')
        self.init()
        self.parser.Parse(self.xml_content, 1)
        print 'Commiting index...'
        ir.writer.commit()
    
    def parse_file(self, file_):
        self.file = file_
        self.init()
        self.parser.ParseFile(file_)
        print 'Commiting index...'
        ir.writer.commit()

    def handleCharData(self, data):
        self.chars = data
    
    def handleStartElement(self, name, attrs):
        if not name:
            return
        
        name = name.lower()
        
        if name in entry_names:
            self.doc_temp = Document(attrs['mdate'], attrs['key'])
            self.doc_temp.type = name
        
    def handleEndElement(self, name):
        if not name or not self.doc_temp:
            return
        
        name = name.lower()
        
        if name == "author":
            author = Author()
            author.complete_name = self.chars
            self.doc_temp.authors.append(author)
            if self.doc_temp.author:
                self.doc_temp.author = ', '.join([self.doc_temp.author, self.chars])
            else:
                self.doc_temp.author = self.chars
        
        elif name == "editor":
            editor = Editor()
            editor.complete_name = self.chars
            self.doc_temp.editors.append(editor)
            if self.doc_temp.editor:
                self.doc_temp.editor = ', '.join([self.doc_temp.editor, self.chars])
            else:
                self.doc_temp.editor = self.chars
        
        elif name == "title":
            self.doc_temp.title = self.chars
        
        elif name == "crossref":
            self.doc_temp.crossref = self.chars
            
        elif name == "pages":
            self.doc_temp.pages = self.chars
                
        elif name == "year":
            self.doc_temp.year = self.chars
            
        elif name == "volume":
            if '-' in self.chars:
                self.doc_temp.volume = self.chars.split('-')[0]
                self.doc_temp.number = self.chars.split('-')[1]
            else:
                self.doc_temp.volume = self.chars
        
        elif name == "number":
            if not '-' in self.chars:
                self.doc_temp.number = self.chars
            
        elif name == "ee":
            self.doc_temp.ee = self.chars
            
        elif name == "url":
            self.doc_temp.url = self.chars
            
        elif name == "series":
            self.doc_temp.series = self.chars
            
        elif name == "isbn":
            self.doc_temp.isbn = self.chars
            
        elif name == "publisher":
            self.doc_temp.publisher = self.chars
            
        elif name == "school":
            self.doc_temp.school = self.chars
            
        elif name == "booktitle":
            self.doc_temp.booktitle = self.chars
            
        elif name == "journal":
            self.doc_temp.journal = self.chars

        elif name == "note":
            self.doc_temp.journal = self.chars

        elif name == 'cdrom':
            self.doc_temp.cdrom = self.chars

        elif name == 'cite':
            self.doc_temp.cite = self.chars

        elif name in entry_names:
            # End of one entry parsing.
            ir.add_document(self.doc_temp)
            db.insert(self.doc_temp)
            print 'Progress:', round(self.get_progress() * 100.0, 2), '%'

        elif name in ("sup", "sub", "i", "tt"):
            # Title with HTML formating
            self.doc_temp.title += self.chars

        else:
            print "Got an unexpected tag: " + name

