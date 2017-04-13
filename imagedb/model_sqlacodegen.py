# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Table, Unicode, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Camera(Base):
    __tablename__ = 'camera'

    cameraid = Column(Integer, primary_key=True)
    camera = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    manufacturer = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    aperture_mm = Column(
        Float(53),
        nullable=False,
        server_default=text("((0))"))
    focal_distance_mm = Column(
        Integer,
        nullable=False,
        server_default=text("((0))"))
    cmos_rows = Column(Integer)
    cmos_columns = Column(Integer)
    cmos_height_mm = Column(Integer)
    cmos_width_mm = Column(Integer)


class Housing(Base):
    __tablename__ = 'housing'

    housingid = Column(Integer, primary_key=True)
    housing = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    laser_type = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    lasers_nr = Column(Integer, nullable=False, server_default=text("((0))"))
    b_b_to_b_lens_adjust = Column(
        Integer,
        nullable=False,
        server_default=text("((0))"))


class HousingMount(Base):
    __tablename__ = 'housing_mount'

    housing_mountid = Column(Integer, primary_key=True)
    housingid = Column(ForeignKey('housing.housingid'), nullable=False)
    mountid = Column(ForeignKey('mount.mountid'), nullable=False)
    conversion_name = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    subject_to_lens_conversion_mm = Column(
        Integer, nullable=False, server_default=text("((0))"))

    housing = relationship('Housing')
    mount = relationship('Mount')


class Mount(Base):
    __tablename__ = 'mount'

    mountid = Column(Integer, primary_key=True)
    mount_name = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))


class Sample(Base):
    __tablename__ = 'sample'

    sampleid = Column(Integer, primary_key=True)
    unique_code = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    tl_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    fl_mm = Column(Integer)
    weight_g = Column(Integer)
    maturity = Column(String(50, 'Latin1_General_CI_AS'))
    gutted = Column(BIT, nullable=False, server_default=text("((0))"))
    laser_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    sample_headerid = Column(
        ForeignKey('sample_header.sample_headerid'),
        nullable=False)
    measurer = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    cameraid = Column(ForeignKey('camera.cameraid'), nullable=False)
    housing_mountid = Column(
        ForeignKey('housing_mount.housing_mountid'),
        nullable=False)
    board_board_length_mm = Column(
        Integer,
        nullable=False,
        server_default=text("((0))"))
    capture_resolution = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    useable_footage = Column(BIT, nullable=False, server_default=text("((0))"))
    comment = Column(Unicode)
    speciesid = Column(ForeignKey('species.speciesid'))

    camera = relationship('Camera')
    housing_mount = relationship('HousingMount')
    sample_header = relationship('SampleHeader')
    species = relationship('Species')


class SampleHeader(Base):
    __tablename__ = 'sample_header'

    sample_headerid = Column(Integer, primary_key=True)
    visit_date = Column(
        DateTime,
        nullable=False,
        server_default=text("(getdate())"))
    supplier = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    stock_source = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    stock_location = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))


class SampleLength(Base):
    __tablename__ = 'sample_length'

    sample_lengthid = Column(Integer, primary_key=True)
    sampleid = Column(ForeignKey('sample.sampleid'), nullable=False)
    estimate_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    ref_length_type = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    ref_length_mm = Column(
        Integer,
        nullable=False,
        server_default=text("((0))"))
    optical_lens_correction = Column(
        BIT, nullable=False, server_default=text("((0))"))
    measured_resolution = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    comment = Column(Unicode)

    sample = relationship('Sample')


class Species(Base):
    __tablename__ = 'species'

    speciesid = Column(Integer, primary_key=True)
    common_name = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    latin_name = Column(String(50, 'Latin1_General_CI_AS'))


t_v_lengths = Table(
    'v_lengths', metadata,
    Column('sampleid', Integer, nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('lens_subject_distance', Integer),
    Column('laser_corr', Integer),
    Column('bg_corr', Integer),
    Column('fg_corr', Integer),
    Column('laser_sans_corr', Integer),
    Column('bg_sans_corr', Integer),
    Column('fg_sans_corr', Integer)
)
