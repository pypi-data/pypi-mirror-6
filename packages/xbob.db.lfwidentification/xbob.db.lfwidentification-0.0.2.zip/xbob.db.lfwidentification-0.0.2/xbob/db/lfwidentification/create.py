#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
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

"""This script creates the LFW Identification database in a single pass.
"""

import os

from .models import *

def nodot(item):
  """Can be used to ignore hidden files, starting with the . character."""
  return item[0] != '.'

def add_clients(session, basedir, verbose):
  """Add clients to the LFW Identification database."""

  def parse_input(input_file):

    # Open input file
    f = open(input_file)
    client_dict = {}
    for line in f:
      lst = line.split()
      client_dict[lst[0]] = lst[1]
    f.close()
    return client_dict

  def split_client_dict(client_dict):
    world = {}
    development = {}
    evaluation = {}
    open_set = {}
    dev = True
    c = 0
    for k in sorted(client_dict):
      v = int(client_dict[k])
      if v > 10 or (v > 1 and c < 137):
        world[k] = v
        if v <= 10:
          c += 1
      elif v > 1:
        if c < 537:
          development[k] = v
          c += 1
        else:
          evaluation[k] = v
      else:
        open_set[k] = v
    return (world, development, evaluation, open_set)

  input_file = os.path.join(basedir, 'lfw-names.txt')
  client_dict = parse_input(input_file)
  (dworld, ddev, deval, _) = split_client_dict(client_dict)

  if verbose: print("Adding clients...")
  groups = ['world', 'dev', 'eval']
  lists  = [dworld, ddev, deval]
  for k in range(len(groups)):
    g_cur = groups[k]
    l_cur = lists[k]
    for el in l_cur:
      if verbose>1: print("  Adding client '%s' in group '%s' ('%d' samples)..." %(el, g_cur, l_cur[el]))
      session.add(Client(el, g_cur))

def add_files(session, basedir, verbose):
  """Add files to the LFW Identification database."""

  def add_file(session, file_name):
    """Parses a single filename and add it to the list."""
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    shot_id = base_name.split('_')[-1]
    client_id = base_name[0:-len(shot_id)-1]
    f = File(client_id, shot_id)
    session.add(f)

  # Loops over the directory structure
  if verbose: print("Adding files ...")
  imagedir = os.path.join(basedir, 'all_images')
  for client_dir in filter(nodot, sorted([d for d in os.listdir(imagedir)])):
    for filename in filter(nodot, sorted([d for d in os.listdir(os.path.join(imagedir, client_dir))])):
      if filename.endswith('.jpg'):
        # adds a file to the database
        if verbose>1: print("    Adding file '%s'" % filename)
        add_file(session, filename)

def add_protocols(session, verbose):
  """Adds protocols"""

  protocol_names = [('P0',False),('P0set',True)]
  protocolPurpose_list = [('world', 'train'), ('dev', 'enrol'), ('dev', 'probe'), ('eval', 'enrol'), ('eval', 'probe')]
  for proto,fileset in protocol_names:
    p = Protocol(proto,fileset)
    # Add protocol
    if verbose: print("Adding protocol %s..." % (proto))
    session.add(p)
    session.flush()
    session.refresh(p)

    # Add protocol purposes
    for key in range(len(protocolPurpose_list)):
      purpose = protocolPurpose_list[key]
      pu = ProtocolPurpose(p.id, purpose[0], purpose[1])
      if verbose>1: print("  Adding protocol purpose ('%s','%s')..." % (purpose[0], purpose[1]))
      session.add(pu)
      session.flush()
      session.refresh(pu)

       # Add files attached with this protocol purpose
      client_group = ""
      if(key == 0): client_group = "world"
      elif(key == 1 or key == 2): client_group = "dev"
      elif(key == 3 or key == 4): client_group = "eval"

      # Adds 'protocol' files
      q = session.query(File).join(Client).filter(Client.sgroup == client_group)
      if purpose[1] == 'enrol':
        q = q.filter(File.shot_id == 1)
      elif purpose[1] == 'probe':
        q = q.filter(File.shot_id != 1)
      q = q.order_by(File.id)
      for k in q:
        if verbose>1: print("    Adding protocol file '%s'..." % (k.path))
        pu.files.append(k)

      # Adds Fileset's if required
      if fileset and purpose[1] == 'probe':
        q = session.query(Client).filter(Client.sgroup == client_group)
        for cl in q:
          qf = session.query(File).join(Client).filter(Client.id == cl.id).filter(File.shot_id != 1)
          nprobes = qf.count()
          ids = sorted([k.shot_id for k in qf])
          set_name = "%s/%s" % (cl.id, cl.id)
          for i in ids: 
            set_name = "%s_%04d" % (set_name, i)
          set_name = "%s__%04d" % (set_name, len(ids))
          fs = Fileset(set_name, cl.id)
          if verbose>1: print("    Adding file set '%s'..." % (set_name))
          pu.filesets.append(fs)
          if verbose>1: print("    Adding file set '%s' to the current protocol..." % (set_name))
          session.add(fs)
          session.flush()
          session.refresh(fs)
          for k in qf:
            if verbose>1: print("      Adding file '%s' to file set ..." % (k.path))
            fs.files.append(k)

def create_tables(args):
  """Creates all necessary tables (only to be used at the first time)"""

  from bob.db.utils import create_engine_try_nolock

  engine = create_engine_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  Base.metadata.create_all(engine)

# Driver API
# ==========

def create(args):
  """Creates or re-creates this database"""

  from bob.db.utils import session_try_nolock

  dbfile = args.files[0]

  if args.recreate:
    if args.verbose and os.path.exists(dbfile):
      print('unlinking %s...' % dbfile)
    if os.path.exists(dbfile): os.unlink(dbfile)

  if not os.path.exists(os.path.dirname(dbfile)):
    os.makedirs(os.path.dirname(dbfile))

  # the real work...
  create_tables(args)
  s = session_try_nolock(args.type, args.files[0], echo=(args.verbose > 2))
  add_clients(s, args.basedir, args.verbose)
  add_files(s, args.basedir, args.verbose)
  add_protocols(s, args.verbose)
  s.commit()
  s.close()

def add_command(subparsers):
  """Add specific subcommands that the action "create" can use"""

  parser = subparsers.add_parser('create', help=create.__doc__)

  parser.add_argument('-R', '--recreate', action='store_true', help="If set, I'll first erase the current database")
  parser.add_argument('-v', '--verbose', action='count', help="Do SQL operations in a verbose way")
  parser.add_argument('-D', '--basedir', metavar='DIR', default='/idiap/resource/database/lfw', help='Change the relative path to the directory containing the images of the LFW Identification database.')

  parser.set_defaults(func=create) #action
