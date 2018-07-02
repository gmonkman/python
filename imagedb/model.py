# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, String, Table, Text, Unicode, text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Camera(Base):
    __tablename__ = 'camera'

    cameraid = Column(Integer, primary_key=True)
    camera = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    manufacturer = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    aperture_mm = Column(Float(53))
    focal_distance_mm = Column(Float(53))
    cmos_rows = Column(Integer)
    cmos_columns = Column(Integer)
    cmos_height_mm = Column(Float(53))
    cmos_width_mm = Column(Float(53))
    calib_lens_subj_distance_mm = Column(Float(53), nullable=False, server_default=text("((0))"))
    calib_res_x = Column(Float(53), nullable=False, server_default=text("((0))"))
    calib_res_y = Column(Float(53), nullable=False, server_default=text("((0))"))
    calib_marker_length_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    calib_marker_length_px = Column(Float(53), nullable=False, server_default=text("((0))"))


class Housing(Base):
    __tablename__ = 'housing'

    housingid = Column(Integer, primary_key=True)
    housing = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    laser_type = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    lasers_nr = Column(Integer)
    b_b_to_b_lens_adjust = Column(Integer, nullable=False, server_default=text("((0))"))


class HousingMount(Base):
    __tablename__ = 'housing_mount'

    housing_mountid = Column(Integer, primary_key=True)
    housingid = Column(ForeignKey('housing.housingid'), nullable=False)
    mountid = Column(ForeignKey('mount.mountid'), nullable=False)
    conversion_name = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    subject_to_lens_conversion_mm = Column(Integer, nullable=False, server_default=text("((0))"))

    housing = relationship('Housing')
    mount = relationship('Mount')


class Mount(Base):
    __tablename__ = 'mount'

    mountid = Column(Integer, primary_key=True)
    mount_name = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))


class Sample(Base):
    __tablename__ = 'sample'

    sampleid = Column(Integer, primary_key=True)
    unique_code = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    tl_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    fl_mm = Column(Integer)
    weight_g = Column(Integer)
    species = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    maturity = Column(String(50, 'Latin1_General_CI_AS'))
    gutted = Column(BIT, nullable=False, server_default=text("((0))"))
    laser_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    aruco_mean_diag_px_manual = Column(String(50, 'Latin1_General_CI_AS'))
    aruco_diag_px_auto = Column(String(50, 'Latin1_General_CI_AS'))
    sample_headerid = Column(ForeignKey('sample_header.sample_headerid'), nullable=False)
    measurer = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    cameraid = Column(ForeignKey('camera.cameraid'), nullable=False)
    housing_mountid = Column(ForeignKey('housing_mount.housing_mountid'))
    board_board_length_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    capture_resolution = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    rotated_resolution_x = Column(Integer)
    rotated_resolution_y = Column(Integer)
    useable_footage = Column(BIT, nullable=False, server_default=text("((0))"))
    comment = Column(Unicode)

    camera = relationship('Camera')
    housing_mount = relationship('HousingMount')
    sample_header = relationship('SampleHeader')


class SampleHeader(Base):
    __tablename__ = 'sample_header'

    sample_headerid = Column(Integer, primary_key=True)
    visit_date = Column(DateTime, nullable=False, server_default=text("(getdate())"))
    supplier = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    stock_source = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    stock_location = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))


class SampleLength(Base):
    __tablename__ = 'sample_length'

    sample_lengthid = Column(Integer, primary_key=True)
    sampleid = Column(ForeignKey('sample.sampleid'), nullable=False)
    estimate_mm = Column(Integer)
    ref_length_type = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    ref_length_mm = Column(Integer, nullable=False, server_default=text("((0))"))
    ref_length_px = Column(Float(53), nullable=False, server_default=text("((0))"))
    lens_subj_camprop_est = Column(Float(53))
    lens_subj_triangle_est = Column(Float(53))
    measured_resolution = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    lens_correction_mm = Column(Float(53), nullable=False, server_default=text("((0))"))
    mv_nas_lens_correction_mm = Column(Float(53))
    mv_ssd_lens_correction_mm = Column(Float(53))
    mv_res_lens_correction_mm = Column(Float(53))
    perspective_corrected_estimate_mm = Column(Float(53))
    perspective_corrected_estimate_iter_mm = Column(Float(53))
    persp_corr_iter_profile_mm = Column(Float(53))
    persp_corr_iter_profile_camdist_mm = Column(Float(53))
    persp_corr_iter_profile_tridist_mm = Column(Float(53))
    unique_code = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    species = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    comment = Column(Text(2147483647, 'Latin1_General_CI_AS'))
    w = Column(Integer)
    h = Column(Integer)
    groundtruth_xmin = Column(Float(53))
    groundtruth_xmax = Column(Float(53))
    groundtruth_ymin = Column(Float(53))
    groundtruth_ymax = Column(Float(53))
    nas_xmin = Column(Float(53))
    nas_xmax = Column(Float(53))
    nas_ymin = Column(Float(53))
    nas_ymax = Column(Float(53))
    nas_accuracy = Column(Float(53))
    nas_iou = Column(Float(53))
    nas_persp_corr_iter_profile_tridist_mm = Column(Integer)
    ssd_xmin = Column(Float(53))
    ssd_xmax = Column(Float(53))
    ssd_ymin = Column(Float(53))
    ssd_ymax = Column(Float(53))
    ssd_accuracy = Column(Float(53))
    ssd_iou = Column(Float(53))
    ssd_persp_corr_iter_profile_tridist_mm = Column(Integer)
    res_xmin = Column(Float(53))
    res_xmax = Column(Float(53))
    res_ymin = Column(Float(53))
    res_ymax = Column(Float(53))
    res_accuracy = Column(Float(53))
    res_iou = Column(Float(53))
    res_persp_corr_iter_profile_tridist_mm = Column(Integer)

    sample = relationship('Sample')


