# Copyright (c) 2012 Santosh Philip

# This file is part of eppy.

# Eppy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Eppy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with eppy.  If not, see <http://www.gnu.org/licenses/>.

"""read the table html files"""

import readhtml
fname = "../outputfiles/V_7_2/5ZoneCAVtoVAVWarmestTempFlowTable_ABUPS.html"
txt = open(fname, 'r').read()
htables = readhtml.titletable(txt)
fname = "../outputfiles/V_7_2/5ZoneCAVtoVAVWarmestTempFlowTable.html"
txt = open(fname, 'r').read()
htables = readhtml.titletable(txt)
