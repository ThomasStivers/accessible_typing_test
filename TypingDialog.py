import datetime
from lev import levenshteinDistance
import wx

class TypingDialog(wx.Dialog):
	"""Dialog box for testing typing.
	
	Attributes:
	typed_count: Keeps track of the number of words typed across invocations of this dialog.
	"""

	typed_count = 0

	def __init__(self, parent):
		"""Initialize a TypingDialog.
		
		Arguments:
		parent: The parent of this dialog box. This class depends on the parent having a specific interface.
		"""
		super().__init__(parent=parent, name="TypingTest")
		self.word_count = int(parent.word_count.GetValue())
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.sentence = parent.sentences.pop()
		given_label = wx.StaticText(self, wx.ID_ANY, label=f"Type the below text exactly as it is written. Press enter when you are done.")
		self.given_text = wx.TextCtrl(self, wx.ID_ANY, name="Given", style=wx.TE_MULTILINE|wx.TE_READONLY, value=self.sentence)
		self.typed_label = wx.StaticText(self, wx.ID_ANY, label=self.sentence)
		self.typed_text = wx.TextCtrl(self, wx.ID_ANY, name="Typing", style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
		sizer.Add(given_label, proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL)
		sizer.Add(self.given_text, proportion=5, flag=wx.EXPAND)
		sizer.Add(self.typed_text, proportion=5, flag=wx.EXPAND)
		self.typed_text.Bind(wx.EVT_TEXT_ENTER, self.onEnter, source=self.typed_text)
		self.typed_label.Hide()
		sizer.SetSizeHints(self)
		self.SetSizer(sizer)
		self.Fit()
		self.typed_text.SetFocus()
		self.start_time = datetime.datetime.now()

	def onEnter(self, event):
		"""Handles enter when pressed in typed_text."""
		user_name = self.GetParent().user_name.GetValue()
		self.typed_text.SetValue(self.typed_text.GetValue().replace("\n", " "))
		self.typed_text.SetInsertionPointEnd()
		self.typed_count = len(self.typed_text.GetValue().split(" "))
		if self.typed_count <= self.word_count:
			self.sentence = self.GetParent().sentences.pop()
			self.given_text.AppendText(f" {self.sentence}")
			self.typed_label.SetLabel(self.sentence)
			self.Refresh()
			self.Update()
		else:
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
			self.GetParent()._persistence_manager.Save(test_list)
			self.Close()

	def calculateResults(self):
		"""Compares the typed and given text and returns a results dictionary.
		
		Returns:
		results: keys are accuracy, speed, duration, words, and timestamp.
		"""
		typed = self.typed_text.GetValue()
		given = self.given_text.GetValue()
		results = {}
		results["end_time"] = datetime.datetime.now()
		results["accuracy"] = int((len(given)-levenshteinDistance(given, typed))/len(given)*100)
		results["duration"] = results['end_time'] - self.start_time
		results["words"] = len(typed.split(" "))
		results["speed"] = int(results["words"] / (results["duration"].total_seconds() / 60))
		results["timestamp"] = results["end_time"].strftime("%m/%d/%y %H:%M")
		return results