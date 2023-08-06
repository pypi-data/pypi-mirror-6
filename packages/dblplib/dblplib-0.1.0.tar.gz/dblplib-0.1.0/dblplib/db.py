from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
from sqlalchemy.orm import sessionmaker, mapper
from bibtexmodel import FIELDS, Document

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)
session = Session()
metadata = MetaData(bind=engine)

def insert(document):
    entry = Document()
    for field in FIELDS:
        if hasattr(document, field):
            entry.__setattr__(field, str(document.__getattribute__(field)))
        else:
            entry.__setattr__(field, '')
    session.add(entry)
    session.commit()

fields = [Column('key', String(255), primary_key=True)]

for field in FIELDS:
    if field == 'key': continue
    fields.append(Column(field, String(255)))

document_table = Table('bibtex_entry', metadata, *fields)

mapper(Document, document_table)

metadata.create_all(engine) 