class Sysdiagram(Base):
    __tablename__ = 'sysdiagrams'
    __table_args__ = (
        Index('UK_principal_name', 'principal_id', 'name', unique=True),
    )

    name = Column(Unicode(128), nullable=False)
    principal_id = Column(Integer, nullable=False)
    diagram_id = Column(Integer, primary_key=True)
    version = Column(Integer)
    definition = Column(LargeBinary)


t_v_lengths = Table(
    'v_lengths', metadata,
    Column('sampleid', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('lens_subject_distance', Integer),
    Column('laser_sans_corr', Integer),
    Column('bg_sans_corr', Integer),
    Column('fg_sans_corr', Integer),
    Column('laser_lens_corr', Integer),
    Column('bg_lens_corr', Integer),
    Column('fg_lens_corr', Integer),
    Column('laser_all_cor_estimate_depth', Integer),
    Column('fg_all_cor_estimate_depth', Integer),
    Column('laser_all_corr_estimate_iter', Integer),
    Column('fg_all_corr_estimate_iter', Integer)
)


t_v_lengths_bass = Table(
    'v_lengths_bass', metadata,
    Column('sampleid', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('lens_subject_distance', Integer),
    Column('laser_sans_corr', Integer),
    Column('bg_sans_corr', Integer),
    Column('fg_sans_corr', Integer),
    Column('laser_lens_corr', Float(53)),
    Column('bg_lens_corr', Float(53)),
    Column('fg_lens_corr', Float(53)),
    Column('laser_all_cor_estimate_depth', Float(53)),
    Column('fg_all_cor_estimate_depth', Float(53)),
    Column('laser_perspective_corrected_estimate_iter_mm', Float(53)),
    Column('fg_perspective_corrected_estimate_iter_mm', Float(53)),
    Column('laser_persp_corr_iter_profile_mm', Float(53)),
    Column('fg_persp_corr_iter_profile_mm', Float(53)),
    Column('laser_persp_corr_iter_profile_camdist_mm', Float(53)),
    Column('fg_persp_corr_iter_profile_camdist_mm', Float(53)),
    Column('laser_persp_corr_iter_profile_tridist_mm', Float(53)),
    Column('fg_persp_corr_iter_profile_tridist_mm', Float(53))
)


t_v_lengths_dab = Table(
    'v_lengths_dab', metadata,
    Column('sampleid', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('lens_subject_distance', Integer),
    Column('laser_sans_corr', Integer),
    Column('bg_sans_corr', Integer),
    Column('fg_sans_corr', Integer),
    Column('laser_lens_corr', Float(53)),
    Column('bg_lens_corr', Float(53)),
    Column('fg_lens_corr', Float(53)),
    Column('laser_all_cor_estimate_depth', Float(53)),
    Column('fg_all_cor_estimate_depth', Float(53)),
    Column('laser_perspective_corrected_estimate_iter_mm', Float(53)),
    Column('fg_perspective_corrected_estimate_iter_mm', Float(53)),
    Column('laser_persp_corr_iter_profile_mm', Float(53)),
    Column('fg_persp_corr_iter_profile_mm', Float(53)),
    Column('laser_persp_corr_iter_profile_camdist_mm', Float(53)),
    Column('fg_persp_corr_iter_profile_camdist_mm', Float(53)),
    Column('laser_persp_corr_iter_profile_tridist_mm', Float(53)),
    Column('fg_persp_corr_iter_profile_tridist_mm', Float(53))
)
