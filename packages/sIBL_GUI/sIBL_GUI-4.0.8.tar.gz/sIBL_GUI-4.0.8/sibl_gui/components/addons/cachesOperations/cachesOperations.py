#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**cachesOperations.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Defines the :class:`CachesOperations` Component Interface class.

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
from PyQt4.QtGui import QGridLayout

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.exceptions
import foundations.io
import foundations.verbose
import foundations.walkers
import sibl_gui.exceptions
import umbra.exceptions
from manager.qwidgetComponent import QWidgetComponentFactory
from umbra.globals.constants import Constants
from umbra.globals.runtimeGlobals import RuntimeGlobals
from umbra.globals.uiConstants import UiConstants

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER", "COMPONENT_UI_FILE", "CachesOperations"]

LOGGER = foundations.verbose.installLogger()

COMPONENT_UI_FILE = os.path.join(os.path.dirname(__file__), "ui", "Caches_Operations.ui")

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class CachesOperations(QWidgetComponentFactory(uiFile=COMPONENT_UI_FILE)):
	"""
	| Defines the :mod:`sibl_gui.components.addons.cachesOperations.cachesOperations` Component Interface class.
	| It provides various methods to operate on the images caches.
	"""

	def __init__(self, parent=None, name=None, *args, **kwargs):
		"""
		Initializes the class.

		:param parent: Object parent.
		:type parent: QObject
		:param name: Component name.
		:type name: unicode
		:param \*args: Arguments.
		:type \*args: \*
		:param \*\*kwargs: Keywords arguments.
		:type \*\*kwargs: \*\*
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		super(CachesOperations, self).__init__(parent, name, *args, **kwargs)

		# --- Setting class attributes. ---
		self.deactivatable = True

		self.__engine = None

		self.__scriptEditor = None
		self.__preferencesManager = None

	#******************************************************************************************************************
	#***	Attributes properties.
	#******************************************************************************************************************
	@property
	def engine(self):
		"""
		Property for **self.__engine** attribute.

		:return: self.__engine.
		:rtype: QObject
		"""

		return self.__engine

	@engine.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def engine(self, value):
		"""
		Setter for **self.__engine** attribute.

		:param value: Attribute value.
		:type value: QObject
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "engine"))

	@engine.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def engine(self):
		"""
		Deleter for **self.__engine** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "engine"))

	@property
	def scriptEditor(self):
		"""
		Property for **self.__scriptEditor** attribute.

		:return: self.__scriptEditor.
		:rtype: QWidget
		"""

		return self.__scriptEditor

	@scriptEditor.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def scriptEditor(self, value):
		"""
		Setter for **self.__scriptEditor** attribute.

		:param value: Attribute value.
		:type value: QWidget
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "scriptEditor"))

	@scriptEditor.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def scriptEditor(self):
		"""
		Deleter for **self.__scriptEditor** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "scriptEditor"))

	@property
	def preferencesManager(self):
		"""
		Property for **self.__preferencesManager** attribute.

		:return: self.__preferencesManager.
		:rtype: QWidget
		"""

		return self.__preferencesManager

	@preferencesManager.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def preferencesManager(self, value):
		"""
		Setter for **self.__preferencesManager** attribute.

		:param value: Attribute value.
		:type value: QWidget
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "preferencesManager"))

	@preferencesManager.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def preferencesManager(self):
		"""
		Deleter for **self.__preferencesManager** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "preferencesManager"))

	#******************************************************************************************************************
	#***	Class methods.
	#******************************************************************************************************************
	def activate(self, engine):
		"""
		Activates the Component.

		:param engine: Engine to attach the Component to.
		:type engine: QObject
		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Activating '{0}' Component.".format(self.__class__.__name__))

		self.__engine = engine

		self.__scriptEditor = self.__engine.componentsManager["factory.scriptEditor"]
		self.__preferencesManager = self.__engine.componentsManager["factory.preferencesManager"]

		self.activated = True
		return True

	def deactivate(self):
		"""
		Deactivates the Component.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Deactivating '{0}' Component.".format(self.__class__.__name__))

		self.__engine = None

		self.__scriptEditor = None
		self.__preferencesManager = None

		self.activated = False
		return True

	def initializeUi(self):
		"""
		Initializes the Component ui.
		
		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Initializing '{0}' Component ui.".format(self.__class__.__name__))

		# Signals / Slots.
		self.Output_Caches_Metrics_pushButton.clicked.connect(self.__Output_Caches_Metrics_pushButton__clicked)
		self.Clear_Thumbnails_Cache_pushButton.clicked.connect(self.__Clear_Thumbnails_Cache_pushButton__clicked)
		self.Clear_Images_Caches_pushButton.clicked.connect(self.__Clear_Images_Caches_pushButton__clicked)

		self.initializedUi = True
		return True

	def uninitializeUi(self):
		"""
		Uninitializes the Component ui.
		
		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Uninitializing '{0}' Component ui.".format(self.__class__.__name__))

		# Signals / Slots.
		self.Output_Caches_Metrics_pushButton.clicked.disconnect(self.__Output_Caches_Metrics_pushButton__clicked)
		self.Clear_Thumbnails_Cache_pushButton.clicked.disconnect(self.__Clear_Thumbnails_Cache_pushButton__clicked)
		self.Clear_Images_Caches_pushButton.clicked.disconnect(self.__Clear_Images_Caches_pushButton__clicked)

		self.initializedUi = False
		return True

	def addWidget(self):
		"""
		Adds the Component Widget to the engine.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Adding '{0}' Component Widget.".format(self.__class__.__name__))

		self.__preferencesManager.Others_Preferences_gridLayout.addWidget(self.Caches_Operations_groupBox)

		return True

	def removeWidget(self):
		"""
		Removes the Component Widget from the engine.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Removing '{0}' Component Widget.".format(self.__class__.__name__))

		self.__preferencesManager.findChild(QGridLayout, "Others_Preferences_gridLayout").removeWidget(self)
		self.Caches_Operations_groupBox.setParent(None)

		return True

	def __Clear_Thumbnails_Cache_pushButton__clicked(self, checked):
		"""
		Defines the slot triggered by **Thumbnails_Cache_pushButton** Widget when clicked.

		:param checked: Checked state.
		:type checked: bool
		"""

		self.clearThumbnailsCache()

	def __Clear_Images_Caches_pushButton__clicked(self, checked):
		"""
		Defines the slot triggered by **Clear_Images_Caches_pushButton** Widget when clicked.

		:param checked: Checked state.
		:type checked: bool
		"""

		self.clearImagesCaches()

	def __Output_Caches_Metrics_pushButton__clicked(self, checked):
		"""
		Defines the slot triggered by **Output_Caches_Metrics_pushButton** Widget when clicked.

		:param checked: Checked state.
		:type checked: bool
		"""

		self.outputCachesMetrics()
		self.__scriptEditor.restoreDevelopmentLayout()

	def outputCachesMetrics(self):
		"""
		Outputs caches metrics.

		:return: Method success.
		:rtype: bool
		"""

		separator = "{0}".format(Constants.loggingSeparators.replace("*", "-"))
		metrics = dict.fromkeys(UiConstants.thumbnailsSizes, 0)
		for type, cache in self.__engine.imagesCaches.iteritems():
			LOGGER.info(separator)
			LOGGER.info("{0} | Metrics for '{1}' '{2}' images memory cache:".format(self.__class__.__name__,
																			Constants.applicationName, type))
			cacheMetrics = cache.getMetrics().content
			LOGGER.info("{0} | \tCached graphics items count: '{1}'".format(self.__class__.__name__, len(cacheMetrics)))
			for path, data in sorted(cache.getMetrics().content.iteritems()):
				LOGGER.info("{0} | \t\t'{1}':".format(self.__class__.__name__, path))
				for size, data in sorted(data.iteritems()):
					if data is not None:
						metrics[size] += 1
						path, imageInformationsHeader = data
						LOGGER.info("{0} | \t\t\t'{1}': '{2}':".format(self.__class__.__name__, size, path))
						LOGGER.info("{0} | \t\t\t\tSize: {1}x{2} px".format(self.__class__.__name__,
																		imageInformationsHeader.width,
																		imageInformationsHeader.height))
						LOGGER.info("{0} | \t\t\t\tBpp: {1} bit".format(self.__class__.__name__,
																	imageInformationsHeader.bpp / 4))
					else:
						LOGGER.info("{0} | \t\t\t'{1}': '{2}'.".format(self.__class__.__name__, size, Constants.nullObject))
			LOGGER.info(separator)

		LOGGER.info(separator)
		LOGGER.info("{0} | Metrics for 'Application' thumbnails disk cache:".format(self.__class__.__name__))
		for size, count in sorted(metrics.iteritems()):
			LOGGER.info("{0} | \t\t{1} '{2}' registered thumbnails.".format(self.__class__.__name__, count, size))
		thumbnails = list(foundations.walkers.filesWalker(RuntimeGlobals.thumbnailsCacheDirectory))
		LOGGER.info("{0} | \t\t{1} files in disk cache directory.".format(self.__class__.__name__, len(thumbnails)))
		LOGGER.info(separator)
		return True

	@foundations.exceptions.handleExceptions(umbra.exceptions.notifyExceptionHandler,
											sibl_gui.exceptions.CacheOperationError)
	def clearThumbnailsCache(self):
		"""
		Clears the thumbnails cache.

		:return: Method success.
		:rtype: bool
		"""

		thumbnails = list(foundations.walkers.filesWalker(RuntimeGlobals.thumbnailsCacheDirectory))

		success = True
		for thumbnail in thumbnails:
			success *= foundations.io.remove(thumbnail)

		if success:
			self.__engine.notificationsManager.notify(
			"{0} | Thumbnails cache has been successfully cleared!".format(self.__class__.__name__))
			return True
		else:
			raise sibl_gui.exceptions.CacheOperationError(
				"{0} | Exception raised while attempting to clear thumbnails cache!".format(
				self.__class__.__name__))

	@foundations.exceptions.handleExceptions(umbra.exceptions.notifyExceptionHandler,
											sibl_gui.exceptions.CacheOperationError)
	def clearImagesCaches(self):
		"""
		Clears the images caches.

		:return: Method success.
		:rtype: bool
		"""

		success = True
		for cache in self.__engine.imagesCaches.itervalues():
			success *= cache.flushContent()

		if success:
			self.__engine.notificationsManager.notify(
			"{0} | Images caches have been successfully cleared!".format(self.__class__.__name__))
			return True
		else:
			raise sibl_gui.exceptions.CacheOperationError(
				"{0} | Exception raised while attempting to clear images caches!".format(
				self.__class__.__name__))
