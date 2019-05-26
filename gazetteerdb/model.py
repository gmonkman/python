# coding: utf-8
from sqlalchemy import BigInteger, Column, DECIMAL, Date, DateTime, Float, ForeignKey, Integer, Numeric, SmallInteger, String, TEXT, Table, Unicode, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class LK(Base):
    __tablename__ = 'LK'

    Id = Column(Integer, primary_key=True)
    Name = Column(String(255, 'Latin1_General_CI_AS'))
    gx_media_links = Column(String(collation='Latin1_General_CI_AS'))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))
    x = Column(Float(53))
    y = Column(Float(53))


class CoastlineWgs84(Base):
    __tablename__ = 'coastline_wgs84'

    ogr_fid = Column(Integer, primary_key=True)
    code = Column(Numeric(6, 0))
    legend = Column(Unicode(42))
    amended = Column(Date)


class CountiesWgs84(Base):
    __tablename__ = 'counties_wgs84'

    ogr_fid = Column(Integer, primary_key=True)
    id_0 = Column(Numeric(9, 0))
    iso = Column(Unicode(3))
    name_0 = Column(Unicode(75))
    id_1 = Column(Numeric(9, 0))
    name_1 = Column(Unicode(75))
    id_2 = Column(Numeric(9, 0))
    name_2 = Column(Unicode(75))
    varname_2 = Column(Unicode(150))
    nl_name_2 = Column(Unicode(75))
    hasc_2 = Column(Unicode(15))
    cc_2 = Column(Unicode(15))
    type_2 = Column(Unicode(50))
    engtype_2 = Column(Unicode(50))
    validfr_2 = Column(Unicode(25))
    validto_2 = Column(Unicode(25))
    remarks_2 = Column(Unicode(100))
    shape_leng = Column(Numeric(19, 11))
    shape_area = Column(Numeric(19, 11))


class EnglandWgs84(Base):
    __tablename__ = 'england_wgs84'

    ogr_fid = Column(Integer, primary_key=True)
    id = Column(Numeric(6, 0))


class Geograph(Base):
    __tablename__ = 'geograph'

    gridimage_id = Column(Integer, primary_key=True, server_default=text("((0))"))
    user_id = Column(Integer, server_default=text("((0))"))
    realname = Column(String(128, 'Latin1_General_CI_AS'), server_default=text("(N'')"))
    title = Column(String(128, 'Latin1_General_CI_AS'))
    moderation_status = Column(String(8, 'Latin1_General_CI_AS'), server_default=text("(N'pending')"))
    imagetaken = Column(Date, server_default=text("(getdate())"))
    grid_reference = Column(String(6, 'Latin1_General_CI_AS'), server_default=text("(N'')"))
    x = Column(SmallInteger, server_default=text("((0))"))
    y = Column(SmallInteger, server_default=text("((0))"))
    wgs84_lat = Column(DECIMAL(10, 6), server_default=text("((0.000000))"))
    wgs84_long = Column(DECIMAL(10, 6), server_default=text("((0.000000))"))
    reference_index = Column(SmallInteger, server_default=text("((0))"))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))


class GnFeatureClas(Base):
    __tablename__ = 'gn_feature_class'

    gn_feature_classid = Column(String(1, 'Latin1_General_CI_AS'), primary_key=True)
    feature_class = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    eg = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))


class HighWaterWgs84(Base):
    __tablename__ = 'high_water_wgs84'

    ogr_fid = Column(Integer, primary_key=True)
    code = Column(Unicode(4))
    descriptio = Column(Unicode(21))
    file_name = Column(Unicode(50))
    number = Column(Numeric(11, 0))
    link_id = Column(Numeric(11, 0))


class IfcaAreaNoholesWgs84(Base):
    __tablename__ = 'ifca_area_noholes_wgs84'

    ogr_fid = Column(Integer, primary_key=True)
    name = Column(Unicode(50))
    shape_area = Column(Numeric(19, 11))
    shape_len = Column(Numeric(19, 11))
    et_id = Column(Numeric(9, 0))


class Medin(Base):
    __tablename__ = 'medin'

    medinid = Column(Integer, primary_key=True)
    medinid_orig = Column(Integer, nullable=False, server_default=text("((0))"))
    name = Column(String(200, 'Latin1_General_CI_AS'))
    description = Column(String(100, 'Latin1_General_CI_AS'))
    feature_type = Column(String(50, 'Latin1_General_CI_AS'))
    x = Column(Float(53), nullable=False, server_default=text("((0))"))
    y = Column(Float(53), nullable=False, server_default=text("((0))"))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))


