# Script for testing typing speed and accuracy.

import datetime
import openpyxl
import os
import wx
import wx.lib.agw.persist as pm
from lev import levenshteinDistance
from random import shuffle

class TypingDialog(wx.Dialog):
	"""Dialog box for testing typing."""

	typed_count = 0

	def __init__(self, parent, sentence_count=1):
		wx.Dialog.__init__(self, parent=parent)
		self._persistence_manager = pm.PersistenceManager.get()
		self._persistence_manager.SetPersistenceFile("typing_test.dat")
		if not self._persistence_manager.SaveAndRestoreAll(self):
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.sentence = parent.sentences.pop()
		given_label = wx.StaticText(self, wx.ID_ANY, label=f"Type the below text exactly as it is written. Press enter when you are done.")
		given_text = wx.TextCtrl(self, wx.ID_ANY, name="Given", style=wx.TE_MULTILINE|wx.TE_READONLY, value=self.sentence)
		typed_label = wx.StaticText(self, wx.ID_ANY, label=self.sentence)
		typed_text = wx.TextCtrl(self, wx.ID_ANY, name="Typing", style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER|wx.TE_PASSWORD)
		sizer.Add(given_label)
		sizer.Add(given_text)
		sizer.Add(typed_label)
		sizer.Add(typed_text)
		self.Bind(wx.EVT_TEXT_ENTER, self.onEnter, typed_text)
		self.SetSizer(sizer)
		self.Fit()
		self.Show(True)
		typed_text.SetFocus()
		self.start_time = datetime.datetime.now()
		pm.PersistenceManager.Register(self))

	def onEnter(self, event):
		self.typed = event.GetEventObject().GetValue()
		sentence_count = int(self.GetParent().sentence_count.GetValue())
		user_name = self.GetParent().user_name.GetValue()
		self.typed_count += 1
		if self.typed_count <= sentence_count:
			self.Show(True)
			results = self.calculateResults()
		test_list = self.GetParent().test_list
		if test_list.GetItemCount() > 0:
			index = test_list.GetItemCount()
		else:
			index = 0
		test_list.InsertItem(index, f"{results['accuracy']}%")
		test_list.SetItem(index, 1, f"{results['speed']} WPM")
		test_list.SetItem(index, 2, f"{results['duration'].seconds} seconds")
		test_list.SetItem(index, 3, str(results['words']))
		test_list.SetItem(index, 4, user_name)
		test_list.SetItem(index, 5, results["timestamp"])
		self.Close()

	def calculateResults(self):
		typed = self.typed
		results = {}
		results["end_time"] = datetime.datetime.now()
		results["accuracy"] = int((len(self.sentence)-levenshteinDistance(self.sentence, typed))/len(self.sentence)*100)
		results["duration"] = results['end_time'] - self.start_time
		results["words"] = len(typed.split(" "))
		results["speed"] = int(results["words"] / (results["duration"].total_seconds() / 60))
		results["timestamp"] = results["end_time"].strftime("%m/%d/%y %H:%M")
		return results


	def export_results(self):
		pass

class SettingsDialog(wx.Dialog):
	pass

class ResultsDialog(wx.Dialog):
	pass

class TypingFrame(wx.Frame):

	def __init__(self):
		wx.Frame.__init__(self, None, title="Typing Test", size=(600, 800))
		with open("sentences.txt", "r") as sentence_file:
			self.sentences = sentence_file.read().split("\n")
			shuffle(self.sentences)
		font = wx.Font(wx.FontInfo(16))
		panel = wx.Panel(self)
		h_sizer = wx.BoxSizer(wx.HORIZONTAL)
		h_sizer_flags = wx.SizerFlags(1).Align(wx.ALIGN_BOTTOM).Border(wx.ALL)
		v_sizer = wx.BoxSizer(wx.VERTICAL)

		sentence_count_label = wx.StaticText(panel, wx.ID_ANY, label="How many sentences?")
		self.sentence_count = wx.TextCtrl(panel, wx.ID_ANY, value="1")
		user_name_label = wx.StaticText(panel, wx.ID_ANY, label="Who are you?")
		self.user_name = wx.TextCtrl(panel, wx.ID_ANY, value="Unknown")

		# Define the buttons.
		start_button = wx.Button(panel, wx.ID_ANY, label="&Start Test")
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

		# Bind the controls to their event handlers.
		self.Bind(wx.EVT_BUTTON, self.onStart, start_button)
		self.Bind(wx.EVT_BUTTON, self.onExportResults, export_results_button)
		self.Bind(wx.EVT_BUTTON, self.onSettings, settings_button)
		self.Bind(wx.EVT_BUTTON, self.onExit, exit_button)

		# Now fill the sizers with controls.
		h_sizer.Add(start_button, h_sizer_flags)
		h_sizer.Add(export_results_button, h_sizer_flags)
		h_sizer.Add(settings_button, h_sizer_flags)
		h_sizer.Add(exit_button, h_sizer_flags)
		v_sizer.Add(self.sentence_count)
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
		self.Close(True)

if __name__ == "__main__":
	app = wx.App(False)
	frame = TypingFrame()
	app.SetTopWindow(frame)
	app.MainLoop()