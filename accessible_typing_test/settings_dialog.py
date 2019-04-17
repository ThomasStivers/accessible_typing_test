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
import wx

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
		self.speech_voice_label = wx.StaticText(
			self.speech_group,
			id=wx.ID_ANY,
			label="Speech Voice"
			)
		self.speech_voice = wx.Choice(
			self.speech_group,
			id=wx.ID_ANY,
			choices=["TODO: speech stuff"]
			)
		self.speech_rate_label = wx.StaticText(
			self.speech_group,
			id=wx.ID_ANY,
			label="Speech Rate"
			)
		self.speech_rate = wx.TextCtrl(
			self.speech_group,
			id=wx.ID_ANY,
			name="speechRate",
			value=str(config.ReadInt("speechRate", defaultVal=100))
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
		config.Write("speechVoice", self.speech_voice.GetStringSelection())
		config.WriteInt("speechRate", int(self.speech_rate.GetValue()))
		config.WriteInt("speechVolume", int(self.speech_volume.GetValue()))
		event.Skip()
