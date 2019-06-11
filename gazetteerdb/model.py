# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Index, Integer, LargeBinary, NCHAR, String, TEXT, Table, Unicode, text, Float
from sqlalchemy.dialects.mssql import BIT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Gazetteer(Base):
    __tablename__ = 'gazetteer'

    gazetteerid = Column(BigInteger, primary_key=True)
    id = Column(BigInteger, nullable=False)
    source = Column(String(15, 'Latin1_General_CI_AS'), nullable=False)
    name = Column(String(255))
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
    cleaned = Column(BIT, nullable=False, server_default=text("((0))"))
    name_cleaned = Column(String(255))