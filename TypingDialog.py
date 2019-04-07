"""Contains the dialog used for handling typing tests."""

import datetime
from lev import levenshteinDistance
from ResultsDatabase import Session, Sentences, Results
import logging
from time import sleep
from pprint import pprint
import wx

class TypingDialog(wx.Dialog):
	"""Dialog box for testing typing.
	
	Attributes:
	typed_count: Keeps track of the number of words typed across invocations of 
	this dialog.
	"""

	def __init__(self, parent):
		"""Initialize a TypingDialog.
		
		Arguments:
		parent: The parent of this dialog box. This class depends on the parent being 
		of type TypingFrame.
		"""
		super().__init__(parent=parent, name="TypingTest")
		self._config = parent._config
		self.user_name = self.GetParent().user_name.GetValue()
		self.word_count = self._config.ReadInt(
			parent.word_count.GetName(), defaultVal=int(parent.word_count.GetValue())
			)
		self.time_limit = self._config.ReadInt(
			parent.time_limit.GetName(), defaultVal=int(parent.time_limit.GetValue())
			)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.used_sentences = set()
		record = Sentences.randomSentence()
		self.sentence = record.sentence
		self.used_sentences.add(record.id)
		given_label = wx.StaticText(
			self, wx.ID_ANY,
			label="Type the below text exactly as it is written. "
			"Press enter when you are done."""
			)
		self.given_text = wx.TextCtrl(self, wx.ID_ANY,
			name="GivenText", style=wx.TE_MULTILINE|wx.TE_READONLY, value=self.sentence
			)
		self.typed_label = wx.StaticText(self, wx.ID_ANY, label=self.sentence)
		self.typed_text = wx.TextCtrl(self, wx.ID_ANY,
			name="typedText", style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER
			)
		sizer.Add(given_label,
			proportion=1, flag=wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL
			)
		sizer.Add(self.given_text, proportion=5, flag=wx.EXPAND)
		sizer.Add(self.typed_text, proportion=5, flag=wx.EXPAND)
		self.time_gauge = wx.Gauge(self, wx.ID_ANY, range=self.time_limit)
		sizer.Add(self.time_gauge, flag=wx.ALIGN_BOTTOM)
		self.typed_text.Bind(wx.EVT_TEXT_ENTER, self.onEnter, source=self.typed_text)
		self.typed_text.Bind(wx.EVT_CHAR, self.onTyping, source=self.typed_text)
		self.typed_label.Hide()
		self.SetSizer(sizer)
		self.Fit()
		self.typed_text.SetFocus()
		self.start_time = datetime.datetime.now()
		self.timer = wx.Timer(self)
		self.gauge_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer)
		self.timer.StartOnce(self.time_limit * 1000)
		self.gauge_timer.Start(1000)

	def onEnter(self, event=None):
		"""Handles enter when pressed in typed_text."""
		self.time = int((datetime.datetime.now()-self.start_time).seconds)
		# Remove any extra newline characters and convert any that remain into spaces.
		# self.typed_text.ChangeValue(
			# self.typed_text.GetValue().strip()
			# )
		self.typed_text.SetInsertionPointEnd()
		self.typed_count = len(self.typed_text.GetValue().split())
		if self.typed_count <= self.word_count:
			record = Sentences.randomSentence()
			while record.id in self.used_sentences:
				record = Sentences.randomSentence()
			self.used_sentences.add(record.id)
			self.sentence = record.sentence
			self.given_text.AppendText(f"\n{self.sentence}")
			self.typed_label.SetLabel(self.sentence)
			self.Refresh()
			self.Update()
		else:
			self.storeResults(self.calculateResults())
			wx.MessageBox("Test completed.", caption="Done")
			
	def onTyping(self, event):
		"""Track the count of typed characters excluding enter."""
		key = event.GetUnicodeKey()
		ignored_keys = [0, 8, 9, 13]
		if hasattr(self, "typed_character_count") and key not in ignored_keys:
			self.typed_character_count += 1
		elif key not in ignored_keys:
			self.typed_character_count = 1
		# logging.debug(f"In onTyping key={repr(chr(key))}, "
			# f"typed_text={repr(self.typed_text.GetValue())}")
		# Pass this event along.
		event.Skip()

	def onTimer(self, event):
		"""Fires for all timer events.
		
		Tests if the event comes from the gauge timer which counts seconds or
		from the generic timer which times the test."""
		timer = event.GetTimer()
		if timer == self.gauge_timer:
			self.time_gauge.SetValue((datetime.datetime.now() - self.start_time).seconds)
		else:
			self.storeResults(self.calculateResults())
			# If we stop because of the timer we need to keep extra keys from taking
			# action in the TypingFrame.
			wx.MessageBox("Time is up.", caption="Done")
			sleep(1)

	def storeResults(self, results):
		"""Stores the results of the typing test.
		
		Results are stored in the database and the test_list from our parent
		frame is updated with the results."""
		session = Session()
		results = Results(**results)
		session.add(results)
		session.commit()
		test_list = self.GetParent().test_list
		if test_list.GetItemCount() > 0:
			index = test_list.GetItemCount()
		else:
			index = 0
		test_list.InsertItem(index, f"{results.accuracy}%")
		test_list.SetItem(index, 1, f"{results.speed} WPM")
		test_list.SetItem(index, 2, f"{results.duration} seconds")
		test_list.SetItem(index, 3, f"{results.words}")
		test_list.SetItem(index, 4, f"{results.user_name}")
		test_list.SetItem(index, 5, results.timestamp)
		# If we don't explicitly stop this timer it runs even after the dialog is
		# closed.
		self.gauge_timer.Stop()
		self.Close()
		return results

	def calculateResults(self):
		"""Compares the typed and given text and returns a results dictionary.
		
		Returns:
		results: keys are accuracy, speed, duration, words, and timestamp.
		"""
		if not hasattr(self, "typed_character_count"):
			wx.MessageBox("Nothing typed. Cancelled test.")
			return
		typed = self.typed_text.GetValue().strip()
		given = self.given_text.GetValue()
		count = self.typed_character_count
		results = {}
		results['user_name'] = self.user_name
		results["start_time"] = self.start_time
		results['end_time'] = datetime.datetime.now()
		results['edit_distance'] = levenshteinDistance(given[0:count], typed)
		results['accuracy'] = \
			int((count - results['edit_distance']) /  count * 100)
		logging.debug(f"In calculateResults "
			f"given[0:{count}]={repr(given[0:count])}, "
			f"typed={repr(typed)}, "
			f"edit distance={results['edit_distance']}"
		)
		duration = results['end_time'] - results['start_time']
		results["duration"] = duration.seconds
		results["words"] = len(typed.split(" "))
		results["speed"] = int(results["words"] / (duration.total_seconds() / 60))
		results["timestamp"] = results["end_time"].strftime("%m/%d/%y %I:%M %p")
		results['given_text'] = given
		results['typed_text'] = typed
		return results