class OsGazetteerFeatureCode(Base):
    __tablename__ = 'os_gazetteer_feature_code'

    os_gazetteer_feature_codeid = Column(String(2, 'Latin1_General_CI_AS'), primary_key=True)
    feature_type = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)


t_os_locator = Table(
    'os_locator', metadata,
    Column('feature_name', Unicode(255)),
    Column('road_classification', Unicode(255)),
    Column('x_centre_coord', Float(53)),
    Column('y_centre_coord', Float(53)),
    Column('min_x', Float(53)),
    Column('max_x', Float(53)),
    Column('min_y', Float(53)),
    Column('max_y', Float(53)),
    Column('settlement', Unicode(255)),
    Column('locality', Unicode(255)),
    Column('cou_unit', Unicode(255)),
    Column('local_authority', Unicode(255)),
    Column('ten_k_tile_ref', Unicode(255)),
    Column('twenty_five_k_tile_ref', Unicode(255)),
    Column('source', Unicode(255))
)


class OsOpenName(Base):
    __tablename__ = 'os_open_name'

    os_open_nameid = Column(BigInteger, primary_key=True)
    names_uri = Column(String(75, 'Latin1_General_CI_AS'), server_default=text("('')"))
    name1 = Column(Unicode(250), server_default=text("('')"))
    name1_lang = Column(String(3, 'Latin1_General_CI_AS'), server_default=text("('')"))
    name2 = Column(Unicode(250), server_default=text("('')"))
    name2_lang = Column(String(3, 'Latin1_General_CI_AS'), server_default=text("('')"))
    type = Column(String(30, 'Latin1_General_CI_AS'), server_default=text("('')"))
    local_type = Column(String(250, 'Latin1_General_CI_AS'), server_default=text("('')"))
    geometry_x = Column(BigInteger, server_default=text("((0))"))
    geometry_y = Column(BigInteger, server_default=text("((0))"))
    most_detail_view_res = Column(Integer, server_default=text("((0))"))
    least_detail_view_res = Column(Integer, server_default=text("((0))"))
    mbr_xmin = Column(BigInteger, server_default=text("((0))"))
    mbr_ymin = Column(BigInteger, server_default=text("((0))"))
    mbr_xmax = Column(BigInteger, server_default=text("((0))"))
    mbr_ymax = Column(BigInteger, server_default=text("((0))"))
    postcode_district = Column(String(4, 'Latin1_General_CI_AS'), server_default=text("('')"))
    postcode_district_uri = Column(String(60, 'Latin1_General_CI_AS'), server_default=text("('')"))
    populated_place = Column(Unicode(103))
    populated_place_uri = Column(String(60, 'Latin1_General_CI_AS'))
    populated_place_type = Column(String(1000, 'Latin1_General_CI_AS'))
    district_borough = Column(String(80, 'Latin1_General_CI_AS'))
    district_borough_uri = Column(String(80, 'Latin1_General_CI_AS'))
    district_borough_type = Column(String(80, 'Latin1_General_CI_AS'))
    county_unitary = Column(String(80, 'Latin1_General_CI_AS'))
    county_unitary_uri = Column(String(80, 'Latin1_General_CI_AS'))
    county_unitary_type = Column(String(80, 'Latin1_General_CI_AS'))
    region = Column(String(30, 'Latin1_General_CI_AS'))
    region_uri = Column(String(60, 'Latin1_General_CI_AS'))
    country = Column(String(30, 'Latin1_General_CI_AS'), server_default=text("('')"))
    country_uri = Column(String(60, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    related_spatial_object = Column(String(20, 'Latin1_General_CI_AS'))
    same_as_dbpedia = Column(String(100, 'Latin1_General_CI_AS'))
    same_as_geonames = Column(String(100, 'Latin1_General_CI_AS'), server_default=text("('')"))
    source_csv = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    source_row = Column(Integer, nullable=False)
    x = Column(Float(53))
    y = Column(Float(53))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))


class SpatialRefSy(Base):
    __tablename__ = 'spatial_ref_sys'

    srid = Column(Integer, primary_key=True)
    auth_name = Column(String(256, 'Latin1_General_CI_AS'))
    auth_srid = Column(Integer)
    srtext = Column(String(2048, 'Latin1_General_CI_AS'))
    proj4text = Column(String(2048, 'Latin1_General_CI_AS'))


class Town(Base):
    __tablename__ = 'town'

    townid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True)
    settlement = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    population = Column(Integer, nullable=False, server_default=text("((0))"))


