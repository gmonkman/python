# coding: utf-8
from sqlalchemy import BigInteger, Column, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, String, Table, Text, Unicode, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class GnFeature(Base):
    __tablename__ = 'gn_feature'

    gn_featureid = Column(Integer, primary_key=True)
    name = Column(String(200, 'Latin1_General_CI_AS'))
    asciiname = Column(String(200, 'Latin1_General_CI_AS'))
    alternatenames = Column(Text(2147483647, 'Latin1_General_CI_AS'))
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

    gn_feature_class1 = relationship('GnFeatureClass1')
    gn_feature_clas = relationship('GnFeatureClas')


class GnFeatureAlia(Base):
    __tablename__ = 'gn_feature_alias'

    gn_feature_aliasid = Column(Integer, primary_key=True)
    gn_featureid = Column(ForeignKey('gn_feature.gn_featureid'), nullable=False)
    gn_feature_alias = Column(Unicode(200), nullable=False)

    gn_feature = relationship('GnFeature')


class GnFeatureClas(Base):
    __tablename__ = 'gn_feature_class'

    gn_feature_classid = Column(String(1, 'Latin1_General_CI_AS'), primary_key=True)
    feature_class = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    eg = Column(String(50, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))


class GnFeatureClass1(Base):
    __tablename__ = 'gn_feature_class1'

    gn_feature_class1id = Column(String(10, 'Latin1_General_CI_AS'), primary_key=True)
    gn_feature_classid = Column(ForeignKey('gn_feature_class.gn_feature_classid'), nullable=False)
    feature_class1 = Column(String(250, 'Latin1_General_CI_AS'), nullable=False, server_default=text("('')"))
    descrption = Column(String(500, 'Latin1_General_CI_AS'))

    gn_feature_clas = relationship('GnFeatureClas')


class Medin(Base):
    __tablename__ = 'medin'

    medinid = Column(Integer, primary_key=True)
    medinid_orig = Column(Integer, nullable=False, server_default=text("((0))"))
    name = Column(String(200, 'Latin1_General_CI_AS'))
    description = Column(String(100, 'Latin1_General_CI_AS'))
    feature_type = Column(String(50, 'Latin1_General_CI_AS'))
    x = Column(Float(53), nullable=False, server_default=text("((0))"))
    y = Column(Float(53), nullable=False, server_default=text("((0))"))


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


t_os_gazetteer = Table(
    'os_gazetteer', metadata,
    Column('seq', Float(53)),
    Column('km_ref', Unicode(255)),
    Column('def_nam', Unicode(255)),
    Column('tile_ref', Unicode(255)),
    Column('lat_deg', Float(53)),
    Column('lat_min', Float(53)),
    Column('y', Float(53)),
    Column('long_deg', Float(53)),
    Column('long_min', Float(53)),
    Column('x', Float(53)),
    Column('Column1', Unicode(255)),
    Column('north', Float(53)),
    Column('east', Float(53)),
    Column('gmt', Unicode(255)),
    Column('co_code', Unicode(255)),
    Column('county', Unicode(255)),
    Column('full_county', Unicode(255)),
    Column('os_gazetteer_feature_codeid', ForeignKey('os_gazetteer_feature_code.os_gazetteer_feature_codeid')),
    Column('e_date', DateTime),
    Column('update_co', Unicode(255)),
    Column('sheet_1', Float(53)),
    Column('sheet_2', Float(53)),
    Column('sheet_3', Float(53))
)


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
    column_default_sort = 'os_open_namesid'
    os_open_namesid = Column(String(50, 'Latin1_General_CI_AS'), primary_key=True, index=True)
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


t_v_gn_feature = Table(
    'v_gn_feature', metadata,
    Column('source', String(8, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', String(200, 'Latin1_General_CI_AS')),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(250, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53), nullable=False),
    Column('y', Float(53), nullable=False)
)


t_v_gn_feature_alias = Table(
    'v_gn_feature_alias', metadata,
    Column('source', String(8, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', Unicode(200), nullable=False),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(250, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53), nullable=False),
    Column('y', Float(53), nullable=False)
)


t_v_medin = Table(
    'v_medin', metadata,
    Column('source', String(5, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', String(200, 'Latin1_General_CI_AS')),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(100, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53), nullable=False),
    Column('y', Float(53), nullable=False)
)


t_v_os_gazetteer = Table(
    'v_os_gazetteer', metadata,
    Column('source', String(12, 'Latin1_General_CI_AS'), nullable=False),
    Column('name', Unicode(255)),
    Column('feature_class', String(50, 'Latin1_General_CI_AS'), nullable=False),
    Column('feature_class1', String(1, 'Latin1_General_CI_AS'), nullable=False),
    Column('x', Float(53)),
    Column('y', Float(53))
)
