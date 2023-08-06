#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**views.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Defines the :class:`sibl_gui.components.core.templatesOutliner.templatesOutliner.TemplatesOutliner`
	Component Interface class Views.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QAbstractItemView

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.namespace
import foundations.exceptions
import foundations.strings
import foundations.verbose
import sibl_gui.ui.views

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER", "Templates_QTreeView"]

LOGGER = foundations.verbose.installLogger()

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class Templates_QTreeView(sibl_gui.ui.views.Abstract_QTreeView):
	"""
	Defines the view for Database Collections.
	"""

	def __init__(self, parent, model=None, readOnly=False, message=None):
		"""
		Initializes the class.

		:param parent: Object parent.
		:type parent: QObject
		:param model: Model.
		:type model: QObject
		:param readOnly: View is read only.
		:type readOnly: bool
		:param message: View default message when Model is empty.
		:type message: unicode
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		sibl_gui.ui.views.Abstract_QTreeView.__init__(self, parent, model, readOnly, message)

		# --- Setting class attributes. ---
		self.__container = parent

		self.__treeViewIndentation = 15

		Templates_QTreeView.__initializeUi(self)

	#******************************************************************************************************************
	#***	Attributes properties.
	#******************************************************************************************************************
	@property
	def container(self):
		"""
		Property for **self.__container** attribute.

		:return: self.__container.
		:rtype: QObject
		"""

		return self.__container

	@container.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def container(self, value):
		"""
		Setter for **self.__container** attribute.

		:param value: Attribute value.
		:type value: QObject
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "container"))

	@container.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def container(self):
		"""
		Deleter for **self.__container** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "container"))

	@property
	def treeViewIndentation(self):
		"""
		Property for **self.__treeViewIndentation** attribute.

		:return: self.__treeViewIndentation.
		:rtype: int
		"""

		return self.__treeViewIndentation

	@treeViewIndentation.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def treeViewIndentation(self, value):
		"""
		Setter for **self.__treeViewIndentation** attribute.

		:param value: Attribute value.
		:type value: int
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "treeViewIndentation"))

	@treeViewIndentation.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def treeViewIndentation(self):
		"""
		Deleter for **self.__treeViewIndentation** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "treeViewIndentation"))

	#******************************************************************************************************************
	#***	Class methods.
	#******************************************************************************************************************
	def __initializeUi(self):
		"""
		Initializes the Widget ui.
		"""

		self.setAutoScroll(True)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setIndentation(self.__treeViewIndentation)
		self.setDragDropMode(QAbstractItemView.DragOnly)

		self.setSortingEnabled(True)
		self.sortByColumn(0, Qt.AscendingOrder)

		self.__setDefaultUiState()

		# Signals / Slots.
		self.model().modelReset.connect(self.__setDefaultUiState)

	def __setDefaultUiState(self):
		"""
		Sets the Widget default ui state.
		"""

		LOGGER.debug("> Setting default View state!")

		if not self.model():
			return

		self.expandAll()

		for column in range(len(self.model().horizontalHeaders)):
			self.resizeColumnToContents(column)

	def storeModelSelection(self):
		"""
		Stores the Model selection.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Storing Model selection!")

		self.modelSelection = {"Templates" : [], "Collections" : [], "Softwares" : []}
		for node in self.getSelectedNodes():
			if node.family == "Template":
				self.modelSelection["Templates"].append(node.id.value)
			elif node.family == "Collection":
				self.modelSelection["Collections"].append(node.id.value)
			elif node.family == "Software":
				self.modelSelection["Softwares"].append(foundations.namespace.setNamespace(node.parent.id.value, node.name))
		return True

	def restoreModelSelection(self):
		"""
		Restores the Model selection.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Restoring Model selection!")

		if not self.modelSelection:
			return False

		selection = self.modelSelection.get("Templates", None) or self.modelSelection.get("Collections", None) or \
		self.modelSelection.get("Softwares", None)
		if not selection:
			return False

		indexes = []
		for node in foundations.walkers.nodesWalker(self.model().rootNode):
			if node.family == "Template":
				self.modelSelection.get("Templates", None) and node.id.value in self.modelSelection["Templates"] and \
				indexes.append(self.model().getNodeIndex(node))
			elif node.family == "Collection":
				self.modelSelection.get("Collections", None) and node.id.value in self.modelSelection["Collections"] and \
				indexes.append(self.model().getNodeIndex(node))
			elif node.family == "Software":
				for item in self.modelSelection["Softwares"]:
					parentId, name = item.split(foundations.namespace.NAMESPACE_SPLITTER)
					for collection in self.model().rootNode.children:
						if not foundations.strings.toString(collection.id.value) == parentId:
							continue

						for software in collection.children:
							if software.name == name:
								indexes.append(self.model().getNodeIndex(software))

		return self.selectIndexes(indexes)
