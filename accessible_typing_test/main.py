#!/usr/bin/python3
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

"""Script for testing typing speed and accuracy."""

import datetime
import logging
import os
import openpyxl
import wx
from accessible_typing_test.results_database import session_scope, Sentences, Results
from accessible_typing_test.typing_dialog import TypingDialog

class SettingsDialog(wx.Dialog):
	"""Settings which apply across all tests.

	* Configure the logging level to use.
	"""

	def __init__(self, parent: wx.Frame = None, config: wx.Config = None) -> None:
		"""Initialize the SettingsDialog.

		Args:
			parent: This should usually be the TypingFrame.
			config: The configuration for the application.
			"""
		super().__init__(parent=parent, title="Settings")
		self.logging_levels = ["debug", "info", "warning", "error", "critical"]
		self.message = wx.StaticText(
			self,
			id=wx.ID_ANY,
			label="Accessible Typing Test Settings"
			)
		self.logging_label = wx.StaticText(self, wx.ID_ANY, label="Logging Level")
		self.logging_choice = wx.Choice(
			self,
			id=wx.ID_ANY,
			choices=self.logging_levels,
			name="loggingLevel"
			)
		self.logging_choice.SetStringSelection(
			config.Read("loggingLevel", defaultVal="info")
			)

		self.ok_button = wx.Button(self, wx.ID_OK, label="OK")
		self.cancel_button = wx.Button(self, wx.ID_CANCEL, label="Cancel")
		self.__do_layout()

	def __do_layout(self) -> bool:
		"""Lays out the controls for this SettingsPanel."""
		# A sizer for the buttons will go at the bottom of the dialog.
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		# controls in the dialog are placed on a grid.
		control_sizer = wx.GridSizer(cols=2, rows=3, hgap=5, vgap=5)
		# The top_sizer contains and lays out the button_sizer and control_sizer.
		top_sizer = wx.BoxSizer(wx.VERTICAL)
		top_sizer.Add(self.message, flag=wx.ALIGN_CENTER_HORIZONTAL)
		
		# Keeps the label and control together.
		logging_sizer = wx.BoxSizer(wx.VERTICAL)
		logging_sizer.Add(self.logging_label, proportion=0, flag=wx.ALIGN_LEFT)
		logging_sizer.Add(self.logging_choice, proportion=0, flag=wx.ALIGN_RIGHT)
		control_sizer.Add(logging_sizer, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
		button_sizer.Add(self.ok_button)
		button_sizer.Add(self.cancel_button)
		top_sizer.Add(control_sizer, flag=wx.EXPAND)
		top_sizer.Add(button_sizer, flag=wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL)
		self.SetSizer(top_sizer)
		top_sizer.Fit(self)
		self.Layout()
		self.Center()


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
		self.message = wx.StaticText(
			self,
			id=wx.ID_ANY,
			label="Typing test program by Thomas Stivers."
			)
		# Now define the list control.
		self.test_list = wx.ListCtrl(
			self,
			id=wx.ID_ANY,
			name="Tests",
			style=wx.LC_REPORT
			)
		self.test_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
		self.test_list.InsertColumn(0, "Accuracy")
		self.test_list.InsertColumn(1, "Speed")
		self.test_list.InsertColumn(2, "Duration")
		self.test_list.InsertColumn(3, "Words")
		self.test_list.InsertColumn(4, "User")
		self.test_list.InsertColumn(5, "Timestamp")
		self.fillTestList()
		self.__do_layout()

	def __do_layout(self) -> None:
		"""Lays out the controls on the ResultsPanel."""
		v_sizer = wx.BoxSizer(wx.VERTICAL)
		# autofit the column widths now that we have list items.
		for col in range(self.test_list.GetColumnCount()):
			self.test_list.SetColumnWidth(col, wx.LIST_AUTOSIZE_USEHEADER)
		self.test_list.Layout()

		v_sizer.Add(
			self.message,
			proportion=0,
			border=5,
			flag=wx.ALIGN_CENTER_HORIZONTAL
			)
		v_sizer.Add(self.test_list)
		self.SetSizer(v_sizer)
		v_sizer.Fit(self)
		self.Layout()
		self.Center()


	def fillTestList(self):
		"""Populate the test_list with results from the database."""
		test_list = self.test_list
		index = test_list.GetItemCount()
		with session_scope() as session:
			for results in session.query(Results):
				test_list.InsertItem(index, f"{results.accuracy}%")
				test_list.SetItem(index, 1, f"{results.speed} WPM")
				test_list.SetItem(index, 2, f"{results.duration} seconds")
				test_list.SetItem(index, 3, f"{results.words}")
				test_list.SetItem(index, 4, f"{results.user_name}")
				test_list.SetItem(index, 5, results.timestamp)
				index += 1

	def onItemActivated(self, event:wx.ListEvent) -> None:
		"""Handles clicks on the test results list."""
		index = event.GetIndex()


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


class TypingMenuBar(wx.MenuBar):
	"""The menu bar displayed on the TypingFrame."""

	def __init__(self) -> None:
		"""Initialize the menu bar with its submenus and their items."""
		super().__init__()
		file = wx.Menu()
		self.Append(file, title="&File")
		edit = wx.Menu()
		self.Append(edit, title="&Edit")
		view = wx.Menu()
		self.Append(view, title="&View")
		help = wx.Menu()
		self.Append(help, title="&Help")

		file.Append(wx.ID_SAVE, "&Save Results")
		self.add_sentences_from_file_id = wx.Window.NewControlId()
		file.Append(self.add_sentences_from_file_id, "&Add sentences from file")
		file.AppendSeparator()
		file.Append(wx.ID_EXIT, "E&xit")
		edit.Append(wx.ID_UNDO, "&Undo")
		self.add_sentence_id = wx.Window.NewControlId()
		edit.Append(self.add_sentence_id, "&Add a sentence")
		edit.Append(wx.ID_CLEAR, "C&lear")
		help.Append(wx.ID_ABOUT, "&About")

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
		elif id == self.add_sentences_from_file_id:
			pass
		elif id == self.add_sentence_id:
			TestsPanel.onAddSentence(None)
		event.Skip()


class TypingFrame(wx.Frame):
	"""The top level window for the application."""

	def __init__(self) -> None:
		"""Initializes the top level window for the application."""
		super().__init__(None, title="Typing Test", size=(600, 800), name="typingFrame")
		self._config = wx.Config("typing_test")
		config = self._config
		self.menu_bar = TypingMenuBar()
		self.font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
		self.panel = wx.Panel(self)
		self.choose_words = wx.RadioButton(
			self.panel,
			id=wx.ID_ANY,
			label="&Words",
			name="wordsRadioButton",
			style=wx.RB_GROUP
			)
		self.choose_words.SetValue(
			config.ReadBool(self.choose_words.GetName(), defaultVal=True)
			)
		self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton, self.choose_words)
		self.choose_time = wx.RadioButton(
			self.panel,
			id=wx.ID_ANY,
			label="&Time",
			name="timeRadioButton"
			)
		self.choose_time.SetValue(
			config.ReadBool(self.choose_time.GetName(), defaultVal=False)
			)
		self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton, self.choose_time)
		self.word_count_label = wx.StaticText(
			self.panel,
			id=wx.ID_ANY,
			label="How many words?"
			)
		self.word_count = wx.TextCtrl(
			self.panel,
			id=wx.ID_ANY,
			name="wordCount",
			value=str(config.ReadInt("wordCount", defaultVal=10))
			)
		self.Bind(wx.EVT_TEXT, self.onText, self.word_count)
		self.time_limit_label = wx.StaticText(
			self.panel,
			id=wx.ID_ANY,
			label="How many seconds?"
			)
		self.time_limit_label.Hide()
		self.time_limit = wx.TextCtrl(
			self.panel,
			id=wx.ID_ANY,
			name="timeLimit",
			value=str(config.ReadInt("timeLimit", defaultVal=60))
			)
		self.time_limit.Hide()
		self.Bind(wx.EVT_TEXT, self.onText, self.time_limit)
		self.user_name_label = wx.StaticText(
			self.panel,
			id=wx.ID_ANY,
			label="Who are you?"
			)
		self.user_name = wx.TextCtrl(
			self.panel,
			id=wx.ID_ANY,
			name="userName",
			value=config.Read("userName", defaultVal="Unknown")
			)
		self.notebook = wx.Notebook(
			self.panel,
			id=wx.ID_ANY,
			name="typingTestNotebook",
			style=wx.NB_TOP
			)
		self.results_panel = ResultsPanel(self.notebook, config=config)
		self.notebook.AddPage(self.results_panel, "Results")
		self.tests_panel = TestsPanel(self.notebook)
		self.notebook.AddPage(self.tests_panel, "tests")

		# Define the buttons.
		self.start_button = wx.Button(
			self.panel,
			id=wx.ID_ANY,
			label="&Start Test"
			)
		self.start_button.SetDefault()
		self.start_button.SetFocus()
		self.Bind(wx.EVT_BUTTON, self.onStart, self.start_button)
		self.export_results_button = wx.Button(
			self.panel,
			id=wx.ID_ANY,
			label="Export &Results"
			)
		self.Bind(wx.EVT_BUTTON, self.onExportResults, self.export_results_button)
		self.settings_button = wx.Button(
			self.panel,
			id=wx.ID_ANY,
			label="Se&ttings"
			)
		self.Bind(wx.EVT_BUTTON, self.onSettings, self.settings_button)
		self.exit_button = wx.Button(
			self.panel, 
			id=wx.ID_ANY,
			label="E&xit"
			)
		self.Bind(wx.EVT_BUTTON, self.onExit, self.exit_button
		)

		#Give the frame a status bar.
		self.status_bar = wx.StatusBar(self, wx.ID_ANY)
		self.status_bar.SetStatusText(
			f"{self.results_panel.test_list.GetItemCount()} test results recorded.")
		self.SetStatusBar(self.status_bar)
		self.SetMenuBar(self.menu_bar)
		self.Bind(wx.EVT_MENU, self.menu_bar.menuHandler)

		self.__do_layout()
		self.Show(True)

	def __do_layout(self) -> None:
		"""Laysout the TypingFrame.
		
		
		"""
		font = self.font
		font.SetPointSize(16)
		self.notebook.SetFont(font)
		self.tests_panel.SetFont(font)
		self.results_panel.SetFont(font)
		self.SetFont(font)
		sizer = wx.BoxSizer(wx.VERTICAL)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer_flags = wx.SizerFlags(1).Align(wx.ALIGN_BOTTOM).Border(wx.ALL)
		choose_sizer = wx.BoxSizer(wx.HORIZONTAL)
		limit_sizer = wx.BoxSizer(wx.HORIZONTAL)
		user_sizer = wx.BoxSizer(wx.HORIZONTAL)
		grid_sizer = wx.GridSizer(rows=4, cols=2, hgap=5, vgap=5)
		choose_sizer.Add(self.choose_words)
		choose_sizer.Add(self.choose_time)
		limit_sizer.Add(self.word_count_label, flag=wx.ALIGN_RIGHT)
		limit_sizer.Add(self.word_count)
		limit_sizer.Add(self.time_limit_label, flag=wx.ALIGN_RIGHT)
		limit_sizer.Add(self.time_limit)
		user_sizer.Add(self.user_name_label, proportion=0, flag=wx.ALIGN_RIGHT)
		user_sizer.Add(self.user_name, proportion=1, flag=wx.EXPAND)
		grid_sizer.Add(choose_sizer, proportion=0, flag=wx.EXPAND) #Row 1 column 1
		grid_sizer.Add(limit_sizer, proportion=1, flag=wx.EXPAND) # Row 1 column 2
		grid_sizer.Add(user_sizer, proportion=1, flag=wx.EXPAND) # Row 2 column 1
		sizer.Add(self.notebook, border=5, flag=wx.ALL|wx.EXPAND)
		button_sizer.Add(self.start_button, button_sizer_flags)
		button_sizer.Add(self.export_results_button, button_sizer_flags)
		button_sizer.Add(self.settings_button, button_sizer_flags)
		button_sizer.Add(self.exit_button, button_sizer_flags)
		sizer.Add(button_sizer, flag=wx.ALIGN_BOTTOM)
		# Set the sizer for the frame, fit the controls to the frame, center
		# everything, and show the frame.
		self.SetSizerAndFit(sizer)
		self.Center()


	def onRadioButton(self, event: wx.CommandEvent) -> None:
		"""Handles choose_time and choose_words radio buttons.
		
		Chooses to show or hide the word count and time limit options based on the
		selected radio button. Also stores radio button state to the application
		configuration.
		"""
		obj = event.GetEventObject()
		self._config.WriteBool(obj.GetName(), obj.GetValue())
		if obj.GetName() == "wordsRadioButton" and obj.GetValue():
			self.time_limit_label.Hide()
			self.time_limit.Hide()
			self.word_count_label.Show()
			self.word_count.Show()
			self._config.WriteBool("wordsRadioButton", value=True)
			self._config.WriteBool("timeRadioButton", value=False)
		elif obj.GetName() == "timeRadioButton" and obj.GetValue():
			self.time_limit_label.Show()
			self.time_limit.Show()
			self.word_count_label.Hide()
			self.word_count.Hide()
			self._config.WriteBool("wordsRadioButton", value=False)
			self._config.WriteBool("timeRadioButton", value=True)
		self.Layout()

	def onText(self, event: wx.CommandEvent) -> None:
		"""Updates the configuration when word count and time limit are changed."""
		obj = event.GetEventObject()
		config = self._config
		logging.debug(f"In onText value is {obj.GetValue()}.")
		if config.ReadInt(obj.GetName()) != int(obj.GetValue()):
			config.WriteInt(obj.GetName(), int(obj.GetValue()))

	def onStart(self, event: wx.CommandEvent) -> None:
		"""Handles the Start button.
		
		Opens a TypingDialog to run the test and updates the status bar of the
		TypingFrame when the test finishes.
		"""
		logging.debug("Starting test...")
		dlg = TypingDialog(self)
		dlg.ShowModal()
		with session_scope() as session:
			self.GetStatusBar().SetStatusText(
				f"{self.results_panel.test_list.GetItemCount()} test results recorded."
				)

	def onSettings(self, event: wx.CommandEvent) -> None:
		"""Opens the SettingsDialog."""
		logging.debug("Opening settings...")
		dlg = SettingsDialog(self, config=self._config)
		dlg.ShowModal()

	def onExportResults(self, event: wx.CommandEvent) -> None:
		"""Exports results into an Excel worksheet."""
		user_name = self.results_panel.user_name.GetValue()
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		directory_name = ""
		file_name = f"{date} - {user_name} - Typing Test Results.xlsx"
		dlg = wx.FileDialog(
			self,
			"Export to Excel workbook",
			directory_name,
			file_name,
			"*.xlsx",
			wx.FD_SAVE
			)
		if dlg.ShowModal() == wx.ID_OK:
			file_name = dlg.GetFilename()
			directory_name = dlg.GetDirectory()
		path = os.path.join(directory_name, file_name)
		wb = openpyxl.workbook.Workbook()
		ws = wb.active
		fields = ["Accuracy", "Speed", "Duration", "Words", "User", "Timestamp"]
		ws.append(fields)
		for index in range(self.test_list.GetItemCount()):
			record = []
			for column in range(self.test_list.GetColumnCount()):
				record.append(self.test_list.GetItem(index, column).GetText())
			ws.append(record)
		wb.save(path)

	def onExit(self, event: wx.CommandEvent) -> None:
		"""Handles exiting of the application.

		Does nothing but log a message at this time.
		"""
		config = self._config
		logging.debug(f"Exiting due to {event.GetEventObject()}.")
		self.Close(True)


def main():
	"""Runs the application."""
	logging.basicConfig(
		format="%(asctime)s: %(levelname)s: %(message)s",
		datefmt="%Y-%m-%d %I:%M:%S %p",
		level=logging.DEBUG
		)
	logging.info("Starting up...")
	app = wx.App(False)
	frame = TypingFrame()
	logging.debug("frame size = %s" % frame.GetSize())
	app.SetTopWindow(frame)
	app.MainLoop()
	logging.info("Shutting down.")

if __name__ == "__main__":
	main()
