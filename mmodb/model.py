# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, NCHAR, String, TEXT, Table, Unicode, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Book(Base):
    __tablename__ = 'book'

    bookid = Column(BigInteger, primary_key=True)
    book = Column(String(250, 'Latin1_General_CI_AS'))
    publication_date = Column(DateTime)
    page_num = Column(Integer, nullable=False)
    para_num = Column(Integer, nullable=False)
    para_text = Column(TEXT(2147483647, 'Latin1_General_CI_AS'), nullable=False)
    date_added = Column(DateTime, nullable=False, server_default="text(getdate())")
    date_modified = Column(DateTime)


class Cb(Base):
    __tablename__ = 'cb'

    cbid = Column(Integer, primary_key=True)
    boat = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default="text(getdate())")
    harbour = Column(String(50, 'Latin1_General_CI_AS'))
    skipper = Column(String(50, 'Latin1_General_CI_AS'))
    website = Column(String(50, 'Latin1_General_CI_AS'))
    boat_size = Column(String(50, 'Latin1_General_CI_AS'))
    passengers = Column(String(50, 'Latin1_General_CI_AS'))
    type_of_fishing = Column(String(336, 'Latin1_General_CI_AS'))
    species_targetted = Column(String(902, 'Latin1_General_CI_AS'))
    hours_of_availability = Column(String(71, 'Latin1_General_CI_AS'))
    months_of_operation = Column(String(94, 'Latin1_General_CI_AS'))
    days_per_week = Column(String(111, 'Latin1_General_CI_AS'))
    catch_details_on_cbuk = Column(String(50, 'Latin1_General_CI_AS'))
    dedicated_to_angling = Column(String(146, 'Latin1_General_CI_AS'))
    economic_survey = Column(String(131, 'Latin1_General_CI_AS'))
    catch_survey = Column(String(107, 'Latin1_General_CI_AS'))
    own_diary_or_records = Column(String(94, 'Latin1_General_CI_AS'))
    keep_a_monthly_diary = Column(String(119, 'Latin1_General_CI_AS'))
    weekly_diary = Column(String(50, 'Latin1_General_CI_AS'))
    how_provide_info = Column(String(132, 'Latin1_General_CI_AS'))
    notes = Column(String(404, 'Latin1_General_CI_AS'))
    code = Column(String(182, 'Latin1_General_CI_AS'))
    notes1 = Column(String(176, 'Latin1_General_CI_AS'))
    boat_noquote = Column(String(100, 'Latin1_General_CI_AS'))


class Mag(Base):
    __tablename__ = 'mag'

    magid = Column(BigInteger, primary_key=True)
    mag = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    issue = Column(NCHAR(10))
    issue_date = Column(DateTime)
    page_num = Column(Integer)
    group_key = Column(String(20, 'Latin1_General_CI_AS'))
    block_num = Column(Integer)
    paragraph = Column(Integer)
    text = Column(TEXT(2147483647, 'Latin1_General_CI_AS'), nullable=False)
    date_added = Column(DateTime, nullable=False, server_default="text(getdate())")
    date_modified = Column(DateTime)


class SpeciesAliasType(Base):
    __tablename__ = 'species_alias_type'

    species_alias_typeid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    comment = Column(TEXT(2147483647, 'Latin1_General_CI_AS'), nullable=False, server_default="text(getdate())")


class SpeciesType(Base):
    __tablename__ = 'species_type'

    species_typeid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)


class SubstSpecy(Base):
    __tablename__ = 'subst_species'

    subst_speciesid = Column(Integer, primary_key=True)
    family = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    species = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    species1 = Column(String(50, 'Latin1_General_CI_AS'))
    species2 = Column(String(50, 'Latin1_General_CI_AS'))
    species3 = Column(String(50, 'Latin1_General_CI_AS'))


class Ugc(Base):
    __tablename__ = 'ugc'

    postid = Column(Integer, primary_key=True)
    source = Column(String(250, 'Latin1_General_CI_AS'), nullable=False)
    published_date = Column(DateTime)
    date_added = Column(DateTime, nullable=False, server_default="text(getdate())")
    date_modified = Column(DateTime)
    board = Column(String(250, 'Latin1_General_CI_AS'))
    content_identifier = Column(String(50, 'Latin1_General_CI_AS'))
    who = Column(String(50, 'Latin1_General_CI_AS'))
    txt = Column(TEXT(2147483647, 'Latin1_General_CI_AS'), nullable=False)
    url = Column(String(500, 'Latin1_General_CI_AS'))
    title = Column(String(500, 'Latin1_General_CI_AS'))


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


class SpeciesType1(Base):
    __tablename__ = 'species_type1'

    species_type1id = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    species_typeid = Column(ForeignKey('species_type.species_typeid'), nullable=False)

    species_type = relationship('SpeciesType')


class Species(Base):
    __tablename__ = 'species'

    speciesid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    latin = Column(String(50, 'Latin1_General_CI_AS'))
    protection = Column(TEXT(2147483647, 'Latin1_General_CI_AS'))
    report_name = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default="text(getdate())")
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
    comment = Column(TEXT(2147483647, 'Latin1_General_CI_AS'), nullable=False, server_default="text(getdate())")

    species_alia = relationship('SpeciesAlia')
    species = relationship('Species')
