# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Table, Text, Unicode, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Book(Base):
    __tablename__ = 'book'

    bookid = Column(BigInteger, primary_key=True)
    book = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    publication_date = Column(DateTime)
    page_num = Column(Integer, nullable=False)
    paragraph = Column(Integer, nullable=False)
    text = Column(Text(2147483647, 'Latin1_General_CI_AS'), nullable=False)
    date_added = Column(DateTime, nullable=False, server_default=text("(getdate())"))
    date_modified = Column(DateTime)


class Mag(Base):
    __tablename__ = 'mag'

    magid = Column(BigInteger, primary_key=True)
    mag = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    issue = Column(Unicode(10))
    issue_date = Column(DateTime)
    page_num = Column(Integer)
    group_key = Column(String(20, 'Latin1_General_CI_AS'))
    block_num = Column(Integer)
    paragraph = Column(Integer)
    text = Column(Text(2147483647, 'Latin1_General_CI_AS'), nullable=False)
    date_added = Column(DateTime, nullable=False, server_default=text("(getdate())"))
    date_modified = Column(DateTime)


class Species(Base):
    __tablename__ = 'species'

    speciesid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    latin = Column(String(50, 'Latin1_General_CI_AS'))
    protection = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    report_name = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    species_group = Column(String(50, 'Latin1_General_CI_AS'))
    species_type1id = Column(ForeignKey('species_type1.species_type1id'))
    catch_rank = Column(Integer, nullable=False, server_default=text("((0))"))
    target_rank = Column(Integer, nullable=False, server_default=text("((0))"))

    species_type1 = relationship('SpeciesType1')


class SpeciesAlia(Base):
    __tablename__ = 'species_alias'

    species_aliasid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    speciesid = Column(ForeignKey('species.speciesid'), nullable=False)
    species_alias_typeid = Column(ForeignKey('species_alias_type.species_alias_typeid'), nullable=False)

    species_alias_type = relationship('SpeciesAliasType')
    species = relationship('Species')


class SpeciesAliasConflict(Base):
    __tablename__ = 'species_alias_conflict'

    species_alias_conflictid = Column(Integer, primary_key=True)
    species_aliasid = Column(ForeignKey('species_alias.species_aliasid'), nullable=False)
    speciesid = Column(ForeignKey('species.speciesid'), nullable=False)
    comment = Column(Text(2147483647, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))

    species_alia = relationship('SpeciesAlia')
    species = relationship('Species')


class SpeciesAliasType(Base):
    __tablename__ = 'species_alias_type'

    species_alias_typeid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    comment = Column(Text(2147483647, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))


class SpeciesType(Base):
    __tablename__ = 'species_type'

    species_typeid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)


class SpeciesType1(Base):
    __tablename__ = 'species_type1'

    species_type1id = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    species_typeid = Column(ForeignKey('species_type.species_typeid'), nullable=False)

    species_type = relationship('SpeciesType')


class SubstSpecy(Base):
    __tablename__ = 'subst_species'

    subst_speciesid = Column(Integer, primary_key=True)
    family = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    species = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    species1 = Column(String(50, 'Latin1_General_CI_AS'))
    species2 = Column(String(50, 'Latin1_General_CI_AS'))
    species3 = Column(String(50, 'Latin1_General_CI_AS'))


t_v_err_species_alias_duplicate_accepted = Table(
    'v_err_species_alias_duplicate_accepted', metadata,
    Column('speciesid', String(50, 'Latin1_General_CI_AS'), nullable=False)
)


t_v_err_species_sans_accepted = Table(
    'v_err_species_sans_accepted', metadata,
    Column('speciesid', String(50, 'Latin1_General_CI_AS'), nullable=False)
)


t_v_species_alias_csv = Table(
    'v_species_alias_csv', metadata,
    Column('speciesid', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('csv', Unicode)
)


t_v_species_alias_csv_with_rank = Table(
    'v_species_alias_csv_with_rank', metadata,
    Column('speciesid', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('csv', Unicode),
    Column('catch_rank', Integer, nullable=False)
)


t_v_species_alias_recognised = Table(
    'v_species_alias_recognised', metadata,
    Column('speciesid', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('catch_rank', Integer, nullable=False),
    Column('species_alias_speciesid', String(50, 'Latin1_General_CI_AS')),
    Column('species_aliasid', String(50, 'Latin1_General_CI_AS')),
    Column('species_alias_typeid', String(50, 'Latin1_General_CI_AS'))
)
