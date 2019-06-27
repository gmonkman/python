# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String, Table, Unicode, text
from sqlalchemy.dialects.mssql import BIT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Gazetteer(Base):
    __tablename__ = 'gazetteer'
    __table_args__ = {'implicit_returning':False}
    gazetteerid = Column(BigInteger, primary_key=True)
    id = Column(BigInteger, nullable=False)
    source = Column(String(15, 'Latin1_General_CI_AS'), nullable=False)
    name = Column(Unicode(255))
    feature_class = Column(Unicode(50), nullable=False)
    feature_class1 = Column(String(250, 'Latin1_General_CI_AS'), nullable=False)
    x = Column(Float(53))
    y = Column(Float(53))
    ifca = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    eng_dist_m = Column(Float(53))
    county = Column(String(50, 'Latin1_General_CI_AS'))
    shape = Column(String(10, 'Latin1_General_CI_AS'))
    x_rnd = Column(Float(53))
    y_rnd = Column(Float(53))
    name_cleaned = Column(String(255, 'Latin1_General_CI_AS'))
    intertidalfid = Column(Integer)
    intertidalfiddistance = Column(Float(53))


t_v_gazetteer_word_count = Table(
    'v_gazetteer_word_count', metadata,
    Column('gazetteerid', BigInteger, nullable=False),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('name_cleaned', String(255, 'Latin1_General_CI_AS')),
    Column('n', Integer),
    Column('feature_class1',  String(250, 'Latin1_General_CI_AS')),
    Column('coast_dist_m', Float)

)
