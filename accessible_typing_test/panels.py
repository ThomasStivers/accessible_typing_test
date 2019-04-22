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

"""Includes the ResultsPanel, TestsPanel, and UserPanel classes."""

import wx
from accessible_typing_test.results_database import session_scope, Sentences, Results


class ResultsPanel(wx.Panel):
	"""Displays a list of results of a series of typing tests."""

	def __init__(self, parent: wx.Notebook, config: wx.Config = None) -> None:
		"""Initialize the ResultsPanel.

		Args:
			parent: The wx.Notebook that contains this panel.
			config: A wx.Config object containing application configuration.
		"""

		super().__init__(parent, name="resultsPanel")
		self._config = config
		# Now define the list control.
		self.test_list = wx.ListCtrl(
			self,
			id=wx.ID_ANY,
			name="Tests",
			style=wx.LC_REPORT
			)
		self.test_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
		self.fillTestList()
		self.__do_layout()

	def __do_layout(self) -> None:
		"""Lays out the controls on the ResultsPanel."""
		sizer = wx.BoxSizer(wx.VERTICAL)
		# autofit the column widths now that we have list items.
		for col in range(self.test_list.GetColumnCount()):
			self.test_list.SetColumnWidth(col, wx.LIST_AUTOSIZE_USEHEADER)
		self.test_list.Layout()

		sizer.Add(
			wx.StaticText(self, id=wx.ID_ANY, label="Test Results"),
			flag=wx.ALIGN_CENTER_HORIZONTAL
			)
		sizer.Add(self.test_list)
		self.SetSizer(sizer)
		sizer.Fit(self)
		self.Layout()
		self.Center()


	def fillTestList(self):
		"""Populate the test_list with results from the database."""
		test_list = self.test_list
		test_list.ClearAll()
		test_list.InsertColumn(0, "Accuracy")
		test_list.InsertColumn(1, "Speed")
		test_list.InsertColumn(2, "Duration")
		test_list.InsertColumn(3, "Words")
		test_list.InsertColumn(4, "User")
		test_list.InsertColumn(5, "Timestamp")
		index = test_list.GetItemCount()
		with session_scope() as session:
			for results in session.query(Results):
				test_list.InsertItem(index, f"{results.accuracy}%")
				test_list.SetItem(index, 1, f"{results.speed} WPM")
				test_list.SetItem(index, 2, f"{results.duration} seconds")
				test_list.SetItem(index, 3, f"{results.words}")
				test_list.SetItem(index, 4, f"{results.user_name}")
				test_list.SetItem(index, 5, str(results.timestamp))
				test_list.SetItemData(index, results.id)
				index += 1

	def onItemActivated(self, event:wx.ListEvent) -> None:
		"""Handles clicks on the test results list."""
		index = event.GetIndex()
		id = event.GetData()
		with session_scope() as session:
			for result in session.query(Results).filter(Results.id == id):
				SingleResultDialog(self, result).ShowModal()


class TestsPanel(wx.Panel):
	"""Displays the test sentences and adds or removes them."""

	def __init__(self, parent: wx.Window) -> None:
		"""Initialize the dialog for reviewing sentences to be typed in tests."""

		super().__init__(parent, name="testsPanel")
		sizer = wx.BoxSizer(wx.VERTICAL)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		sentence_list = wx.ListCtrl(
			self,
			id=wx.ID_ANY,
			name="sentence_list",
			style=wx.LC_LIST
			)
		with session_scope() as session:
			for sentence in session.query(Sentences):
				sentence_list.InsertItem(0, sentence.sentence)
		sizer.Add(sentence_list, proportion=10, flag=wx.EXPAND)
		self.sentence_list = sentence_list
		add_button = wx.Button(self, id=wx.ID_ANY, label="&Add")
		self.Bind(wx.EVT_BUTTON, self.onAddSentence, add_button)
		button_sizer.Add(add_button)
		remove_button = wx.Button(self, id=wx.ID_ANY, label="&Remove")
		self.Bind(wx.EVT_BUTTON, self.onRemoveSentence, remove_button)
		button_sizer.Add(remove_button)
		sizer.Add(button_sizer, proportion=1)
		self.SetSizerAndFit(sizer)

	def onAddSentence(self, event: wx.CommandEvent = None)-> bool:
		"""Adds a sentence to the wx.ListCtrl on the TestsPanel."""
		with session_scope() as session:
			query = session.query(Sentences)
			dlg = wx.TextEntryDialog(self, message="Type the sentence to add.", caption="ADD Sentence")
			if dlg.ShowModal() == wx.ID_OK:
				sentence = dlg.GetValue()
			else:
				return False
			for duplicate in query.filter(Sentences.sentence == sentence):
				return False
			record = Sentences(sentence=sentence)
			session.add(record)
		return True

	def onRemoveSentence(self, event: wx.CommandEvent = None) -> bool:
		"""Removes a sentence from the wx.ListCtrl on the TestsPanel."""
		with session_scope() as session:
			query = session.query(Sentences)
			sentence_list = self.sentence_list
			sentence = sentence_list.GetItem(sentence_list.GetFirstSelected()).GetText()
			for found_record in query.filter(Sentences.sentence == sentence):
				record = found_record
			session.delete(record)


class UsersPanel(wx.Panel):
	"""Allows for viewing of user specific statistics."""

	def __init__(self, parent:wx.Notebook) -> None:
		"""Initialize the panel with a list of users and a statistics button."""
		super().__init__(parent=parent)
