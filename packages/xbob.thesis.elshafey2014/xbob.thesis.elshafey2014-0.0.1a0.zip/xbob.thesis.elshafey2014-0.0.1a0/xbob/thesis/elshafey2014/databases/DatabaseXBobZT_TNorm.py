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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from facereclib.databases.DatabaseXBob import DatabaseXBobZT

class DatabaseXBobZT_TNorm (DatabaseXBobZT):
  """This class can be used whenever you have a database that follows the default XBob database interface defining file lists for ZT score normalization."""

  def __init__(
      self,
      t_norm_options = {}, # Limit the z-probes
      **kwargs
  ):
    # call base class constructor, passing all the parameters to it
    DatabaseXBobZT.__init__(self, t_norm_options = t_norm_options, **kwargs)

    self.m_t_norm_options = t_norm_options


  def t_model_ids(self, group = 'dev'):
    """Returns the T-Norm model ids for the given group and the current protocol."""
    if hasattr(self.m_database, 'tmodel_ids'):
      return sorted(self.m_database.tmodel_ids(protocol = self.protocol, groups = group, **self.m_t_norm_options))
    else:
      return sorted([model.id for model in self.m_database.tmodels(protocol = self.protocol, groups = group, **self.m_t_norm_options)])


  def t_enroll_files(self, model_id, group = 'dev'):
    """Returns the list of enrollment File objects for the given T-Norm model id."""
    files = self.m_database.tobjects(protocol = self.protocol, groups = group, model_ids = (model_id,), **self.m_t_norm_options)
    return self.sort(files)

