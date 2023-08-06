from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker, mapper
from bibtexmodel import FIELDS, Document

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData(bind=engine)

def search(*args, **kargs):
    if kargs.has_key('page'):
        page = kargs['page']
        del kargs['page']
    if kargs.has_key('amount_per_page'):
        amount = kargs['amount_per_page']
        del kargs['amount_per_page']
    if kargs.has_key('count'):
        count = kargs['count']
        del kargs['count']

    results = session.query(Document).filter_by(**kargs)

    if count:
        return results.count()

    if amount:
        results = results.limit(amount)
    if page: 
        results = results.offset(page*amount)

    return results

def insert(document):
    """Inserts a new entry to the storage."""
    entry = Document()
    for field in FIELDS:
        if hasattr(document, field):
            entry.__setattr__(field, str(document.__getattribute__(field)))
        else:
            entry.__setattr__(field, '')
    session.add(entry)
    session.commit()

def get(key, *args, **kargs):
    """Returns an entry according to the given key."""
    results = session.query(Document).filter(Document.key == key)
    if results.count() > 0:
        return results[0]
    else:
        return None

def delete(key, *args, **kargs):
    """Delete an entry according to the given key."""
    results = session.query(Document).filter(Document.key == key)
    if results.count() > 0:
        session.delete(results[0])
        session.commit()
    else:
        raise Exception('There is no entry with key = ' + key + '.')

def delete_all():
    for d in session.query(Document).all():
        session.delete(d)
    session.commit()

def count():
    """Returns the number of entries stored."""
    return session.query(Document).count()

# Create the database
fields = [Column('key', String(255), primary_key=True)]

for field in FIELDS:
    if field == 'key': continue
    fields.append(Column(field, String(255)))

document_table = Table('bibtex_entry', metadata, *fields)

mapper(Document, document_table)

metadata.create_all(engine) 
