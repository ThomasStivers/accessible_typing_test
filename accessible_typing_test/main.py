"""Script for testing typing speed and accuracy."""

import datetime
import logging
import os
import openpyxl
import wx
from ResultsDatabase import session_scope, Sentences, Results
from TypingDialog import TypingDialog

class SettingsDialog(wx.Dialog):
	"""Settings which apply across all tests.

	* Configure the logging level to use.
	"""

	def __init__(self, parent=None, config=None):
		"""Initialize the SettingsDialog.

		Args:
			parent (wx.Window): This should usually be the TypingFrame.
			config (wx.Config): The configuration for the application.
			"""
		super().__init__(parent=parent, title="Settings")
		logging_levels = ["debug", "info", "warning", "error", "critical"]
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		control_sizer = wx.GridSizer(cols=2, rows=3, hgap=5, vgap=5)
		top_sizer = wx.BoxSizer(wx.VERTICAL)
		message = wx.StaticText(self, wx.ID_ANY, label="Settings will go here.")
		top_sizer.Add(message, flag=wx.ALIGN_CENTER_HORIZONTAL)
		logging_sizer = wx.BoxSizer(wx.VERTICAL)
		logging_label = wx.StaticText(self, wx.ID_ANY, label="Logging Level")
		logging_sizer.Add(logging_label, proportion=0, flag=wx.ALIGN_LEFT)
		logging_choice = wx.Choice(
			self,
			id=wx.ID_ANY,
			choices=logging_levels,
			name="loggingLevel"
			)
		logging_choice.SetStringSelection(
			config.Read("loggingLevel", defaultVal="info")
			)
		logging_sizer.Add(logging_choice, proportion=0, flag=wx.ALIGN_RIGHT)
		control_sizer.Add(logging_choice, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)

		ok_button = wx.Button(self, wx.ID_OK, label="OK")
		button_sizer.Add(ok_button)
		cancel_button = wx.Button(self, wx.ID_CANCEL, label="Cancel")
		button_sizer.Add(cancel_button)
		top_sizer.Add(control_sizer, flag=wx.EXPAND)
		top_sizer.Add(button_sizer, flag=wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL)
		self.SetSizer(top_sizer)
		self.Center()

class ResultsPanel(wx.Panel):
	"""Results of a series of typing tests."""

	def __init__(self, parent, config=None):
		"""Initialize the ResultsPanel.

		Args:
			parent: The wx.Notebook that contains this panel.
			config: A wx.Config object containing application configuration.
		"""

		super().__init__(parent, name="resultsPanel")
		self._config = config
		v_sizer = wx.BoxSizer(wx.VERTICAL)
		# Now define the list control.
		self.test_list = wx.ListCtrl(self, wx.ID_ANY, name="Tests", style=wx.LC_REPORT)
		self.test_list.InsertColumn(0, "Accuracy")
		self.test_list.InsertColumn(1, "Speed")
		self.test_list.InsertColumn(2, "Duration")
		self.test_list.InsertColumn(3, "Words")
		self.test_list.InsertColumn(4, "User")
		self.test_list.InsertColumn(5, "Timestamp")
		self.fillTestList()
		for col in range(self.test_list.GetColumnCount()):
			self.test_list.SetColumnWidth(col, wx.LIST_AUTOSIZE_USEHEADER)
		self.test_list.Layout()
		# v_sizer.Add(
			# wx.StaticText(
				# self,
				# id=wx.ID_ANY,
				# label="Typing test program by Thomas Stivers."
				# ),
			# proportion=0,
			# border=5,
			# flag=wx.ALIGN_CENTER_HORIZONTAL
		# )
		# v_sizer.Add(grid_sizer)
		v_sizer.Add(self.test_list)
		self.SetSizer(v_sizer)

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

class TestsPanel(wx.Panel):
	"""Displays the test sentences and adds or removes them."""

	def __init__(self, parent):
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

	def onAddSentence(self, event=None):
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

	def onRemoveSentence(self, event):
		with session_scope() as session:
			query = session.query(Sentences)
			sentence_list = self.sentence_list
			sentence = sentence_list.GetItem(sentence_list.GetFirstSelected()).GetText()
			for found_record in query.filter(Sentences.sentence == sentence):
				record = found_record
			session.delete(record)

