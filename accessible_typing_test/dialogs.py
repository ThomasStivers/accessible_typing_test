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

"""Includes the SettingsDialog, SingleResultDialog, and TypingDialog classes."""

import datetime
import logging
import threading
from time import sleep
import pyttsx3
import wx
from accessible_typing_test.lev import levenshteinDistance
from accessible_typing_test.results_database import session_scope, Sentences, Results

class SettingsDialog(wx.Dialog):
	"""Settings which apply across all tests.

	* Configure the logging level to use.
	* Configure the speech voice, rate, and volume.
	"""

	def __init__(self, parent: wx.Frame = None, config: wx.Config = None) -> None:
		"""Initialize the SettingsDialog.

		Args:
			parent: This should usually be the TypingFrame.
			config: The configuration for the application.
			"""
		super().__init__(parent=parent, title="Settings")
		self._config = config
		self.logging_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
		self.speaker = pyttsx3.init(None)
		speech_voice_choices = [voice.name for voice in self.speaker.getProperty("voices")]
		self.message = wx.StaticText(
			self,
			id=wx.ID_ANY,
			label="Accessible Typing Test Settings"
			)
		self.logging_group = wx.StaticBox(
			self,
			id=wx.ID_ANY,
			label="Logging"
			)
		self.logging_label = wx.StaticText(
			self.logging_group,
			id=wx.ID_ANY,
			label="Logging Level")
		self.logging_choice = wx.Choice(
			self.logging_group,
			id=wx.ID_ANY,
			choices=self.logging_levels,
			name="loggingLevel"
			)
		self.logging_choice.SetStringSelection(
			config.Read("loggingLevel", defaultVal="info")
			)
		self.speech_group = wx.StaticBox(
			self,
			id=wx.ID_ANY,
			label="Speech"
			)
		self.speech_enabled = wx.CheckBox(
			self.speech_group,
			id=wx.ID_ANY,
			label="Enable Speech",
			name="speechEnabled"
			)
		self.speech_enabled.SetValue(
			config.ReadBool("speechEnabled", defaultVal=True)
			)
		self.speech_voice_label = wx.StaticText(
			self.speech_group,
			id=wx.ID_ANY,
			label="Speech Voice"
			)
		self.speech_voice = wx.Choice(
			self.speech_group,
			id=wx.ID_ANY,
			choices=speech_voice_choices
			)
		self.speech_voice.SetStringSelection(config.Read("speechVoice"))
		self.speech_rate_label = wx.StaticText(
			self.speech_group,
			id=wx.ID_ANY,
			label="Speech Rate"
			)
		self.speech_rate = wx.TextCtrl(
			self.speech_group,
			id=wx.ID_ANY,
			name="speechRate",
			value=str(config.ReadInt("speechRate", defaultVal=200))
			)
		self.speech_volume_label = wx.StaticText(
			self.speech_group,
			id=wx.ID_ANY,
			label="Speech Volume"
			)
		self.speech_volume = wx.TextCtrl(
			self.speech_group,
			id=wx.ID_ANY,
			name="speechVolume",
			value=str(config.ReadInt("speechVolume", defaultVal=100))
			)
		self.testing_group = wx.StaticBox(
			self,
			id=wx.ID_ANY,
			label="Testing"
			)
		self.testing_choose_words = wx.RadioButton(
			self.testing_group,
			id=wx.ID_ANY,
			label="Stop after &word count",
			name="wordsRadioButton",
			style=wx.RB_GROUP
			)
		self.testing_choose_time = wx.RadioButton(
			self.testing_group,
			id=wx.ID_ANY,
			label="Stop after &time expires",
			name="timeRadioButton"
			)
		self.testing_choose_words.SetValue(
			config.ReadBool(self.testing_choose_words.GetName(), defaultVal=True)
			)
		self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton, self.testing_choose_words)
		self.testing_choose_time.SetValue(
			config.ReadBool(self.testing_choose_time.GetName(), defaultVal=False)
			)
		self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton, self.testing_choose_time)
		self.testing_word_count_label = wx.StaticText(
			self.testing_group,
			id=wx.ID_ANY,
			label="How many words?"
			)
		self.testing_word_count = wx.TextCtrl(
			self.testing_group,
			id=wx.ID_ANY,
			name="wordCount",
			value=str(config.ReadInt("wordCount", defaultVal=10))
			)
		# self.Bind(wx.EVT_TEXT, self.onText, self.word_count)
		self.testing_time_limit_label = wx.StaticText(
			self.testing_group,
			id=wx.ID_ANY,
			label="How many seconds?"
			)
		self.testing_time_limit_label.Hide()
		self.testing_time_limit = wx.TextCtrl(
			self.testing_group,
			id=wx.ID_ANY,
			name="timeLimit",
			value=str(config.ReadInt("timeLimit", defaultVal=60))
			)
		self.testing_time_limit.Hide()
		# self.Bind(wx.EVT_TEXT, self.onText, self.time_limit)
		self.ok_button = wx.Button(self, wx.ID_OK, label="OK")
		self.Bind(wx.EVT_BUTTON, self.onOK, self.ok_button)
		self.ok_button.SetDefault()
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
		logging_sizer = wx.StaticBoxSizer(box=self.logging_group, orient=wx.VERTICAL)
		logging_sizer.Add(self.logging_label, proportion=0, flag=wx.ALIGN_LEFT)
		logging_sizer.Add(self.logging_choice, proportion=0, flag=wx.ALIGN_RIGHT)
		control_sizer.Add(logging_sizer, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
		speech_sizer = wx.StaticBoxSizer(box=self.speech_group, orient=wx.VERTICAL)
		speech_sizer.Add(self.speech_enabled)
		speech_sizer.Add(self.speech_voice_label)
		speech_sizer.Add(self.speech_voice)
		speech_sizer.Add(self.speech_rate_label)
		speech_sizer.Add(self.speech_rate)
		speech_sizer.Add(self.speech_volume_label)
		speech_sizer.Add(self.speech_volume)
		control_sizer.Add(speech_sizer, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
		testing_sizer = wx.StaticBoxSizer(box=self.testing_group, orient=wx.VERTICAL)
		testing_sizer.Add(self.testing_choose_words)
		testing_sizer.Add(self.testing_choose_time)
		testing_sizer.Add(self.testing_word_count_label)
		testing_sizer.Add(self.testing_word_count)
		testing_sizer.Add(self.testing_time_limit_label)
		testing_sizer.Add(self.testing_time_limit)
		control_sizer.Add(testing_sizer, proportion=0, flag=wx.EXPAND|wx.ALL, border=5)
		button_sizer.Add(self.ok_button)
		button_sizer.Add(self.cancel_button)
		top_sizer.Add(control_sizer, flag=wx.EXPAND)
		top_sizer.Add(button_sizer, flag=wx.ALIGN_BOTTOM|wx.ALIGN_CENTER_HORIZONTAL)
		self.SetSizer(top_sizer)
		top_sizer.Fit(self)
		self.Layout()
		self.Center()

	def onOK(self, event:wx.CommandEvent) -> None:
		"""Writes settings to the configuration when OK is pressed."""
		config = self._config
		config.Write("loggingLevel", self.logging_choice.GetStringSelection())
		config.WriteBool("speechEnabled", self.speech_enabled.GetValue())
		config.Write("speechVoice", self.speech_voice.GetStringSelection())
		config.WriteInt("speechRate", int(self.speech_rate.GetValue()))
		config.WriteInt("speechVolume", int(self.speech_volume.GetValue()))
		config.WriteInt("wordCount", int(self.testing_word_count.GetValue()))
		config.WriteInt("timeLimit", int(self.testing_time_limit.GetValue()))
		event.Skip()

	def onRadioButton(self, event: wx.CommandEvent) -> None:
		"""Handles testing_choose_time and testing_choose_words radio buttons.
		
		Chooses to show or hide the word count and time limit options based on the
		selected radio button. Also stores radio button state to the application
		configuration.
		"""
		obj = event.GetEventObject()
		self._config.WriteBool(obj.GetName(), obj.GetValue())
		if obj.GetName() == "wordsRadioButton" and obj.GetValue():
			self.testing_time_limit_label.Hide()
			self.testing_time_limit.Hide()
			self.testing_word_count_label.Show()
			self.testing_word_count.Show()
			self._config.WriteBool("wordsRadioButton", value=True)
			self._config.WriteBool("timeRadioButton", value=False)
		elif obj.GetName() == "timeRadioButton" and obj.GetValue():
			self.testing_time_limit_label.Show()
			self.testing_time_limit.Show()
			self.testing_word_count_label.Hide()
			self.testing_word_count.Hide()
			self._config.WriteBool("wordsRadioButton", value=False)
			self._config.WriteBool("timeRadioButton", value=True)
		self.Layout()


class SingleResultDialog(wx.Dialog):
	"""Display the details of a single test result."""

	def __init__(self, parent: wx.Window, result: Results) -> None:
		"""Initialize the dialog with test result details."""
		super().__init__(
			parent=parent,
			size=(450, 450),
			title=f"Test Result Details for test #{result.id}",
			)
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.label = wx.StaticText(
			self,
			label="Result Details"
			)
		self.text = wx.TextCtrl(
			self,
			id=wx.ID_ANY,
			name="testResult",
			style=wx.TE_READONLY | wx.TE_MULTILINE,
			value=str(result)
			)
		sizer.Add(self.label)
		sizer.Add(self.text, flag=wx.EXPAND)
		self.SetSizer(sizer)
		self.Center()
		self.text.SetFocus()


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
		self.word_count = self._config.ReadInt("wordCount", defaultVal=10)
		self.time_limit = self._config.ReadInt("timeLimit", defaultVal=30)
		self.typed_count = 0
		self.setupSpeech()
		self.used_sentences = set()
		record = Sentences.randomSentence()
		sentence = record.sentence
		self.used_sentences.add(record.id)
		self.given_label = wx.StaticText(
			self,
			id=wx.ID_ANY,
			label="Type the below text exactly as it is written. "
			"Press enter when you are done."""
			)
		self.given_label.SetForegroundColour("grey")
		self.given_text = wx.StaticText(
			self,
			id=wx.ID_ANY,
			name="GivenText",
			label=sentence
			)
		self.given_list = [sentence]
		self.typed_text = wx.TextCtrl(self, wx.ID_ANY,
			name="typedText", style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER
			)
		self.time_gauge = wx.Gauge(self, wx.ID_ANY, range=self.time_limit)
		self.typed_text.Bind(wx.EVT_TEXT_ENTER, self.onEnter, source=self.typed_text)
		self.typed_text.Bind(wx.EVT_CHAR, self.onTyping, source=self.typed_text)
		self.typed_text.SetFocus()
		self.typed_list = []
		self.start_time = datetime.datetime.now()
		self.timer = wx.Timer(self)
		self.gauge_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onTimer)
		self.__do_layout()
		if self.speech_enabled:
			self.speaker.say(sentence)
		self.timer.StartOnce(self.time_limit * 1000)
		self.gauge_timer.Start(1000)

	def __do_layout(self):
		"""Lays out the controls in the dialog."""
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.given_label,
			proportion=1,
			flag=wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL
			)
		sizer.Add(self.given_text, proportion=2, flag=wx.EXPAND)
		sizer.Add(self.typed_text, proportion=8, flag=wx.EXPAND)
		sizer.Add(self.time_gauge, flag=wx.ALIGN_BOTTOM)
		self.SetSizer(sizer)
		self.Fit()

	def setupSpeech(self)-> bool:
		"""Initialize and configure the speech engine.
		
		Returns:
			bool: True if speech is enabled, false otherwise.
			"""
		self.speech_enabled = self._config.ReadBool("speechEnabled", defaultVal=True)
		if self.speech_enabled:
			self.speaker = pyttsx3.init(None, debug=True)
			voices = self.speaker.getProperty("voices")
			voice_name = self._config.Read("speechVoice")
			voice_rate = self._config.ReadInt("speechRate", defaultVal=200)
			voice_volume = self._config.ReadInt("speechVolume", defaultVal=100)
			voice_id = [voice.id for voice in voices if voice.name == voice_name]
			self.speaker.setProperty("voice", voice_id[0])
			self.speaker.setProperty("rate", voice_rate)
			# pyttsx3 requires a volume in the range 0.0 to 1.0.
			self.speaker.setProperty("volume", voice_volume/100)
			self.speaker_thread = threading.Thread(
				target=self.speaker.startLoop,
				args=(True,),
				daemon=True
				)
			self.speaker_thread.start()
		return self.speech_enabled

	def onEnter(self, event: wx.CommandEvent = None) -> None:
		"""Handles enter when pressed in typed_text."""
		# WHY(self.time = int((datetime.datetime.now()-self.start_time).seconds))
		self.typed_list.append(self.typed_text.GetValue().strip())
		self.typed_count += len(self.typed_list[-1].split())
		self.typed_text.Clear()
		if self.typed_count <= self.word_count:
			record = Sentences.randomSentence()
			while record.id in self.used_sentences:
				record = Sentences.randomSentence()
			self.used_sentences.add(record.id)
			sentence = record.sentence
			self.given_text.SetLabel(sentence)
			self.given_list.append(sentence)
			self.Refresh()
			if self.speech_enabled: self.speaker.say(sentence)
			event.Skip()
		else:
			self.storeResults(self.calculateResults())
			if self.speech_enabled: self.speaker.endLoop()
			wx.MessageBox("Test completed.", caption="Done")
		self.end_time = datetime.datetime.now()

	def onTyping(self, event: wx.KeyEvent) -> None:
		"""Tracks the count of typed printable characters.

		Args:
			event (wx.KeyEvent): Using event.GetUnicodeKey(() will provide the key which
			was pressed.
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
			# Stop the speaker if time runs out.
			if self.speech_enabled: self.speaker.endLoop()
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
		self.GetParent().results_panel.fillTestList()
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
		results = {}
		typed = "\n".join(self.typed_list)
		given = "\n".join(self.given_list[0:len(self.typed_list)])
		count = self.typed_character_count
		for given_sentence, typed_sentence in zip(self.given_list, self.typed_list):
			logging.debug(f"given_sentence={repr(given_sentence)}, typed_sentence={repr(typed_sentence)}")
			# given += f"{given_sentence}\n"
		results['user_name'] = self.user_name
		results["start_time"] = self.start_time
		results['end_time'] = self.end_time
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
