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

from accessible_typing_test.lev import levenshteinDistance
from accessible_typing_test.dialogs import *
from accessible_typing_test.menus import *
from accessible_typing_test.panels import *
import accessible_typing_test.main as main
from accessible_typing_test.results_database import session_scope, Sentences, Results
# from accessible_typing_test.typing_dialog import TypingDialog
# from accessible_typing_test.menus import TypingMenuBar

__all__ = ["main", "TypingDialog", "ResultsDatabase", "TypingMenuBar"]
__version__ = "1.0"