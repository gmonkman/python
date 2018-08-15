#pylint: skip-file
# coding: utf-8
from sqlalchemy import Column, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, String, Table, Text, Unicode, text
from sqlalchemy.dialects.mssql.base import BIT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


t_LKMSPJEM = Table('LKMSPJEM', metadata,
    Column('line', String(50, 'Latin1_General_CI_AS')),
    Column('reviewer1', String(509, 'Latin1_General_CI_AS')),
    Column('reviewer2', String(626, 'Latin1_General_CI_AS')),
    Column('remedial', String(479, 'Latin1_General_CI_AS')),
    Column('response', String(509, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')")),
    Column('status', String(50, 'Latin1_General_CI_AS')))


t_Section = Table('Section', metadata,
    Column('line', String(50, 'Latin1_General_CI_AS')),
    Column('reviewer1', String(960, 'Latin1_General_CI_AS')),
    Column('reviewer2', String(294, 'Latin1_General_CI_AS')),
    Column('reviewer3', String(591, 'Latin1_General_CI_AS')),
    Column('remedial', String(2860, 'Latin1_General_CI_AS')),
    Column('response', String(2470, 'Latin1_General_CI_AS')),
    Column('status', String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')")))


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


class Combined(Base):
    __tablename__ = 'combined'

    combinedid = Column(Integer, primary_key=True)
    sample_lengthid = Column(ForeignKey('sample_length.sample_lengthid'), nullable=False)
    imgname = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    w = Column(Integer, nullable=False, server_default=text("((0))"))
    h = Column(Integer, nullable=False, server_default=text("((0))"))
    groundtruth_xmin = Column(Float(53))
    groundtruth_xmax = Column(Float(53))
    groundtruth_ymin = Column(Float(53))
    groundtruth_ymax = Column(Float(53))
    xmin = Column(Float(53))
    xmax = Column(Float(53))
    ymin = Column(Float(53))
    ymax = Column(Float(53))
    score = Column(Float(53), nullable=False, server_default=text("((0))"))
    length_est = Column(Float(53))
    length_est_rotation_adjust1 = Column(Float(53))
    length_est_rotation_adjust2 = Column(Float(53))
    network = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    platform = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    camera = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    transform = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    rotation = Column(Integer, nullable=False, server_default=text("((0))"))
    scale = Column(Float(53))
    status = Column(String(50, 'Latin1_General_CI_AS'))
    sampleid = Column(ForeignKey('sample.sampleid'))
    species = Column(Unicode(10))
    hflip = Column(BIT, server_default=text("((0))"))

    sample_length = relationship('SampleLength')
    sample = relationship('Sample')


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
    status = Column(Unicode(100))
    transform = Column(Unicode(20), server_default=text("('None')"))
    rotation = Column(Integer, server_default=text("((0))"))
    scale = Column(Float(53), server_default=text("((1))"))
    date_added = Column(DateTime, server_default=text("(getdate())"))
    nas_length_est_rotation_adjust1 = Column(Float(53))
    ssd_length_est_rotation_adjust1 = Column(Float(53))
    res_length_est_rotation_adjust1 = Column(Float(53))
    nas_length_est_rotation_adjust2 = Column(Float(53))
    ssd_length_est_rotation_adjust2 = Column(Float(53))
    res_length_est_rotation_adjust2 = Column(Float(53))
    hflip = Column(BIT, server_default=text("((0))"))
    nas_status = Column(Unicode(50))
    res_status = Column(Unicode(50))
    ssd_status = Column(Unicode(50))
    nas_all_corr_rot_adj2_mm = Column(Float(53))
    nas_all_corr_rot_adj1_mm = Column(Float(53))
    res_all_corr_rot_adj2_mm = Column(Float(53))
    res_all_corr_rot_adj1_mm = Column(Float(53))
    ssd_all_corr_rot_adj2_mm = Column(Float(53))
    ssd_all_corr_rot_adj1_mm = Column(Float(53))

    sample = relationship('Sample')


class Sysdiagram(Base):
    __tablename__ = 'sysdiagrams'
    __table_args__ = (Index('UK_principal_name', 'principal_id', 'name', unique=True),)

    name = Column(Unicode(128), nullable=False)
    principal_id = Column(Integer, nullable=False)
    diagram_id = Column(Integer, primary_key=True)
    version = Column(Integer)
    definition = Column(LargeBinary)


class Transform(Base):
    __tablename__ = 'transform'

    transform = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    rotation = Column(Integer, nullable=False)
    scale = Column(Float(53), nullable=False)
    hflip = Column(BIT, nullable=False)


t_v_fid_long_form_all = Table('v_fid_long_form_all', metadata,
    Column('Species', String(4, 'Latin1_General_CI_AS'), nullable=False),
    Column('sampleid', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('Marker', String(11, 'Latin1_General_CI_AS'), nullable=False),
    Column('Correction', String(14, 'Latin1_General_CI_AS'), nullable=False),
    Column('Correction_Order', String(9, 'Latin1_General_CI_AS'), nullable=False),
    Column('Actual length', Integer, nullable=False),
    Column('Length estimate', Float(53)),
    Column('Error', Float(53)),
    Column('Percent Error', Float(53)),
    Column('lens_subject_distance', Integer))


t_v_fid_long_form_bass = Table('v_fid_long_form_bass', metadata,
    Column('sampleid', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('marker_type', String(5, 'Latin1_General_CI_AS'), nullable=False),
    Column('correction', String(79, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('length_estimate', Float(53)),
    Column('length_estimate_error', Float(53)),
    Column('lens_subject_distance', Integer))


t_v_fid_long_form_dab = Table('v_fid_long_form_dab', metadata,
    Column('sampleid', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('marker_type', String(5, 'Latin1_General_CI_AS'), nullable=False),
    Column('correction', String(79, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('length_estimate', Float(53)),
    Column('length_estimate_error', Float(53)),
    Column('lens_subject_distance', Integer))


t_v_fid_stats = Table('v_fid_stats', metadata,
    Column('species', String(4, 'Latin1_General_CI_AS'), nullable=False),
    Column('marker_type', String(5, 'Latin1_General_CI_AS'), nullable=False),
    Column('correction', String(79, 'Latin1_General_CI_AS'), nullable=False),
    Column('nr', Integer),
    Column('avg_err', Float(53)),
    Column('std_err', Float(53)),
    Column('avg_percent_err', Float(53)),
    Column('std_percent_err', Float(53)),
    Column('min_err', Float(53)),
    Column('max_err', Float(53)))


t_v_fid_stats_agg = Table('v_fid_stats_agg', metadata,
    Column('marker_type', String(5, 'Latin1_General_CI_AS'), nullable=False),
    Column('correction', String(79, 'Latin1_General_CI_AS'), nullable=False),
    Column('nr', Integer),
    Column('avg_percent_err', Float(53)),
    Column('std_percent_err', Float(53)),
    Column('min_err', Float(53)),
    Column('max_err', Float(53)))


t_v_lengths = Table('v_lengths', metadata,
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
    Column('laser_all_corr_estimate_iter', Float(53)),
    Column('fg_all_corr_estimate_iter', Float(53)))


t_v_lengths_bass = Table('v_lengths_bass', metadata,
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
    Column('fg_persp_corr_iter_profile_tridist_mm', Float(53)))


t_v_lengths_dab = Table('v_lengths_dab', metadata,
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
    Column('fg_persp_corr_iter_profile_tridist_mm', Float(53)))


t_v_mv_detections = Table('v_mv_detections', metadata,
    Column('Platform', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('Camera', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('sampleid', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('species', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('lens_correction_mm', Float(53), nullable=False),
    Column('mv_nas_lens_correction_mm', Float(53)),
    Column('mv_ssd_lens_correction_mm', Float(53)),
    Column('mv_res_lens_correction_mm', Float(53)),
    Column('persp_corr_iter_profile_tridist_mm', Float(53)),
    Column('nas_iou', Float(53)),
    Column('nas_persp_corr_iter_profile_tridist_mm', Integer),
    Column('ssd_iou', Float(53)),
    Column('ssd_persp_corr_iter_profile_tridist_mm', Integer),
    Column('res_iou', Float(53)),
    Column('res_persp_corr_iter_profile_tridist_mm', Integer))


t_v_mv_detections_long_form = Table('v_mv_detections_long_form', metadata,
    Column('CNN', String(3, 'Latin1_General_CI_AS'), nullable=False),
    Column('Platform', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('Camera', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('iou', Float(53)))


t_v_mv_long_form = Table('v_mv_long_form', metadata,
    Column('sample_lengthid', Integer, nullable=False),
    Column('supplier', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('camera', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('species', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('cnn', String(3, 'Latin1_General_CI_AS'), nullable=False),
    Column('persp_corr_iter_profile_camdist_mm', Float(53)),
    Column('persp_corr_iter_profile_tridist_mm', Float(53)),
    Column('mv_lens_correction_mm', Float(53)),
    Column('iou', Float(53)),
    Column('mv_persp_corr_iter_profile_tridist_mm', Integer))


t_v_mv_long_form_errors = Table('v_mv_long_form_errors', metadata,
    Column('cnn', String(3, 'Latin1_General_CI_AS'), nullable=False),
    Column('supplier', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('camera', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('species', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('unique_code', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('tl_mm', Integer, nullable=False),
    Column('persp_corr_iter_profile_tridist_mm', Float(53)),
    Column('mv_persp_corr_iter_profile_tridist_mm', Integer),
    Column('manual_tridist_err', Float(53)),
    Column('mv_tridist_err', Float(53)),
    Column('pct_manual_tridist_err', Float(53)),
    Column('pct_mv_tridist_err', Float(53)))
