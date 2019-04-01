# pylint: disable=C0103, too-few-public-methods, locally-disabled, no-self-use, unused-argument
'''Manage database operations for the mag table'''
from sqlalchemy.orm import Session as _Session
from sqlalchemy.orm import sessionmaker

from mmodb.model import t_mag as Mag
import dblib.alchemylib as _alc
import mmodb as _mmodb


Session = sessionmaker(bind=_mmodb.ENGINE, autocommit=False)


