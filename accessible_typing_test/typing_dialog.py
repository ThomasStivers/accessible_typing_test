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

"""Contains the dialog used for handling typing tests."""

import datetime
import logging
from time import sleep
from pprint import pprint
import wx
from accessible_typing_test.lev import levenshteinDistance
from accessible_typing_test.results_database import session_scope, Sentences, Results

class TypingDialog(wx.Dialog):
	"""Dialog box for testing typing."""

	def __init__(self, parent: wx.Frame) -> None:
		"""Initialize a TypingDialog.
		
		Args:
			parent (accessible_typing_test.TypingFrame): The parent of this dialog box.
			This class depends on the parent being of type TypingFrame.
		"""
		self.name = "typingTest"
		super().__init__(parent=parent, name=self.name)
		self._config = parent._config
		self.user_name = parent.user_name.GetValue()
		self.word_count = self._config.ReadInt(
			parent.word_count.GetName(), defaultVal=int(parent.word_count.GetValue())
			)
		self.time_limit = self._config.ReadInt(
			parent.time_limit.GetName(), defaultVal=int(parent.time_limit.GetValue())
			)
		self.time = 0
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

	def onEnter(self, event: wx.CommandEvent = None) -> None:
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

	def onTyping(self, event: wx.KeyEvent) -> None:
		"""Tracks the count of typed characters excluding enter.
		
		Args:
			event (wx.KeyEvent): Using event.GetUnicodeKey(() will provide the key which was pressed.
		"""
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

	def onTimer(self, event: wx.TimerEvent) -> None:
		"""Fires for all timer events.
		
		Tests if the event comes from the gauge timer which counts seconds or
		from the generic timer which times the test.
		
		Args:
			event (wx.TimerEvent): Indicates which timer this method is handling.
		"""
		timer = event.GetTimer()
		if timer == self.gauge_timer:
			self.time_gauge.SetValue((datetime.datetime.now() - self.start_time).seconds)
		else:
			self.storeResults(self.calculateResults())
			# If we stop because of the timer we need to keep extra keys from taking
			# action in the TypingFrame.
			wx.MessageBox("Time is up.", caption="Done")
			sleep(1)

	def storeResults(self, results_dict: dict) -> Results:
		"""Stores the results of the typing test.
		
		Results are stored in the database and the test_list from our parent
		frame is updated with the results.
		
		Args:
			results_dict (dict): Results dictionary to be stored to the database.

		Returns:
			accessible_typing_test.Results: The database object storing the test
			results.
		"""
		with session_scope() as session:
			results = Results(**results_dict)
			session.add(results)
			test_list = self.GetParent().results_panel.test_list
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
		self.timer.Stop()
		self.Close()
		return results

	def calculateResults(self) -> dict:
		"""Compares the typed and given text and returns a results dictionary.
		
		Returns:
			dict: keys are accuracy, speed, duration, words, and timestamp.
		"""
		if not hasattr(self, "typed_character_count"):
			wx.MessageBox("Nothing typed. Cancelled test.")
			return {}
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
		