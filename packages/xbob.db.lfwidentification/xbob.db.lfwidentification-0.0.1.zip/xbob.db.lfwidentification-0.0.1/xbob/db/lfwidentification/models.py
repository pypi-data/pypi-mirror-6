#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <laurent.el-shafey@idiap.ch>
#
# Copyright (C) 2013-2014 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Table models and functionality for the LFW Identification database.
"""

import os, numpy
import bob.db.utils
from sqlalchemy import Table, Column, Integer, String, Boolean, ForeignKey, or_, and_, not_
from bob.db.sqlalchemy_migration import Enum, relationship
from sqlalchemy.orm import backref
from sqlalchemy.ext.declarative import declarative_base

import xbob.db.verification.utils

Base = declarative_base()

protocolPurpose_file_association = Table('protocolPurpose_file_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('file_id',  String(100), ForeignKey('file.id')))

protocolPurpose_fileset_association = Table('protocolPurpose_fileset_association', Base.metadata,
  Column('protocolPurpose_id', Integer, ForeignKey('protocolPurpose.id')),
  Column('fileset_id',  Integer, ForeignKey('fileset.id')))

fileset_file_association = Table('fileset_file_association', Base.metadata,
  Column('fileset_id', Integer, ForeignKey('fileset.id')),
  Column('file_id',  String(100), ForeignKey('file.id')))

class Client(Base):
  """Database clients, marked by an integer identifier and the group they belong to"""

  __tablename__ = 'client'

  # Key identifier for the client
  id = Column(String(100), primary_key=True)
  # Group to which the client belongs to
  group_choices = ('dev','eval','world')
  sgroup = Column(Enum(*group_choices)) # do NOT use group (SQL keyword)

  def __init__(self, name, group):
    self.id = name
    self.sgroup = group

  def __repr__(self):
    return "Client(%s, '%s')" % (self.id, self.sgroup)

class File(Base, xbob.db.verification.utils.File):
  """Information about the files of the LFW Identification database"""

  __tablename__ = 'file'

  # Unique key identifier for the file; here we use strings
  id = Column(String(100), primary_key=True)
  # Identifier of the client associated with this file
  client_id = Column(String(100), ForeignKey('client.id'))
  # Unique path to this file inside the database
  path = Column(String(100), unique=True)
  # Identifier for the current image number of the client
  shot_id = Column(Integer)

  # a back-reference from file to client
  client = relationship("Client", backref=backref("files", order_by=id))

  def __init__(self, client_id, shot_id):
    # call base class constructor
    file_id = client_id + "_" + "0"*(4-len(str(shot_id))) + str(shot_id)
    xbob.db.verification.utils.File.__init__(self, client_id = client_id, file_id = file_id, path = os.path.join(client_id, file_id))

    self.shot_id = shot_id

class Fileset(Base):
  """Information about the file sets of the LFW Identification database"""
  
  __tablename__ = 'fileset'

  # Unique key identifier for the file; here we use integers
  id = Column(Integer, primary_key=True)
  # Unique 'path' for this fileset; here we use strings
  path = Column(String(200), unique=True)
  # Identifier of the client associated with this file
  client_id = Column(String(100), ForeignKey('client.id'))

  # a back-reference from file to client
  client = relationship("Client", backref=backref("filesets", order_by=id))
  # For Python: A direct link to the File objects associated with this Fileset 
  files = relationship("File", secondary=fileset_file_association, backref=backref("filesets", order_by=id))

  def __init__(self, path, client_id):
    # call base class constructor
    self.path = path
    self.client_id = client_id

  def __lt__(self, other):
    return self.client_id < other.client_id or (self.client_id == other.client_id and self.path < other.path)

  def __eq__(self, other):
    return self.id == other.id

  def __repr__(self):
    return "Fileset('%s')" % self.path

class Protocol(Base):
  """LFW Identification protocols"""

  __tablename__ = 'protocol'

  # Unique identifier for this protocol object
  id = Column(Integer, primary_key=True)
  # Name of the protocol associated with this object
  name = Column(String(20), unique=True)
  # Tells whether several probe files are used to generate a single score
  # or not
  fileset = Column(Boolean)

  def __init__(self, name, fileset):
    self.name = name
    self.fileset = fileset

  def __repr__(self):
    return "Protocol('%s')" % self.name

class ProtocolPurpose(Base):
  """LFW Identification protocol purposes"""

  __tablename__ = 'protocolPurpose'

  # Unique identifier for this protocol purpose object
  id = Column(Integer, primary_key=True)
  # Id of the protocol associated with this protocol purpose object
  protocol_id = Column(Integer, ForeignKey('protocol.id')) # for SQL
  # Group associated with this protocol purpose object
  group_choices = ('world', 'dev', 'eval')
  sgroup = Column(Enum(*group_choices))
  # Purpose associated with this protocol purpose object
  purpose_choices = ('train', 'enrol', 'probe')
  purpose = Column(Enum(*purpose_choices))

  # For Python: A direct link to the Protocol object that this ProtocolPurpose belongs to
  protocol = relationship("Protocol", backref=backref("purposes", order_by=id))
  # For Python: A direct link to the File objects associated with this ProtocolPurpose
  files = relationship("File", secondary=protocolPurpose_file_association, backref=backref("protocolPurposes", order_by=id))
  # For Python: A direct link to the Fileset objects associated with this ProtocolPurpose
  filesets = relationship("Fileset", secondary=protocolPurpose_fileset_association, backref=backref("protocolPurposes", order_by=id))

  def __init__(self, protocol_id, sgroup, purpose):
    self.protocol_id = protocol_id
    self.sgroup = sgroup
    self.purpose = purpose

  def __repr__(self):
    return "ProtocolPurpose('%s', '%s', '%s')" % (self.protocol.name, self.sgroup, self.purpose)

