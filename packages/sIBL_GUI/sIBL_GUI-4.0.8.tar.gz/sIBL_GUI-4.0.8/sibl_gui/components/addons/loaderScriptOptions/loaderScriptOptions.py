#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**loaderScriptOptions.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Defines the :class:`LoaderScriptOptions` Component Interface class.

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
import sys
if sys.version_info[:2] <= (2, 6):
	from ordereddict import OrderedDict
else:
	from collections import OrderedDict
from PyQt4.QtCore import QString
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QDoubleSpinBox
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPalette

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.common
import foundations.exceptions
import foundations.io
import foundations.parsers
import foundations.strings
import foundations.verbose
import umbra.exceptions
import umbra.ui.common
from foundations.parsers import SectionsFileParser
from manager.qwidgetComponent import QWidgetComponentFactory
from sibl_gui.components.addons.loaderScriptOptions.views import TemplatesAttributes_QTableWidget
from umbra.globals.constants import Constants
from umbra.ui.widgets.variable_QPushButton import Variable_QPushButton

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER", "COMPONENT_UI_FILE", "LoaderScriptOptions"]

LOGGER = foundations.verbose.installLogger()

COMPONENT_UI_FILE = os.path.join(os.path.dirname(__file__), "ui", "Loader_Script_Options.ui")

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class LoaderScriptOptions(QWidgetComponentFactory(uiFile=COMPONENT_UI_FILE)):
	"""
	| Definesthe :mod:`sibl_gui.components.addons.loaderScriptOptions.loaderScriptOptions` Component Interface class.
	| It provides override keys on request for the :mod:`sibl_gui.components.addons.loaderScript.loaderScript` Component.
	| It exposes Templates files **Common Attributes** and **Additional Attributes** sections so that
		the user can configure the behavior of the Loader Script.
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

		super(LoaderScriptOptions, self).__init__(parent, name, *args, **kwargs)

		# --- Setting class attributes. ---
		self.deactivatable = True

		self.__dockArea = 2

		self.__engine = None

		self.__templatesOutliner = None
		self.__loaderScript = None

		self.__views = None
		self.__commonView = None
		self.__additionalView = None

		self.__namespaceSplitter = "|"

		self.__templatesSettingsDirectory = "templates/"
		self.__templateSettingsFile = None
		self.__templateCommonAttributesSection = "Common Attributes"
		self.__templateAdditionalAttributesSection = "Additional Attributes"
		self.__templateScriptSection = "Script"
		self.__optionsToolboxesHeaders = ["Value"]

		self.__uiLightGrayColor = QColor(240, 240, 240)
		self.__uiDarkGrayColor = QColor(160, 160, 160)

		self.__enumSplitter = ";"

	#******************************************************************************************************************
	#***	Attributes properties.
	#******************************************************************************************************************
	@property
	def dockArea(self):
		"""
		Property for **self.__dockArea** attribute.

		:return: self.__dockArea.
		:rtype: int
		"""

		return self.__dockArea

	@dockArea.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def dockArea(self, value):
		"""
		Setter for **self.__dockArea** attribute.

		:param value: Attribute value.
		:type value: int
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "dockArea"))

	@dockArea.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def dockArea(self):
		"""
		Deleter for **self.__dockArea** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "dockArea"))

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
	def templatesOutliner(self):
		"""
		Property for **self.__templatesOutliner** attribute.

		:return: self.__templatesOutliner.
		:rtype: QWidget
		"""

		return self.__templatesOutliner

	@templatesOutliner.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templatesOutliner(self, value):
		"""
		Setter for **self.__templatesOutliner** attribute.

		:param value: Attribute value.
		:type value: QWidget
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "templatesOutliner"))

	@templatesOutliner.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templatesOutliner(self):
		"""
		Deleter for **self.__templatesOutliner** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "templatesOutliner"))

	@property
	def loaderScript(self):
		"""
		Property for **self.__loaderScript** attribute.

		:return: self.__loaderScript.
		:rtype: QWidget
		"""

		return self.__loaderScript

	@loaderScript.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def loaderScript(self, value):
		"""
		Setter for **self.__loaderScript** attribute.

		:param value: Attribute value.
		:type value: QWidget
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "loaderScript"))

	@loaderScript.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def loaderScript(self):
		"""
		Deleter for **self.__loaderScript** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "loaderScript"))

	@property
	def views(self):
		"""
		Property for **self.__views** attribute.

		:return: self.__views.
		:rtype: tuple
		"""

		return self.__views

	@views.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def views(self, value):
		"""
		Setter for **self.__views** attribute.

		:param value: Attribute value.
		:type value: tuple
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "views"))

	@views.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def views(self):
		"""
		Deleter for **self.__views** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "views"))

	@property
	def commonView(self):
		"""
		Property for **self.__commonView** attribute.

		:return: self.__commonView.
		:rtype: QListView
		"""

		return self.__commonView

	@commonView.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def commonView(self, value):
		"""
		Setter for **self.__commonView** attribute.

		:param value: Attribute value.
		:type value: QListView
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "commonView"))

	@commonView.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def commonView(self):
		"""
		Deleter for **self.__commonView** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "view"))

	@property
	def additionalView(self):
		"""
		Property for **self.__additionalView** attribute.

		:return: self.__additionalView.
		:rtype: QListView
		"""

		return self.__additionalView

	@additionalView.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def additionalView(self, value):
		"""
		Setter for **self.__additionalView** attribute.

		:param value: Attribute value.
		:type value: QListView
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "additionalView"))

	@additionalView.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def additionalView(self):
		"""
		Deleter for **self.__additionalView** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "view"))

	@property
	def namespaceSplitter(self):
		"""
		Property for **self.__namespaceSplitter** attribute.

		:return: self.__namespaceSplitter.
		:rtype: unicode
		"""

		return self.__namespaceSplitter

	@namespaceSplitter.setter
	@foundations.exceptions.handleExceptions(AssertionError)
	def namespaceSplitter(self, value):
		"""
		Setter for **self.__namespaceSplitter** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		if value is not None:
			assert type(value) is unicode, "'{0}' attribute: '{1}' type is not 'unicode'!".format(
			"namespaceSplitter", value)
			assert len(value) == 1, "'{0}' attribute: '{1}' has multiples characters!".format(
			"namespaceSplitter", value)
			assert not re.search(r"\w", value), "'{0}' attribute: '{1}' is an alphanumeric character!".format(
			"namespaceSplitter", value)
		self.__namespaceSplitter = value

	@namespaceSplitter.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def namespaceSplitter(self):
		"""
		Deleter for **self.__namespaceSplitter** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "namespaceSplitter"))

	@property
	def templatesSettingsDirectory(self):
		"""
		Property for **self.__templatesSettingsDirectory** attribute.

		:return: self.__templatesSettingsDirectory.
		:rtype: unicode
		"""

		return self.__templatesSettingsDirectory

	@templatesSettingsDirectory.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templatesSettingsDirectory(self, value):
		"""
		Setter for **self.__templatesSettingsDirectory** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "templatesSettingsDirectory"))

	@templatesSettingsDirectory.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templatesSettingsDirectory(self):
		"""
		Deleter for **self.__templatesSettingsDirectory** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "templatesSettingsDirectory"))

	@property
	def templateSettingsFile(self):
		"""
		Property for **self.__templateSettingsFile** attribute.

		:return: self.__templateSettingsFile.
		:rtype: unicode
		"""

		return self.__templateSettingsFile

	@templateSettingsFile.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateSettingsFile(self, value):
		"""
		Setter for **self.__templateSettingsFile** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "templateSettingsFile"))

	@templateSettingsFile.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateSettingsFile(self):
		"""
		Deleter for **self.__templateSettingsFile** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "templateSettingsFile"))

	@property
	def templateCommonAttributesSection(self):
		"""
		Property for **self.__templateCommonAttributesSection** attribute.

		:return: self.__templateCommonAttributesSection.
		:rtype: unicode
		"""

		return self.__templateCommonAttributesSection

	@templateCommonAttributesSection.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateCommonAttributesSection(self, value):
		"""
		Setter for **self.__templateCommonAttributesSection** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "templateCommonAttributesSection"))

	@templateCommonAttributesSection.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateCommonAttributesSection(self):
		"""
		Deleter for **self.__templateCommonAttributesSection** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "templateCommonAttributesSection"))

	@property
	def templateAdditionalAttributesSection(self):
		"""
		Property for **self.__templateAdditionalAttributesSection** attribute.

		:return: self.__templateAdditionalAttributesSection.
		:rtype: unicode
		"""

		return self.__templateAdditionalAttributesSection

	@templateAdditionalAttributesSection.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateAdditionalAttributesSection(self, value):
		"""
		Setter for **self.__templateAdditionalAttributesSection** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "templateAdditionalAttributesSection"))

	@templateAdditionalAttributesSection.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateAdditionalAttributesSection(self):
		"""
		Deleter for **self.__templateAdditionalAttributesSection** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(
		self.__class__.__name__, "templateAdditionalAttributesSection"))

	@property
	def templateScriptSection(self):
		"""
		Property for **self.__templateScriptSection** attribute.

		:return: self.__templateScriptSection.
		:rtype: unicode
		"""

		return self.__templateScriptSection

	@templateScriptSection.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateScriptSection(self, value):
		"""
		Setter for **self.__templateScriptSection** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "templateScriptSection"))

	@templateScriptSection.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def templateScriptSection(self):
		"""
		Deleter for **self.__templateScriptSection** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "templateScriptSection"))

	@property
	def optionsToolboxesHeaders(self):
		"""
		Property for **self.__optionsToolboxesHeaders** attribute.

		:return: self.__optionsToolboxesHeaders.
		:rtype: list
		"""

		return self.__optionsToolboxesHeaders

	@optionsToolboxesHeaders.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def optionsToolboxesHeaders(self, value):
		"""
		Setter for **self.__optionsToolboxesHeaders** attribute.

		:param value: Attribute value.
		:type value: list
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "optionsToolboxesHeaders"))

	@optionsToolboxesHeaders.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def optionsToolboxesHeaders(self):
		"""
		Deleter for **self.__optionsToolboxesHeaders** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "optionsToolboxesHeaders"))

	@property
	def uiLightGrayColor(self):
		"""
		Property for **self.__uiLightGrayColor** attribute.

		:return: self.__uiLightGrayColor.
		:rtype: QColor
		"""

		return self.__uiLightGrayColor

	@uiLightGrayColor.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def uiLightGrayColor(self, value):
		"""
		Setter for **self.__uiLightGrayColor** attribute.

		:param value: Attribute value.
		:type value: QColor
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "uiLightGrayColor"))

	@uiLightGrayColor.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def uiLightGrayColor(self):
		"""
		Deleter for **self.__uiLightGrayColor** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "uiLightGrayColor"))

	@property
	def uiDarkGrayColor(self):
		"""
		Property for **self.__uiDarkGrayColor** attribute.

		:return: self.__uiDarkGrayColor.
		:rtype: QColor
		"""

		return self.__uiDarkGrayColor

	@uiDarkGrayColor.setter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def uiDarkGrayColor(self, value):
		"""
		Setter for **self.__uiDarkGrayColor** attribute.

		:param value: Attribute value.
		:type value: QColor
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is read only!".format(self.__class__.__name__, "uiDarkGrayColor"))

	@uiDarkGrayColor.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def uiDarkGrayColor(self):
		"""
		Deleter for **self.__uiDarkGrayColor** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "uiDarkGrayColor"))

	@property
	def enumSplitter(self):
		"""
		Property for **self.__enumSplitter** attribute.

		:return: self.__enumSplitter.
		:rtype: unicode
		"""

		return self.__enumSplitter

	@enumSplitter.setter
	@foundations.exceptions.handleExceptions(AssertionError)
	def enumSplitter(self, value):
		"""
		Setter for **self.__enumSplitter** attribute.

		:param value: Attribute value.
		:type value: unicode
		"""

		if value is not None:
			assert type(value) is unicode, "'{0}' attribute: '{1}' type is not 'unicode'!".format(
			"enumSplitter", value)
			assert len(value) == 1, "'{0}' attribute: '{1}' has multiples characters!".format("enumSplitter", value)
			assert not re.search(r"\w", value), "'{0}' attribute: '{1}' is an alphanumeric character!".format(
			"enumSplitter", value)
		self.__enumSplitter = value

	@enumSplitter.deleter
	@foundations.exceptions.handleExceptions(foundations.exceptions.ProgrammingError)
	def enumSplitter(self):
		"""
		Deleter for **self.__enumSplitter** attribute.
		"""

		raise foundations.exceptions.ProgrammingError(
		"{0} | '{1}' attribute is not deletable!".format(self.__class__.__name__, "enumSplitter"))

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

		self.__templatesOutliner = self.__engine.componentsManager["core.templatesOutliner"]
		self.__loaderScript = self.__engine.componentsManager["addons.loaderScript"]

		self.__templatesSettingsDirectory = os.path.join(self.__engine.userApplicationDataDirectory,
														Constants.settingsDirectory,
														self.__templatesSettingsDirectory)
		not foundations.common.pathExists(self.__templatesSettingsDirectory) and \
		os.makedirs(self.__templatesSettingsDirectory)
		self.__templateSettingsFile = None

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

		self.__templatesOutliner = None
		self.__loaderScript = None

		self.__templatesSettingsDirectory = os.path.basename(os.path.abspath(self.__templatesSettingsDirectory))
		self.__templateSettingsFile = None

		self.activated = False
		return True

	def initializeUi(self):
		"""
		Initializes the Component ui.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Initializing '{0}' Component ui.".format(self.__class__.__name__))

		umbra.ui.common.setToolBoxHeight(self.Loader_Script_Options_toolBox)

		self.Common_Attributes_tableWidget.setParent(None)
		self.Common_Attributes_tableWidget = TemplatesAttributes_QTableWidget(self, message="No Attributes to view!")
		self.Common_Attributes_tableWidget.setObjectName("Common_Attributes_tableWidget")
		self.Common_Attributes_page_gridLayout.addWidget(self.Common_Attributes_tableWidget, 0, 0)
		self.__commonView = self.Common_Attributes_tableWidget

		self.Additional_Attributes_tableWidget.setParent(None)
		self.Additional_Attributes_tableWidget = TemplatesAttributes_QTableWidget(self, message="No Attributes to view!")
		self.Additional_Attributes_tableWidget.setObjectName("Additional_Attributes_tableWidget")
		self.Additional_Attributes_page_gridLayout.addWidget(self.Additional_Attributes_tableWidget, 0, 0)
		self.__additionalView = self.Additional_Attributes_tableWidget

		self.__views = (self.__commonView, self.__additionalView)

		# Signals / Slots.
		self.__templatesOutliner.view.selectionModel().selectionChanged.connect(
		self.__templatesOutliner_view_selectionModel__selectionChanged)

		self.initializedUi = True
		return True

	def uninitializeUi(self):
		"""
		Uninitializes the Component ui.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Uninitializing '{0}' Component ui.".format(self.__class__.__name__))

		self.__views = None
		self.__commonView = None
		self.__additionalView = None

		# Signals / Slots.
		self.__templatesOutliner.view.selectionModel().selectionChanged.disconnect(
		self.__templatesOutliner_view_selectionModel__selectionChanged)

		self.initializedUi = False
		return True

	def addWidget(self):
		"""
		Adds the Component Widget to the engine.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Adding '{0}' Component Widget.".format(self.__class__.__name__))

		self.__engine.addDockWidget(Qt.DockWidgetArea(self.__dockArea), self)

		return True

	def removeWidget(self):
		"""
		Removes the Component Widget from the engine.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Removing '{0}' Component Widget.".format(self.__class__.__name__))

		self.__engine.removeDockWidget(self)
		self.setParent(None)

		return True

	@foundations.exceptions.handleExceptions(ValueError)
	def __view_setUi(self, section, view, overrides):
		"""
		Defines and sets the given View.

		:param section: Section attributes.
		:type section: dict
		:param view: Table Widget.
		:type view: QTableWidget
		:param overrides: Attributes overrides.
		:type overrides: dict
		"""

		LOGGER.debug("> Updating '{0}'.".format(view.objectName()))

		view.hide()

		self.__view_clearUi(view)

		view.setRowCount(len(section))
		view.setColumnCount(len(self.__optionsToolboxesHeaders))
		view.horizontalHeader().setStretchLastSection(True)
		view.setHorizontalHeaderLabels(self.__optionsToolboxesHeaders)
		view.horizontalHeader().hide()

		palette = QPalette()
		palette.setColor(QPalette.Base, Qt.transparent)
		view.setPalette(palette)

		verticalHeaderLabels = []
		for row, attribute in enumerate(section):
			LOGGER.debug("> Current attribute: '{0}'.".format(attribute))

			overridesValue = overrides[attribute] if attribute in overrides else None
			LOGGER.debug("> Settings value: '{0}'.".format(overridesValue or Constants.nullObject))

			attributeCompound = foundations.parsers.getAttributeCompound(attribute, section[attribute])
			if attributeCompound.name:
				verticalHeaderLabels.append(attributeCompound.alias)
			else:
				verticalHeaderLabels.append(foundations.strings.getNiceName(attributeCompound.name))

			LOGGER.debug("> Attribute type: '{0}'.".format(attributeCompound.type))
			if attributeCompound.type == "Boolean":
				state = True if int(overridesValue if overridesValue is not None else attributeCompound.value) else False
				item = Variable_QPushButton(self,
						state,
						(self.__uiLightGrayColor, self.__uiDarkGrayColor),
						("True", "False"))
				item.setObjectName("Spread_Sheet_pushButton")
				item.setChecked(state)

				# Signals / Slots.
				item.clicked.connect(self.__view__valueChanged)
			elif attributeCompound.type == "Float":
				item = QDoubleSpinBox()
				item.setMinimum(0)
				item.setMaximum(65535)
				item.setValue(float(overridesValue if overridesValue is not None else attributeCompound.value))

				# Signals / Slots.
				item.valueChanged.connect(self.__view__valueChanged)
			elif attributeCompound.type == "Enum":
				item = QComboBox()
				comboBoxItems = [enumItem.strip() for enumItem in attributeCompound.value.split(self.__enumSplitter)]
				item.addItems(comboBoxItems)
				if overridesValue in comboBoxItems:
					item.setCurrentIndex(comboBoxItems.index(overridesValue))

				# Signals / Slots.
				item.currentIndexChanged.connect(self.__view__valueChanged)
			elif attributeCompound.type == "String":
				item = QLineEdit(QString(overridesValue if overridesValue is not None else attributeCompound.value))
				item.setAlignment(Qt.AlignCenter)

				# Signals / Slots.
				item.editingFinished.connect(self.__view__valueChanged)
			else:
				item = QLabel(QString("Attribute Type Error!"))
				item.setStyleSheet("QLabel {background-color: rgb(210, 64, 32);}")
				item.setAlignment(Qt.AlignCenter)

			item.data = attributeCompound
			view.setCellWidget(row, 0, item)

		view.setVerticalHeaderLabels(verticalHeaderLabels)
		view.show()

	def __view_clearUi(self, view):
		"""
		Defines and sets the given View.

		:param view: Table Widget.
		:type view: QTableWidget
		"""

		LOGGER.debug("> Clearing '{0}'.".format(view.objectName()))

		view.clear()
		view.setRowCount(0)
		view.setColumnCount(0)

	def __views_setUi(self):
		"""
		Sets the Views.
		"""

		selectedTemplates = self.__templatesOutliner.getSelectedTemplates()
		template = foundations.common.getFirstItem(selectedTemplates)
		if not (template and foundations.common.pathExists(template.path)):
			for view in self.__views:
				self.__view_clearUi(view)
			return

		LOGGER.debug("> Attempting to read '{0}' Template settings file.".format(template.name))
		commonAttributesOverrides = {}
		additionalAttributesOverrides = {}
		templateSettingsDirectory = os.path.join(self.__templatesSettingsDirectory, template.software, template.name)
		currentTemplateSettingsDirectory = os.path.join(templateSettingsDirectory, template.release)
		self.__templateSettingsFile = os.path.join(templateSettingsDirectory,
										template.release,
										os.path.basename(template.path))

		not foundations.common.pathExists(currentTemplateSettingsDirectory) and \
		foundations.io.setDirectory(currentTemplateSettingsDirectory)

		templateSettingsFile = None
		if foundations.common.pathExists(self.__templateSettingsFile):
			templateSettingsFile = self.__templateSettingsFile
		else:
			for version in sorted((
							path for path in os.listdir(templateSettingsDirectory)
							if re.search(r"\d\.\d\.\d", path)), reverse=True, key=lambda x:(foundations.strings.getVersionRank(x))):
				path = os.path.join(templateSettingsDirectory, version, os.path.basename(template.path))
				if foundations.common.pathExists(path):
					templateSettingsFile = path
					break

		if templateSettingsFile:
			LOGGER.debug("> Accessing '{0}' Template settings file: '{1}'.".format(template.name, templateSettingsFile))
			templateSettingsSectionsFileParser = SectionsFileParser(templateSettingsFile)
			templateSettingsSectionsFileParser.parse()
			commonAttributesOverrides.update(
			templateSettingsSectionsFileParser.sections[self.__templateCommonAttributesSection])
			additionalAttributesOverrides.update(
			templateSettingsSectionsFileParser.sections[self.__templateAdditionalAttributesSection])
		else:
			LOGGER.debug("> No Template settings file found for : '{0}'.".format(template.name))

		LOGGER.debug("> Parsing '{0}' Template for '{1}' and '{2}' section.".format(
		template.name, self.__templateCommonAttributesSection, self.__templateAdditionalAttributesSection))
		templateSectionsFileParser = SectionsFileParser(template.path)
		templateSectionsFileParser.parse(rawSections=(self.__templateScriptSection))

		self.__view_setUi(templateSectionsFileParser.sections.get(self.__templateCommonAttributesSection, {}),
								self.__commonView, commonAttributesOverrides)
		self.__view_setUi(templateSectionsFileParser.sections.get(self.__templateAdditionalAttributesSection, {}),
								self.__additionalView, additionalAttributesOverrides)

	def __view__valueChanged(self, *args):
		"""
		Defines the slot triggered by a View when value changed.

		:param \*args: Arguments.
		:type \*args: \*
		"""

		LOGGER.debug("> Initializing '{0}' Template settings file content.".format(self.__templateSettingsFile))
		templateSettingsSectionsFileParser = SectionsFileParser(self.__templateSettingsFile)
		templateSettingsSectionsFileParser.sections = OrderedDict()
		for section, view in OrderedDict([(self.__templateCommonAttributesSection,
												self.Common_Attributes_tableWidget),
												(self.__templateAdditionalAttributesSection,
												self.Additional_Attributes_tableWidget)]).iteritems():
			templateSettingsSectionsFileParser.sections[section] = OrderedDict()
			for row in range(view.rowCount()):
				widget = view.cellWidget(row, 0)
				if type(widget) is Variable_QPushButton:
					value = widget.text() == "True" and "1" or "0"
				elif type(widget) is QDoubleSpinBox:
					value = foundations.strings.toString(widget.value())
				elif type(widget) is QComboBox:
					value = foundations.strings.toString(widget.currentText())
				else:
					value = foundations.strings.toString(widget.text())
				templateSettingsSectionsFileParser.sections[
				section][foundations.namespace.removeNamespace(widget.data.name)] = value
		templateSettingsSectionsFileParser.write()

	def __templatesOutliner_view_selectionModel__selectionChanged(self, selectedItems, deselectedItems):
		"""
		Defines the slot triggered by **templatesOutliner.view** Model when selection changed

		:param selectedItems: Selected items.
		:type selectedItems: QItemSelection
		:param deselectedItems: Deselected items.
		:type deselectedItems: QItemSelection
		"""

		self.__views_setUi()

	def __updateOverrideKeys(self, view):
		"""
		Updates the Loader Script Component override keys.

		:param view: Table Widget.
		:type view: QTableWidget
		:return: Method success.
		:rtype: bool
		"""

		LOGGER.debug("> Updating override keys with '{0}' attributes.".format(view.objectName()))

		for row in range(view.rowCount()):
			widget = view.cellWidget(row, 0)
			if type(widget) is Variable_QPushButton:
				value = widget.text() == "True" and "1" or "0"
			elif type(widget) is QDoubleSpinBox:
				value = foundations.strings.toString(widget.value())
			elif type(widget) is QComboBox:
				value = foundations.strings.toString(widget.currentText())
			else:
				value = foundations.strings.toString(widget.text())
			widget.data.value = value

			LOGGER.debug("> Adding '{0}' override key with value: '{1}'.".format(widget.data.name, widget.data.value))
			self.__loaderScript.overrideKeys[widget.data.name] = widget.data
		return True

	@foundations.exceptions.handleExceptions(umbra.exceptions.notifyExceptionHandler, Exception)
	def getOverrideKeys(self):
		"""
		Gets override keys.

		:return: Method success.
		:rtype: bool
		"""

		LOGGER.info("{0} | Updating Loader Script override keys!".format(self.__class__.__name__))

		success = True
		success *= self.__updateOverrideKeys(self.Common_Attributes_tableWidget) or False
		success *= self.__updateOverrideKeys(self.Additional_Attributes_tableWidget) or False

		if success:
			return True
		else:
			raise Exception("{0} | Exception raised while retrieving override keys!".format(self.__class__.__name__))