class UkhoGazetteer(Base):
    __tablename__ = 'ukho_gazetteer'

    ukho_gazetteerid = Column(Integer, primary_key=True)
    name = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    description = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    ukhoid = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    medinid = Column(Integer, nullable=False)
    prelabel = Column(String(50, 'Latin1_General_CI_AS'))
    sourcename = Column(String(50, 'Latin1_General_CI_AS'))
    region_sea = Column(String(50, 'Latin1_General_CI_AS'))
    featuret_1 = Column(String(50, 'Latin1_General_CI_AS'))
    orig_fid = Column(Integer, nullable=False)
    x = Column(Float(53), nullable=False, server_default=text("((0))"))
    y = Column(Float(53), nullable=False, server_default=text("((0))"))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))


class UkhoSeacoverWgs84(Base):
    __tablename__ = 'ukho_seacover_wgs84'

    ogr_fid = Column(Integer, primary_key=True)
    objectid = Column(Numeric(9, 0))
    id = Column(Numeric(9, 0))
    feature = Column(Unicode(38))
    dsnm = Column(Unicode(12))
    objnam = Column(Unicode(254))
    inform = Column(Unicode(254))
    scamin = Column(Numeric(9, 0))
    shape_leng = Column(Numeric(19, 11))
    shape_area = Column(Numeric(19, 11))
    x = Column(Numeric(19, 11))
    y = Column(Numeric(19, 11))
    et_id = Column(Numeric(9, 0))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))


