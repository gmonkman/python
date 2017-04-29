# pylint: skip-file
# coding: utf-8
'''sql server database for my fish records'''

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Unicode, text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.ext.declarative import declarative_base


_BASE = declarative_base()
_META = _BASE.metadata


class Camera(_BASE):
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

    def __repr__(self):
        return "<Camera(cameraid=%i, camera='%s', manufacturer='%s', aperture_mm=%d, focal_distance_mm=%i, cmos_rows=%i, cmos_columns=%i, cmos_height_mm=%i, cmos_width_mm=%i)>" % (
            self.cameraid, self.camera, self.manufacturer, self.aperture_mm, self.focal_distance_mm, self.cmos_rows, self.cmos_columns, self.cmos_height_mm, self.cmos_width_mm)


class Housing(_BASE):
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

    def __repr__(self):
        return "<Housing(housingid=%i, housing='%s', laser_type='%s', lasers_nr=%i, b_b_to_b_lens_adjust=%i)>" % (
            self.housingid, self.housing, self.laser_type, self.lasers_nr, self.b_b_to_b_lens_adjust)


class HousingMount(_BASE):
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

    def __repr__(self):
        return "<Housing_mount(housing_mountid=%i, conversion_name='%s', subject_to_lens_conversion_mm=%i)>" % (
            self.housing_mountid, self.housingid, self.mountid, self.conversion_name, self.subject_to_lens_conversion_mm)


class Mount(_BASE):
    __tablename__ = 'mount'

    mountid = Column(Integer, primary_key=True)
    mount_name = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))

    def __repr__(self):
        return "<Mount(mountid=%i, mount_name='%s')>" % (
            self.mountid, self.mount_name)


class Sample(_BASE):
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

    camera = relationship('Camera', backref='cameras')
    housing_mount = relationship('HousingMount')
    sample_header = relationship('SampleHeader')
    species = relationship('Species')

    def __repr__(self):
        return "<Sample(sampleid=%i, unique_code='%s', tl_mm=%i, fl_mm=%i, weight_g=%i, maturity='%s', laser_mm=%i, measurer='%s',"
        "board_board_length_mm=%i, capture_resolution='%s', speciesid=%i)>" \
            % (self.sampleid, self.unique_code, self.tl_mm, self.fl_mm,
               self.weight_g, self.maturity, self.gutted, self.laser_mm,
               self.sample_headerid, self.measurer, self.cameraid, self.housing_mountid,
               self.board_board_length_mm, self.capture_resolution,
               self.useable_footage, self.comment, self.speciesid
               )


class SampleHeader(_BASE):
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

    def __repr__(self):
        return "<Sample_header(sample_headerid=%i, supplier='%s', stock_source='%s', stock_location='%s')>" \
            % (self.sample_headerid, self.visit_date, self.supplier, self.stock_source, self.stock_location)


class SampleLength(_BASE):
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
        nullable=True,
        server_default=text("((0))"))
    measured_resolution = Column(
        String(
            50,
            'Latin1_General_CI_AS'),
        nullable=False,
        server_default=text("('')"))
    comment = Column(Unicode)
    perspective_corrected_actual_mm = Column(Integer, nullable=True)
    lens_correction_mm = Column(Integer, nullable=True)
    perspective_corrected_estimate_mm = Column(Integer, nullable=True)
    perspective_corrected_estimate_iter_mm = Column(Integer, nullable=True)
    sample = relationship('Sample', backref='sample_lengths')

    def __repr__(self):
        return "<Sample_length(sample_lengthid=%i, estimate_mm=%i, ref_length_type='%s', ref_length_mm=%i, measured_resolution='%s', perspective_corrected_actual_mm=%i, lens_correction_mm=%i, perspective_corrected_estimate_iter_mm=%i)>" % (
            self.sample_lengthid, self.sampleid, self.estimate_mm, self.ref_length_type, self.ref_length_mm, self.measured_resolution, self.comment, self.perspective_corrected_actual_mm, self.lens_correction_mm, self.perspective_corrected_estimate_iter_mm)


class Species(_BASE):
    __tablename__ = 'species'

    speciesid = Column(Integer, primary_key=True)
    common_name = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    latin_name = Column(String(50, 'Latin1_General_CI_AS'))


t_v_lengths = Table(
    'v_lengths', _META,
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