class TypingMenuBar(wx.MenuBar):

	def __init__(self):
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

	def menuHandler(self, event):
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

	def __init__(self):
		super().__init__(None, title="Typing Test", size=(600, 800), name="typingFrame")
		self._config = wx.Config("typing_test")
		config = self._config
		menuBar = TypingMenuBar()
		font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
		font.SetPointSize(16)
		sizer = wx.BoxSizer(wx.VERTICAL)
		button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		button_sizer_flags = wx.SizerFlags(1).Align(wx.ALIGN_BOTTOM).Border(wx.ALL)
		choose_sizer = wx.BoxSizer(wx.HORIZONTAL)
		limit_sizer = wx.BoxSizer(wx.HORIZONTAL)
		user_sizer = wx.BoxSizer(wx.HORIZONTAL)
		grid_sizer = wx.GridSizer(rows=4, cols=2, hgap=5, vgap=5)
		panel = wx.Panel(self)
		choose_words = wx.RadioButton(
			panel,
			id=wx.ID_ANY,
			label="&Words",
			name="wordsRadioButton",
			style=wx.RB_GROUP
			)
		choose_words.SetValue(
			config.ReadBool(choose_words.GetName(), defaultVal=True)
			)
		choose_sizer.Add(choose_words)
		self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton, choose_words)
		choose_time = wx.RadioButton(
			panel,
			id=wx.ID_ANY,
			label="&Time",
			name="timeRadioButton"
			)
		choose_time.SetValue(
			config.ReadBool(choose_time.GetName(), defaultVal=False)
			)
		choose_sizer.Add(choose_time)
		self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton, choose_time)
		grid_sizer.Add(choose_sizer, proportion=0, flag=wx.EXPAND) #Row 1 column 1
		self.word_count_label = wx.StaticText(
			panel,
			id=wx.ID_ANY,
			label="How many words?"
			)
		limit_sizer.Add(self.word_count_label, flag=wx.ALIGN_RIGHT)
		self.word_count = wx.TextCtrl(
			panel,
			id=wx.ID_ANY,
			name="wordCount",
			value=str(config.ReadInt("wordCount", defaultVal=10))
			)
		limit_sizer.Add(self.word_count)
		self.Bind(wx.EVT_TEXT, self.onText, self.word_count)
		self.time_limit_label = wx.StaticText(
			panel,
			id=wx.ID_ANY,
			label="How many seconds?"
			)
		limit_sizer.Add(self.time_limit_label, flag=wx.ALIGN_RIGHT)
		self.time_limit_label.Hide()
		self.time_limit = wx.TextCtrl(
			panel,
			id=wx.ID_ANY,
			name="timeLimit",
			value=str(config.ReadInt("timeLimit", defaultVal=60))
			)
		limit_sizer.Add(self.time_limit)
		self.time_limit.Hide()
		self.Bind(wx.EVT_TEXT, self.onText, self.time_limit)
		user_name_label = wx.StaticText(panel, wx.ID_ANY, label="Who are you?")
		user_sizer.Add(user_name_label, proportion=0, flag=wx.ALIGN_RIGHT)
		self.user_name = wx.TextCtrl(
			panel,
			id=wx.ID_ANY,
			name="userName",
			value=config.Read("userName", defaultVal="Unknown")
			)
		user_sizer.Add(self.user_name, proportion=1, flag=wx.EXPAND)
		grid_sizer.Add(limit_sizer, proportion=1, flag=wx.EXPAND) # Row 1 column 2
		grid_sizer.Add(user_sizer, proportion=1, flag=wx.EXPAND) # Row 2 column 1
		notebook = wx.Notebook(
			panel,
			id=wx.ID_ANY,
			name="typingTestNotebook",
			style=wx.NB_TOP
			)
		notebook.SetFont(font)
		self.results_panel = ResultsPanel(notebook, config=config)
		self.results_panel.SetFont(font)
		notebook.AddPage(self.results_panel, "Results")
		self.tests_panel = TestsPanel(notebook)
		self.tests_panel.SetFont(font)
		notebook.AddPage(self.tests_panel, "tests")
		sizer.Add(notebook, border=5, flag=wx.ALL|wx.EXPAND)

		# Define the buttons.
		start_button = wx.Button(panel, wx.ID_ANY, label="&Start Test")
		start_button.SetDefault()
		start_button.SetFocus()
		self.Bind(wx.EVT_BUTTON, self.onStart, start_button)
		export_results_button = wx.Button(panel, wx.ID_ANY, label="Export &Results")
		self.Bind(wx.EVT_BUTTON, self.onExportResults, export_results_button)
		settings_button = wx.Button(panel, wx.ID_ANY, label="Se&ttings")
		self.Bind(wx.EVT_BUTTON, self.onSettings, settings_button)
		exit_button = wx.Button(panel, wx.ID_ANY, label="E&xit")
		self.Bind(wx.EVT_BUTTON, self.onExit, exit_button)
		button_sizer.Add(start_button, button_sizer_flags)
		button_sizer.Add(export_results_button, button_sizer_flags)
		button_sizer.Add(settings_button, button_sizer_flags)
		button_sizer.Add(exit_button, button_sizer_flags)
		sizer.Add(button_sizer, flag=wx.ALIGN_BOTTOM)

		#Give the frame a status bar.
		status_bar = wx.StatusBar(self, wx.ID_ANY)
		status_bar.SetStatusText(
			f"{self.results_panel.test_list.GetItemCount()} test results recorded.")
		self.SetStatusBar(status_bar)
		self.SetMenuBar(menuBar)
		self.Bind(wx.EVT_MENU, menuBar.menuHandler)

		# Set the sizer for the frame, fit the controls to the frame, center
		# everything, and show the frame.
		self.SetFont(font)
		self.SetSizerAndFit(sizer)
		self.Center()
		self.Show(True)

	def onRadioButton(self, event):
		obj = event.GetEventObject()
		self._config.WriteBool(obj.GetName(), obj.GetValue())
		if obj.GetName() == "wordsRadioButton" and obj.GetValue() == True:
			self.time_limit_label.Hide()
			self.time_limit.Hide()
			self.word_count_label.Show()
			self.word_count.Show()
			self._config.WriteBool("wordsRadioButton", value=True)
			self._config.WriteBool("timeRadioButton", value=False)
		elif obj.GetName() == "timeRadioButton" and obj.GetValue() == True:
			self.time_limit_label.Show()
			self.time_limit.Show()
			self.word_count_label.Hide()
			self.word_count.Hide()
			self._config.WriteBool("wordsRadioButton", value=False)
			self._config.WriteBool("timeRadioButton", value=True)
		self.Layout()

	def onText(self, event):
		obj = event.GetEventObject()
		config = self._config
		logging.debug(f"In onText value is {obj.GetValue()}.")
		if config.ReadInt(obj.GetName()) != int(obj.GetValue()):
			config.WriteInt(obj.GetName(), int(obj.GetValue()))

	def onStart(self, event):
		logging.debug("Starting test...")
		dlg = TypingDialog(self)
		dlg.ShowModal()
		with session_scope() as session:
			self.GetStatusBar().SetStatusText(
				f"{self.results_panel.test_list.GetItemCount()} test results recorded."
				)

	def onSettings(self, event):
		logging.debug("Opening settings...")
		dlg = SettingsDialog(self, config=self._config)
		dlg.ShowModal()

	def onExportResults(self, event):
		"""Export results into an Excel worksheet."""
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

	def onExit(self, event):
		config = self._config
		logging.debug(f"Exiting due to {event.GetEventObject()}.")
		self.Close(True)

def main():
	logging.basicConfig(
		format="%(asctime)s: %(levelname)s: %(message)s",
		datefmt="%Y-%m-%d %I:%M:%S %p",
		level=logging.DEBUG
		)
	logging.debug("Starting up...")
	app = wx.App(False)
	frame = TypingFrame()
	logging.debug("frame size = %s" % frame.GetSize())
	app.SetTopWindow(frame)
	app.MainLoop()
	logging.debug("Shutting down.")

if __name__ == "__main__":
	main()
