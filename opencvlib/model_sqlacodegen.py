# coding: utf-8
from sqlalchemy import Column, Date, DateTime, Float, Index, Integer, LargeBinary, Table, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class AlbumRoot(Base):
    __tablename__ = 'AlbumRoots'
    __table_args__ = (
        UniqueConstraint('identifier', 'specificPath'),
    )

    id = Column(Integer, primary_key=True)
    label = Column(Text)
    status = Column(Integer, nullable=False)
    type = Column(Integer, nullable=False)
    identifier = Column(Text)
    specificPath = Column(Text)


class Album(Base):
    __tablename__ = 'Albums'
    __table_args__ = (
        UniqueConstraint('albumRoot', 'relativePath'),
    )

    id = Column(Integer, primary_key=True)
    albumRoot = Column(Integer, nullable=False)
    relativePath = Column(Text, nullable=False)
    date = Column(Date)
    caption = Column(Text)
    collection = Column(Text)
    icon = Column(Integer)


class DownloadHistory(Base):
    __tablename__ = 'DownloadHistory'
    __table_args__ = (
        UniqueConstraint('identifier', 'filename', 'filesize', 'filedate'),
    )

    id = Column(Integer, primary_key=True)
    identifier = Column(Text)
    filename = Column(Text)
    filesize = Column(Integer)
    filedate = Column(DateTime)


class ImageComment(Base):
    __tablename__ = 'ImageComments'
    __table_args__ = (
        UniqueConstraint('imageid', 'type', 'language', 'author'),
    )

    id = Column(Integer, primary_key=True)
    imageid = Column(Integer, index=True)
    type = Column(Integer)
    language = Column(Text)
    author = Column(Text)
    date = Column(DateTime)
    comment = Column(Text)


class ImageCopyright(Base):
    __tablename__ = 'ImageCopyright'
    __table_args__ = (
        UniqueConstraint('imageid', 'property', 'value', 'extraValue'),
    )

    id = Column(Integer, primary_key=True)
    imageid = Column(Integer, index=True)
    property = Column(Text)
    value = Column(Text)
    extraValue = Column(Text)


class ImageHaarMatrix(Base):
    __tablename__ = 'ImageHaarMatrix'

    imageid = Column(Integer, primary_key=True)
    modificationDate = Column(DateTime)
    uniqueHash = Column(Text)
    matrix = Column(LargeBinary)


class ImageHistory(Base):
    __tablename__ = 'ImageHistory'

    imageid = Column(Integer, primary_key=True)
    uuid = Column(Text, index=True)
    history = Column(Text)


class ImageInformation(Base):
    __tablename__ = 'ImageInformation'

    imageid = Column(Integer, primary_key=True)
    rating = Column(Integer)
    creationDate = Column(DateTime, index=True)
    digitizationDate = Column(DateTime)
    orientation = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    format = Column(Text)
    colorDepth = Column(Integer)
    colorModel = Column(Integer)


class ImageMetadatum(Base):
    __tablename__ = 'ImageMetadata'

    imageid = Column(Integer, primary_key=True)
    make = Column(Text)
    model = Column(Text)
    lens = Column(Text)
    aperture = Column(Float)
    focalLength = Column(Float)
    focalLength35 = Column(Float)
    exposureTime = Column(Float)
    exposureProgram = Column(Integer)
    exposureMode = Column(Integer)
    sensitivity = Column(Integer)
    flash = Column(Integer)
    whiteBalance = Column(Integer)
    whiteBalanceColorTemperature = Column(Integer)
    meteringMode = Column(Integer)
    subjectDistance = Column(Float)
    subjectDistanceCategory = Column(Integer)


class ImagePosition(Base):
    __tablename__ = 'ImagePositions'

    imageid = Column(Integer, primary_key=True)
    latitude = Column(Text)
    latitudeNumber = Column(Float)
    longitude = Column(Text)
    longitudeNumber = Column(Float)
    altitude = Column(Float)
    orientation = Column(Float)
    tilt = Column(Float)
    roll = Column(Float)
    accuracy = Column(Float)
    description = Column(Text)


t_ImageProperties = Table(
    'ImageProperties', metadata,
    Column('imageid', Integer, nullable=False),
    Column('property', Text, nullable=False),
    Column('value', Text, nullable=False),
    UniqueConstraint('imageid', 'property')
)


t_ImageRelations = Table(
    'ImageRelations', metadata,
    Column('subject', Integer, index=True),
    Column('object', Integer, index=True),
    Column('type', Integer),
    UniqueConstraint('subject', 'object', 'type')
)


t_ImageTagProperties = Table(
    'ImageTagProperties', metadata,
    Column('imageid', Integer, index=True),
    Column('tagid', Integer, index=True),
    Column('property', Text),
    Column('value', Text),
    Index('imagetagproperties_index', 'imageid', 'tagid')
)


t_ImageTags = Table(
    'ImageTags', metadata,
    Column('imageid', Integer, nullable=False, index=True),
    Column('tagid', Integer, nullable=False, index=True),
    UniqueConstraint('imageid', 'tagid')
)


class Image(Base):
    __tablename__ = 'Images'
    __table_args__ = (
        UniqueConstraint('album', 'name'),
    )

    id = Column(Integer, primary_key=True)
    album = Column(Integer, index=True)
    name = Column(Text, nullable=False, index=True)
    status = Column(Integer, nullable=False)
    category = Column(Integer, nullable=False)
    modificationDate = Column(DateTime)
    fileSize = Column(Integer)
    uniqueHash = Column(Text, index=True)


class Search(Base):
    __tablename__ = 'Searches'

    id = Column(Integer, primary_key=True)
    type = Column(Integer)
    name = Column(Text, nullable=False)
    query = Column(Text, nullable=False)


t_Settings = Table(
    'Settings', metadata,
    Column('keyword', Text, nullable=False, unique=True),
    Column('value', Text)
)


t_TagProperties = Table(
    'TagProperties', metadata,
    Column('tagid', Integer, index=True),
    Column('property', Text),
    Column('value', Text)
)


class Tag(Base):
    __tablename__ = 'Tags'
    __table_args__ = (
        UniqueConstraint('name', 'pid'),
    )

    id = Column(Integer, primary_key=True)
    pid = Column(Integer)
    name = Column(Text, nullable=False)
    icon = Column(Integer)
    iconkde = Column(Text)


t_TagsTree = Table(
    'TagsTree', metadata,
    Column('id', Integer, nullable=False),
    Column('pid', Integer, nullable=False),
    UniqueConstraint('id', 'pid')
)


class VideoMetadatum(Base):
    __tablename__ = 'VideoMetadata'

    imageid = Column(Integer, primary_key=True)
    aspectRatio = Column(Text)
    audioBitRate = Column(Text)
    audioChannelType = Column(Text)
    audioCompressor = Column(Text)
    duration = Column(Text)
    frameRate = Column(Text)
    exposureProgram = Column(Integer)
    videoCodec = Column(Text)


t_v_data_images = Table(
    'v_data_images', metadata,
    Column('imageid', Integer),
    Column('tagid', Integer),
    Column('identifier', Text),
    Column('specificPath', Text),
    Column('relativePath', Text),
    Column('name', Text)
)


t_v_image_paths = Table(
    'v_image_paths', metadata,
    Column('id', Integer),
    Column('identifier', Text),
    Column('specificPath', Text),
    Column('relativePath', Text),
    Column('name', Text)
)
