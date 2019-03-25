# Script for testing typing speed and accuracy.

import openpyxl
import os
import wx
import wx.lib.agw.persist as pm
from random import shuffle
from TypingDialog import TypingDialog

class SettingsDialog(wx.Dialog):
	pass

class TypingFrame(wx.Frame):

	def __init__(self):
		super().__init__(None, title="Typing Test", size=(850, 1100), name="Typing Frame")
		persistence_file = os.path.join(os.getcwd(), "typing_test.dat")
		self._persistence_manager = pm.PersistenceManager.Get()
		self._persistence_manager.SetPersistenceFile(persistence_file)
		with open("sentences.txt", "r") as sentence_file:
			self.sentences = sentence_file.read().split("\n")
			shuffle(self.sentences)
		font = wx.Font(wx.FontInfo(16))
		panel = wx.Panel(self, size=self.GetSize())
		h_sizer = wx.BoxSizer(wx.HORIZONTAL)
		h_sizer_flags = wx.SizerFlags(1).Align(wx.ALIGN_BOTTOM).Border(wx.ALL)
		v_sizer = wx.BoxSizer(wx.VERTICAL)

		word_count_label = wx.StaticText(panel, wx.ID_ANY, label="How many words?")
		self.word_count = wx.TextCtrl(panel, wx.ID_ANY, value="10", name="Word Count")
		user_name_label = wx.StaticText(panel, wx.ID_ANY, label="Who are you?")
		self.user_name = wx.TextCtrl(panel, wx.ID_ANY, value="Unknown", name="User Name")
		self._persistence_manager.RegisterAndRestore(self.user_name)
		self._persistence_manager.RegisterAndRestore(self.word_count)

		# Define the buttons.
		start_button = wx.Button(panel, wx.ID_ANY, label="&Start Test")
		start_button.SetDefault()
		export_results_button = wx.Button(panel, wx.ID_ANY, label="Export &Results")
		settings_button = wx.Button(panel, wx.ID_ANY, label="S&ettings")
		exit_button = wx.Button(panel, wx.ID_ANY, label="E&xit")

# Now define the list control.
		self.test_list = wx.ListCtrl(panel, wx.ID_ANY, name="Tests", style=wx.LC_REPORT)
		self.test_list.InsertColumn(0, "Accuracy")
		self.test_list.InsertColumn(1, "Speed")
		self.test_list.InsertColumn(2, "Duration")
		self.test_list.InsertColumn(3, "Words")
		self.test_list.InsertColumn(4, "User")
		self.test_list.InsertColumn(5, "Timestamp")
		self._persistence_manager.RegisterAndRestore(self.test_list)

		# Bind the controls to their event handlers.
		self.Bind(wx.EVT_BUTTON, self.onStart, start_button)
		self.Bind(wx.EVT_BUTTON, self.onExportResults, export_results_button)
		self.Bind(wx.EVT_BUTTON, self.onSettings, settings_button)
		self.Bind(wx.EVT_BUTTON, self.onExit, exit_button)
		# self.Bind(wx.EVT_CLOSE, self.onExit)

		# Now fill the sizers with controls.
		h_sizer.Add(start_button, h_sizer_flags)
		h_sizer.Add(export_results_button, h_sizer_flags)
		h_sizer.Add(settings_button, h_sizer_flags)
		h_sizer.Add(exit_button, h_sizer_flags)
		v_sizer.Add(self.word_count)
		v_sizer.Add(self.user_name)
		v_sizer.Add(h_sizer)
		v_sizer.Add(self.test_list)

		# Set the sizer for the frame, fit the controls to the frame, center everything, and show the frame.
		self.SetSizer(v_sizer)
		panel.SetFont(font)
		self.Fit()
		self.Center()
		self.Show(True)
		start_button.SetFocus()

	def onStart(self, event):
		dlg = TypingDialog(self)
		dlg.ShowModal()
		self._persistence_manager.Save(self.user_name)
		self._persistence_manager.Save(self.word_count)
		self._persistence_manager.Save(self.test_list)

	def onSettings(self, event):
		dlg = SettingsDialog()

	def onExportResults(self, event):
		directory_name = ""
		dlg = wx.FileDialog(self, "Export to Excel workbook", directory_name, "", "*.xlsx", wx.FD_SAVE)
		if dlg.ShowModal() == wx.ID_OK:
			filename = dlg.GetFilename()
			directory = dlg.GetDirectory()
		path = os.path.join(directory, filename)
		wb = openpyxl.workbook.Workbook()
		ws = wb.active
		ws.append(["Accuracy", "Speed", "Duration", "Words", "User", "Timestamp"])
		for index in range(self.test_list.GetItemCount()):
			record = []
			for column in range(self.test_list.GetColumnCount()):
				record.append(self.test_list.GetItem(index, column).GetText())
			ws.append(record)
		wb.save(path)

	def onExit(self, event):
		# self._persistence_manager.SaveAndUnregister(self.user_name)
		# self._persistence_manager.SaveAndUnregister(self.test_list)
		self.Close(True)

if __name__ == "__main__":
	app = wx.App(False)
	frame = TypingFrame()
	app.SetTopWindow(frame)
	app.MainLoop()