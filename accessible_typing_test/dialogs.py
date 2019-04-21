# accessible_typing_test
# Copyright (C) 2019 Thomas Stivers

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import wx
from accessible_typing_test.results_database import session_scope, Sentences, Results


class SingleResultDialog(wx.Dialog):
	"""Display the details of a single test result."""

	def __init__(self, parent: wx.Window, result: Results) -> None:
		"""Initialize the dialog with test result details."""
		super().__init__(
			parent=parent,
			size=(450, 450),
			title=f"Test Result Details for test #{result.id}",
			)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.label = wx.StaticText(
			self,
			label="Result Details"
			)
		self.text = wx.TextCtrl(
			self,
			id=wx.ID_ANY,
			name="testResult",
			style=wx.TE_READONLY | wx.TE_MULTILINE,
			value=str(result)
			)
		sizer.Add(self.label)
		sizer.Add(self.text, flag=wx.EXPAND)
		self.SetSizer(sizer)
		self.Center()
		self.text.SetFocus()