t_v_LK = Table(
    'v_LK', metadata,
    Column('id', Integer, nullable=False),
    Column('source', String(15, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', String(255, 'Latin1_General_CI_AS')),
    Column('feature_class', String(1, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(1, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53)),
    Column('y', Float(53)),
    Column('IFCA', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_geograph = Table(
    'v_geograph', metadata,
    Column('id', Integer, nullable=False),
    Column('source', String(8, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', String(128, 'Latin1_General_CI_AS')),
    Column('feature_class', String(1, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(1, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', DECIMAL(10, 6)),
    Column('y', DECIMAL(10, 6)),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_gn_feature = Table(
    'v_gn_feature', metadata,
    Column('id', Integer, nullable=False),
    Column('source', String(8, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', String(200, 'Latin1_General_CI_AS')),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(250, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53), nullable=False),
    Column('y', Float(53), nullable=False),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_gn_feature_alias = Table(
    'v_gn_feature_alias', metadata,
    Column('id', Integer, nullable=False),
    Column('source', String(8, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', Unicode(200), nullable=False),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(250, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53), nullable=False),
    Column('y', Float(53), nullable=False),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_medin = Table(
    'v_medin', metadata,
    Column('id', Integer, nullable=False),
    Column('source', String(5, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', String(200, 'Latin1_General_CI_AS')),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(100, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53), nullable=False),
    Column('y', Float(53), nullable=False),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_os_gazetteer = Table(
    'v_os_gazetteer', metadata,
    Column('id', BigInteger, nullable=False),
    Column('source', String(12, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', Unicode(255)),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(1, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53)),
    Column('y', Float(53)),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_os_open_name = Table(
    'v_os_open_name', metadata,
    Column('id', BigInteger, nullable=False),
    Column('source', String(12, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', Unicode(250)),
    Column('feature_class', String(30, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(250, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53)),
    Column('y', Float(53)),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_ukho_gazetteer = Table(
    'v_ukho_gazetteer', metadata,
    Column('id', Integer, nullable=False),
    Column('source', String(14, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53), nullable=False),
    Column('y', Float(53), nullable=False),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


t_v_ukho_seacover_wgs84 = Table(
    'v_ukho_seacover_wgs84', metadata,
    Column('id', Integer, nullable=False),
    Column('source', String(13, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', Unicode(254)),
    Column('feature_class', Unicode(38), nullable=False),
    Column('feature_class1', String(1, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Numeric(19, 11)),
    Column('y', Numeric(19, 11)),
    Column('ifca', String(50, 'Latin1_General_CI_AS')),
    Column('nn_coastline_wgs84_ogr_fid', Integer),
    Column('coast_dist_m', Float(53)),
    Column('eng_dist_m', Float(53))
)


class GnFeatureClass1(Base):
    __tablename__ = 'gn_feature_class1'

    gn_feature_class1id = Column(String(10, 'Latin1_General_CI_AS'), primary_key=True)
    gn_feature_classid = Column(ForeignKey('gn_feature_class.gn_feature_classid'), nullable=False)
    feature_class1 = Column(String(250, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    descrption = Column(String(500, 'Latin1_General_CI_AS'))

    gn_feature_clas = relationship('GnFeatureClas')


class OnsPopulationCentre(Base):
    __tablename__ = 'ons_population_centres'

    masterid = Column(Integer, primary_key=True)
    place = Column(Integer, nullable=False, server_default=text("((0))"))
    place15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    placesort = Column(String(100, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    place15nm = Column(String(100, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    splitind = Column(Integer, nullable=False, server_default=text("((0))"))
    popcnt = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    descnm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    county = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    authority = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    country = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    unknownref = Column(String(50, 'Latin1_General_CI_AS'), nullable=False)
    cty15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    lad15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    lad15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    laddescnm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    wd15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    par15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    hlth12cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    hlth12nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    regd15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    regd15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    rgn15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    rgn15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    npark15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    npark15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    townid = Column(ForeignKey('town.townid'), nullable=False, server_default=text("('')"))
    pcon15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    pcon15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    eer15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    eer15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    pfa15cd = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    pfa15nm = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    gridgb1m = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    gridgb1e = Column(Integer, nullable=False, server_default=text("((0))"))
    gridgb1n = Column(Integer, nullable=False, server_default=text("((0))"))
    grid1km = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    lat = Column(Float(53), nullable=False, server_default=text("((0))"))
    long = Column(Float(53), nullable=False, server_default=text("((0))"))

    town = relationship('Town')


class OsGazetteer(Base):
    __tablename__ = 'os_gazetteer'

    os_gazetteerid = Column(BigInteger, primary_key=True)
    km_ref = Column(Unicode(255))
    def_nam = Column(Unicode(255))
    tile_ref = Column(Unicode(255))
    lat_deg = Column(Float(53))
    lat_min = Column(Float(53))
    y = Column(Float(53))
    long_deg = Column(Float(53))
    long_min = Column(Float(53))
    x = Column(Float(53))
    Column1 = Column(Unicode(255))
    north = Column(Float(53))
    east = Column(Float(53))
    gmt = Column(Unicode(255))
    co_code = Column(Unicode(255))
    county = Column(Unicode(255))
    full_county = Column(Unicode(255))
    os_gazetteer_feature_codeid = Column(ForeignKey('os_gazetteer_feature_code.os_gazetteer_feature_codeid'))
    e_date = Column(DateTime)
    update_co = Column(Unicode(255))
    sheet_1 = Column(Float(53))
    sheet_2 = Column(Float(53))
    sheet_3 = Column(Float(53))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))

    os_gazetteer_feature_code = relationship('OsGazetteerFeatureCode')


class GnFeature(Base):
    __tablename__ = 'gn_feature'

    gn_featureid = Column(Integer, primary_key=True)
    name = Column(String(200, 'Latin1_General_CI_AS'))
    asciiname = Column(String(200, 'Latin1_General_CI_AS'))
    alternatenames = Column(TEXT(2147483647, 'Latin1_General_CI_AS'))
    latitude = Column(Float(53), nullable=False, server_default=text("((0))"))
    longitude = Column(Float(53), nullable=False, server_default=text("((0))"))
    gn_feature_classid = Column(ForeignKey('gn_feature_class.gn_feature_classid'))
    gn_feature_class1id = Column(ForeignKey('gn_feature_class1.gn_feature_class1id'))
    admin1_code = Column(String(20, 'Latin1_General_CI_AS'))
    admin2_code = Column(String(80, 'Latin1_General_CI_AS'))
    admin3_code = Column(String(20, 'Latin1_General_CI_AS'))
    admin4_code = Column(String(20, 'Latin1_General_CI_AS'))
    population = Column(Integer, nullable=False, server_default=text("((0))"))
    elevation = Column(Integer)
    dem = Column(Integer, nullable=False, server_default=text("((0))"))
    alias = Column(Unicode(4000))
    IFCA = Column(String(50, 'Latin1_General_CI_AS'))
    coast_dist_m = Column(Float(53))
    nn_coastline_wgs84_ogr_fid = Column(Integer)
    eng_dist_m = Column(Float(53))

    gn_feature_class1 = relationship('GnFeatureClass1')
    gn_feature_clas = relationship('GnFeatureClas')


class GnFeatureAlia(Base):
    __tablename__ = 'gn_feature_alias'

    gn_feature_aliasid = Column(Integer, primary_key=True)
    gn_featureid = Column(ForeignKey('gn_feature.gn_featureid'), nullable=False)
    gn_feature_alias = Column(Unicode(200), nullable=False)

    gn_feature = relationship('GnFeature')
