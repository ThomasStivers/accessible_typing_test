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
from accessible_typing_test.menus import TypingMenuBar
from accessible_typing_test.dialogs import *
from accessible_typing_test.panels import *
from accessible_typing_test.results_database import session_scope, Sentences, Results
# from accessible_typing_test.settings_dialog import SettingsDialog
# from accessible_typing_test.typing_dialog import TypingDialog


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
		self.message = wx.StaticText(
			self.panel,
			id=wx.ID_ANY,
			label="Typing test program by Thomas Stivers."
			)
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
		self.notebook.AddPage(self.tests_panel, "Tests")
		self.users_panel = UsersPanel(self.notebook)
		self.notebook.AddPage(self.users_panel, "Users")

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
		self.Bind(wx.EVT_BUTTON, self.onExit, self.exit_button)

		#Give the frame a status bar.
		self.status_bar = wx.StatusBar(self, wx.ID_ANY)
		self.status_bar.SetStatusText(
			f"{self.results_panel.test_list.GetItemCount()} test results recorded.")
		self.SetStatusBar(self.status_bar)
		self.SetMenuBar(self.menu_bar)
		# The table of accelerator keys is part of the TypingMenuBar object, so it is
		# included from there.
		self.SetAcceleratorTable(self.menu_bar.accelerator_table)
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
		user_sizer = wx.BoxSizer(wx.HORIZONTAL)
		grid_sizer = wx.GridSizer(rows=4, cols=2, hgap=5, vgap=5)
		user_sizer.Add(self.user_name_label, proportion=0, flag=wx.ALIGN_RIGHT)
		user_sizer.Add(self.user_name, proportion=1, flag=wx.EXPAND)
		grid_sizer.Add(user_sizer, proportion=1, flag=wx.EXPAND) # Row 2 column 1
		sizer.Add(
			self.message,
			proportion=0,
			border=5,
			flag=wx.ALIGN_CENTER_HORIZONTAL
			)
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
		config.Write("userName", self.user_name.GetValue())
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
	app.SetTopWindow(frame)
	if not app.IsMainLoopRunning(): app.MainLoop()
	logging.info("Shutting down.")
	return

if __name__ == "__main__":
	main()
