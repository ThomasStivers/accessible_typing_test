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

import logging
import wx
from accessible_typing_test.dialogs import *
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

	def onRemoveResult(self, event: wx.CommandEvent = None) -> bool:
		"""Removes a test result from the wx.ListCtrl on the ResultsPanel."""
		with session_scope() as session:
			query = session.query(Results)
			test_list = self.test_list
			id = test_list.GetItem(test_list.GetFirstSelected()).GetData()
			for found_record in query.filter(Results.id == id):
				record = found_record
			if wx.MessageBox(
				f"Are you sure you want to remove the result of the test taken by {record.user_name} on {record.timestamp}?",
				style=wx.YES_NO|wx.NO_DEFAULT
				) == wx.YES:
				session.delete(record)


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
			for index, sentence in enumerate(session.query(Sentences)):
				sentence_list.InsertItem(index, sentence.sentence)
				sentence_list.SetItemData(index, sentence.id)
		sizer.Add(sentence_list, proportion=10, flag=wx.EXPAND)
		self.sentence_list = sentence_list
		add_button = wx.Button(self, id=wx.ID_ANY, label="&Add")
		self.Bind(wx.EVT_BUTTON, self.onAddSentence, add_button)
		button_sizer.Add(add_button)
		edit_button = wx.Button(self, id=wx.ID_ANY, label="E&dit")
		self.Bind(wx.EVT_BUTTON, self.onEditSentence, edit_button)
		button_sizer.Add(edit_button)
		remove_button = wx.Button(self, id=wx.ID_ANY, label="&Remove")
		self.Bind(wx.EVT_BUTTON, self.onRemoveSentence, remove_button)
		button_sizer.Add(remove_button)
		search_button = wx.Button(self, id=wx.ID_ANY, label="&Search")
		self.Bind(wx.EVT_BUTTON, self.onSearchSentence, search_button)
		button_sizer.Add(search_button)
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

	def onSearchSentence(self, event: wx.CommandEvent) -> None:
		"""Filters the sentence list by a search phrase."""
		search = wx.GetTextFromUser(
			message="Search",
			caption="Search for Sentence",
			parent=self
			)
		if search == "":
			return
		with session_scope() as session:
			search_query = session.query(Sentences)
			search_column = Sentences.sentence.contains(search)
			self.sentence_list.ClearAll()
			for index, result in enumerate(search_query.filter(search_column)):
				self.sentence_list.SetItemData(
					self.sentence_list.InsertItem(index, result.sentence),
					result.id
					)

	def onEditSentence(self, event: wx.CommandEvent) -> None:
		"""Edit the selected sentence without changing its id."""
		sentence_list = self.sentence_list
		id = sentence_list.GetItemData(sentence_list.GetFirstSelected())
		sentence = sentence_list.GetItemText(sentence_list.GetFirstSelected())
		new_sentence = wx.GetTextFromUser(
			message="New sentence",
			caption="Edit Sentence",
			default_value=sentence,
			parent=self
			)
		if new_sentence == "":
			return
		with session_scope() as session:
			record = session.query(Sentences).filter(Sentences.id == id).one()
			if record.sentence != new_sentence:
				record.sentence = new_sentence
				sentence_list.SetItemText(sentence_list.GetFirstSelected(), new_sentence)


class UsersPanel(wx.Panel):
	"""Allows for viewing of user specific statistics."""

	def __init__(self, parent:wx.Notebook) -> None:
		"""Initialize the panel with a list of users and a statistics button."""
		super().__init__(parent=parent)
		self.user_list = wx.ListCtrl(
			self,
			id=wx.ID_ANY,
			name="Users",
			style=wx.LC_REPORT
			)
		self.user_list.InsertColumn(0, "Users")
		[self.user_list.Append(user) for user in self.users]
		self.user_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
		self.user_data = wx.TextCtrl(
			self,
			id=wx.ID_ANY,
			name="userData",
			value=f"There are {len(self.users)} users.",
			style=wx.TE_MULTILINE|wx.TE_READONLY
			)
		self.__do_layout()

	@property
	def users(self) -> list:
		"""Lists users in the database."""
		with session_scope() as session:
			return [result for result in session.query(Results.user_name).distinct()]

	def __do_layout(self):
		"""Lays out the controls on the panel"""
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		sizer.Add(self.user_list, proportion=1)
		sizer.Add(self.user_data, proportion=4, flag=wx.EXPAND)
		self.SetSizerAndFit(sizer)

	def onItemActivated(self, event: wx.ListEvent) -> None:
		"""Updates the user data shown when a user name is activated in the list."""
		from sqlalchemy.sql import func
		user = self.user_list.GetItem(event.GetIndex()).GetText()
		with session_scope() as session:
			count = session.query(Results).filter(Results.user_name == user).count()
			average_accuracy = session.query(func.avg(Results.accuracy)).filter(Results.user_name == user).scalar()
			average_speed = session.query(func.avg(Results.speed)).filter(Results.user_name == user).scalar()
		self.user_data.SetValue(f"{user} has taken {count} tests with an average accuracy of {average_accuracy:.1f}% and an average typing speed of {average_speed:.0f} words per minute")