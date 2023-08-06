#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**views.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Defines the Application views classes.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.exceptions
import foundations.verbose
import foundations.walkers
import umbra.ui.views

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER",
			"Mixin_AbstractView"
			"Abstract_QListView",
			"Abstract_QTreeView"]

LOGGER = foundations.verbose.installLogger()

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class Mixin_AbstractView(object):
	"""
	Defines a mixin used to bring common capabilities in Application Views classes.
	"""

	def __init__(self, model=None):
		"""
		Initializes the class.

		:param model: Model.
		:type model: QObject
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		# --- Setting class attributes. ---
		self.__modelSelection = {"Default" : []}

		Mixin_AbstractView.setModel(self, model)

	#******************************************************************************************************************
	#***	Attributes properties.
	#******************************************************************************************************************
	@property
	def modelSelection(self):
		"""
		Property for **self.__modelSelection** attribute.

		:return: self.__modelSelection.
		:rtype: dict
		"""

		return self.__modelSelection

	@modelSelection.setter
	@foundations.exceptions.handleExceptions(AssertionError)
	def modelSelection(self, value):
		"""
		Setter for **self.__modelSelection** attribute.

		:param value: Attribute value.
		:type value: dict
		"""

		if value is not None:
			assert type(value) is dict, "'{0}' attribute: '{1}' type is not 'dict'!".format("modelSelection", value)
			for key, element in value.iteritems():
				assert type(key) is unicode, "'{0}' attribute: '{1}' type is not 'unicode'!".format(
				"modelSelection", key)
				assert type(element) is list, "'{0}' attribute: '{1}' type is not 'list'!".format("modelSelection",
																								element)
		self.__modelSelection = value

	@modelSelection.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def modelSelection(self):
		"""
		Deleter for **self.__modelSelection** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "modelSelection"))

	#******************************************************************************************************************
	#***	Class methods.
	#******************************************************************************************************************
	def setModel(self, model):
		"""
		Reimplements the **umbra.ui.views.Abstract_QListView.setModel** method.
		
		:param model: Model to set.
		:type model: QObject
		"""

		if not model:
			return

		LOGGER.debug("> Setting '{0}' model.".format(model))

		super(type(self), self).setModel(model)

		# Signals / Slots.
		self.model().modelAboutToBeReset.connect(self.__model__modelAboutToBeReset)
		self.model().modelReset.connect(self.__model__modelReset)

	def __model__modelAboutToBeReset(self):
		"""
		Defines the slot triggered by the Model when about to be reset.
		"""

		self.storeModelSelection()

	def __model__modelReset(self):
		"""
		Defines the slot triggered by the Model when reset.
		"""

		self.restoreModelSelection()

	def storeModelSelection(self):
		"""
		Stores the Model selection.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Storing Model selection!")

		self.modelSelection = {"Default" : []}
		for node in self.getSelectedNodes():
			self.modelSelection["Default"].append(node.id.value)
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

		selection = self.modelSelection.get("Default", None)
		if not selection:
			return False

		indexes = []
		for node in foundations.walkers.nodesWalker(self.model().rootNode):
			node.id.value in selection and indexes.append(self.model().getNodeIndex(node))

		return self.selectViewIndexes(indexes)

class Abstract_QListView(umbra.ui.views.Abstract_QListView, Mixin_AbstractView):
	"""
	Defines the base class used by others Application Views classes.
	"""

	def __init__(self, parent=None, model=None, readOnly=False, message=None):
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

		umbra.ui.views.Abstract_QListView.__init__(self, parent, readOnly, message)
		Mixin_AbstractView.__init__(self, model)

class Abstract_QTreeView(umbra.ui.views.Abstract_QTreeView, Mixin_AbstractView):
	"""
	Defines the base class used by others Application Views classes.
	"""

	def __init__(self, parent=None, model=None, readOnly=False, message=None):
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

		umbra.ui.views.Abstract_QTreeView.__init__(self, parent, readOnly, message)
		Mixin_AbstractView.__init__(self, model)

