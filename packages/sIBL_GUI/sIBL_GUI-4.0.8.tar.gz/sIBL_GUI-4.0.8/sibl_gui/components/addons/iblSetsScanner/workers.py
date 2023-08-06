#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**models.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Defines the :class:`sibl_gui.components.addons.iblSetsScanner.iblSetsScanner.IblSetsScanner` 
	Component Interface class Workers.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
import os
import re
from PyQt4.QtCore import QThread
from PyQt4.QtCore import pyqtSignal

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.common
import foundations.exceptions
import foundations.strings
import foundations.verbose
import foundations.walkers
import sibl_gui.components.core.database.operations
from sibl_gui.components.core.database.types import IblSet

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER", "IblSetsScanner_worker"]

LOGGER = foundations.verbose.installLogger()

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class IblSetsScanner_worker(QThread):
	"""
	Defines a `QThread <http://doc.qt.nokia.com/qthread.html>`_ subclass used to retrieve
	new Ibl Sets from Database registered directories parents.
	"""

	# Custom signals definitions.
	iblSetsRetrieved = pyqtSignal(list)
	"""
	This signal is emited by the :class:`IblSetsScanner_worker` class when new Ibl Sets are retrieved. ( pyqtSignal )
	
	:return: New Ibl Sets.
	:rtype: list
	"""

	def __init__(self, parent):
		"""
		Initializes the class.

		:param parent: Object parent.
		:type parent: QObject
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		QThread.__init__(self, parent)

		# --- Setting class attributes. ---
		self.__container = parent

		self.__databaseSession = sibl_gui.components.core.database.operations.createSession()

		self.__newIblSets = None

		self.__extension = "ibl"

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
	def databaseSession(self):
		"""
		Property for **self.__databaseSession** attribute.

		:return: self.__databaseSession.
		:rtype: object
		"""

		return self.__databaseSession

	@databaseSession.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def databaseSession(self, value):
		"""
		Setter for **self.__databaseSession** attribute.

		:param value: Attribute value.
		:type value: object
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "databaseSession"))

	@databaseSession.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def databaseSession(self):
		"""
		Deleter for **self.__databaseSession** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "databaseSession"))

	@property
	def extension(self):
		"""
		Property for **self.__extension** attribute.

		:return: self.__extension.
		:rtype: unicode
		"""

		return self.__extension

	@extension.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def extension(self, value):
		"""
		Setter for **self.__extension** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "extension"))

	@extension.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def extension(self):
		"""
		Deleter for **self.__extension** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "extension"))

	@property
	def newIblSets(self):
		"""
		Property for **self.__newIblSets** attribute.

		:return: self.__newIblSets.
		:rtype: list
		"""

		return self.__newIblSets

	@newIblSets.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def newIblSets(self, value):
		"""
		Setter for **self.__newIblSets** attribute.

		:param value: Attribute value.
		:type value: list
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "newIblSets"))

	@newIblSets.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def newIblSets(self):
		"""
		Deleter for **self.__newIblSets** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "newIblSets"))

	#******************************************************************************************************************
	#***	Class methods.
	#******************************************************************************************************************
	def run(self):
		"""
		Reimplements the :meth:`QThread.run` method.
		"""

		self.scanIblSetsDirectories()

	def scanIblSetsDirectories(self):
		"""
		Scans Ibl Sets directories.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.info("{0} | Scanning Ibl Sets directories for new Ibl Sets!".format(self.__class__.__name__))

		self.__newIblSets = []
		paths = [foundations.common.getFirstItem(path) for path in self.__databaseSession.query(IblSet.path).all()]
		directories = set((os.path.normpath(os.path.join(os.path.dirname(path), "..")) for path in paths))
		for directory in directories:
			if foundations.common.pathExists(directory):
				for path in foundations.walkers.filesWalker(directory, ("\.{0}$".format(self.__extension),), ("\._",)):
					if not sibl_gui.components.core.database.operations.filterIblSets("^{0}$".format(re.escape(path)),
																					"path",
																					session=self.__databaseSession):
						self.__newIblSets.append(path)
			else:
				LOGGER.warning("!> {0} | '{1}' directory doesn't exists and won't be scanned for new Ibl Sets!".format(self.__class__.__name__, directory))

		self.__databaseSession.close()

		LOGGER.info("{0} | Scanning done!".format(self.__class__.__name__))
		self.__newIblSets and self.iblSetsRetrieved.emit(self.__newIblSets)
		return True
