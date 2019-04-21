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

import logging
import os
import wx
from accessible_typing_test.results_database import Sentences
# from accessible_typing_test.main import TestsPanel

class TypingMenuBar(wx.MenuBar):
	"""The menu bar displayed on the TypingFrame."""

	def __init__(self) -> None:
		"""Initialize the menu bar with its submenus and their items."""
		super().__init__()
		self.Bind(wx.EVT_MENU, self.menuHandler)
		keys = list()
		file = wx.Menu()
		self.Append(file, title="&File")
		edit = wx.Menu()
		self.Append(edit, title="&Edit")
		view = wx.Menu()
		self.Append(view, title="&View")
		help = wx.Menu()
		self.Append(help, title="&Help")

		file.Append(wx.ID_SAVE, "&Save Results\tCtrl+S")
		keys.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE))
		self._add_sentences_from_file_id = wx.Window.NewControlId()
		file.Append(
			self._add_sentences_from_file_id,
			item="&Add sentences from file\tCtrl+Shift+A",
			helpString="Adds sentences from a text file with 1 sentence per line."
			)
		keys.append(wx.AcceleratorEntry(
			wx.ACCEL_CTRL|wx.ACCEL_SHIFT,
			ord('A'),
			self._add_sentences_from_file_id
			))
		file.AppendSeparator()
		file.Append(
			wx.ID_EXIT,
			"E&xit\tCtrl+Q",
			helpString="Exit the application."
			)
		keys.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('Q'), wx.ID_EXIT))
		edit.Append(wx.ID_UNDO, "&Undo\tCTRL+Z")
		keys.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('Z'), wx.ID_UNDO))
		self.add_sentence_id = wx.Window.NewControlId()
		edit.Append(
			self.add_sentence_id,
			item="&Add a sentence...",
			helpString="Type in a new sentence to add to the database."
			)
		edit.Append(wx.ID_CLEAR, "C&lear")
		edit.Append(wx.ID_DELETE, "&Delete\tCtrl+D")
		keys.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('D'), wx.ID_DELETE))
		self.VIEW_RESULTS_ID = wx.Window.NewControlId()
		view.AppendRadioItem(
			self.VIEW_RESULTS_ID,
			item="&Results\tCtrl+1",
			help="Show the test results."
			)
		keys.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('1'), self.VIEW_RESULTS_ID))
		self.VIEW_TESTS_ID = wx.Window.NewControlId()
		view.AppendRadioItem(
			self.VIEW_TESTS_ID,
			item="&Tests\tCtrl+2",
			help="Show the test sentences.",
			)
		keys.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('2'), self.VIEW_TESTS_ID))
		self.VIEW_USERS_ID = wx.Window.NewControlId()
		view.AppendRadioItem(
			self.VIEW_USERS_ID,
			item="&Users\tCtrl+3",
			help="Show user statistics.",
			)
		keys.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('3'), self.VIEW_USERS_ID))
		help.Append(wx.ID_ABOUT, "&About")
		self.accelerator_table = wx.AcceleratorTable(keys)

	def menuHandler(self, event: wx.CommandEvent) -> None:
		"""Handles menu events.
		
		Take action(s) based on the id contained in the event. Passes the event on to
		the next handler when finished.
		
		Args:
			event (wx.CommandEvent): The event which called this function.
			"""
		id = event.GetId()
		logging.debug(f"Handling menu event {id}")
		if id == wx.ID_EXIT:
			self.GetParent().onExit(event)
		elif id == wx.ID_ABOUT:
			wx.MessageBox("Typing Test by Thomas Stivers")
		elif id == wx.ID_CLEAR:
			pass
		elif id == self._add_sentences_from_file_id:
			directory_name = os.path.abspath(".")
			file_name = ""
			with wx.FileDialog(
				self,
				"Import sentences from text file.",
				directory_name,
				file_name,
				"*.txt",
				wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
				) as dlg:
				if dlg.ShowModal() == wx.ID_OK:
					file_name = dlg.GetFilename()
					directory_name = dlg.GetDirectory()
					path = os.path.join(directory_name, file_name)
					Sentences.fillSentences(filename=path)
		elif id == self.add_sentence_id:
			TestsPanel.onAddSentence(None)
		elif id == wx.ID_DELETE:
			wx.MessageBox("Deleteing something I guess.")
		elif id == self.VIEW_RESULTS_ID:
			self.GetParent().notebook.ChangeSelection(0)
		elif id == self.VIEW_TESTS_ID:
			self.GetParent().notebook.ChangeSelection(1)
		elif id == self.VIEW_USERS_ID:
			self.GetParent().notebook.ChangeSelection(2)
		event.Skip()
