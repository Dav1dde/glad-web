from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from gladweb.database import Base


class SqlDatabase(object):
    def __init__(self, uri):
        self.engine = create_engine(uri, convert_unicode=True)
        self.session = scoped_session(sessionmaker(bind=self.engine))

    def create_all(self):
        Base.metadata.create_all(self.engine)

    @property
    def query(self):
        return self.session.query_property()
