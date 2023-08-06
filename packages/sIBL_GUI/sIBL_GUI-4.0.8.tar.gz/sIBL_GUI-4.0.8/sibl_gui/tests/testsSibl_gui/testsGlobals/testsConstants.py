#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**testsConstants.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Defines units tests for :mod:`sibl_gui.globals.constants` module.

**Others:**

"""

#**********************************************************************************************************************
#***	Future imports.
#**********************************************************************************************************************
from __future__ import unicode_literals

#**********************************************************************************************************************
#***	External imports.
#**********************************************************************************************************************
import sys
if sys.version_info[:2] <= (2, 6):
	import unittest2 as unittest
else:
	import unittest

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
from sibl_gui.globals.constants import Constants

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["ConstantsTestCase"]

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
class ConstantsTestCase(unittest.TestCase):
	"""
	Defines :class:`sibl_gui.globals.constants.Constants` class units tests methods.
	"""

	def testRequiredAttributes(self):
		"""
		Tests presence of required attributes.
		"""

		requiredAttributes = ("applicationName",
								"majorVersion",
								"minorVersion",
								"changeVersion",
								"version",
								"logger",
								"defaultCodec",
								"codecError",
								"applicationDirectory",
								"providerDirectory",
								"databaseDirectory",
								"patchesDirectory",
								"settingsDirectory",
								"userComponentsDirectory",
								"loggingDirectory",
								"templatesDirectory",
								"ioDirectory",
								"preferencesDirectories",
								"coreComponentsDirectory",
								"addonsComponentsDirectory",
								"resourcesDirectory",
								"patchesFile",
								"databaseFile",
								"settingsFile",
								"loggingFile",
								"databaseMigrationsFilesExtension",
								"librariesDirectory",
								"freeImageLibrary")

		for attribute in requiredAttributes:
			self.assertIn(attribute, Constants.__dict__)

	def testApplicationNameAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.applicationName` attribute.
		"""

		self.assertRegexpMatches(Constants.applicationName, "\w+")

	def testMajorVersionAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.majorVersion` attribute.
		"""

		self.assertRegexpMatches(Constants.version, "\d")

	def testMinorVersionAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.minorVersion` attribute.
		"""

		self.assertRegexpMatches(Constants.version, "\d")

	def testChangeVersionAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.changeVersion` attribute.
		"""

		self.assertRegexpMatches(Constants.version, "\d")

	def testversionAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.version` attribute.
		"""

		self.assertRegexpMatches(Constants.version, "\d\.\d\.\d")

	def testLoggerAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.logger` attribute.
		"""

		self.assertRegexpMatches(Constants.logger, "\w+")

	def testDefaultCodecAttribute(self):
		"""
		Tests :attr:`umbra.globals.constants.Constants.defaultCodec` attribute.
		"""

		validEncodings = ("utf-8",
						"cp1252")

		self.assertIn(Constants.defaultCodec, validEncodings)

	def testEncodingErrorAttribute(self):
		"""
		Tests :attr:`umbra.globals.constants.Constants.codecError` attribute.
		"""

		validEncodingsErrors = ("strict",
						"ignore",
						"replace",
						"xmlcharrefreplace")

		self.assertIn(Constants.codecError, validEncodingsErrors)

	def testApplicationDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.applicationDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.applicationDirectory, "\w+")

	def testProviderDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.providerDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.providerDirectory, "\w+")

	def testDatabaseDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.databaseDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.databaseDirectory, "\w+")

	def testPatchesDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.patchesDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.patchesDirectory, "\w+")

	def testSettingsDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.settingsDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.settingsDirectory, "\w+")

	def testUserComponentsDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.userComponentsDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.userComponentsDirectory, "\w+")

	def testLoggingDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.loggingDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.loggingDirectory, "\w+")

	def testTemplatesDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.templatesDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.templatesDirectory, "\w+")

	def testIoDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.ioDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.ioDirectory, "\w+")

	def testPreferencesDirectoriesAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.preferencesDirectories` attribute.
		"""

		self.assertIsInstance(Constants.preferencesDirectories, tuple)

	def testCoreComponentsDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.coreComponentsDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.coreComponentsDirectory, "\w+")

	def testAddonsComponentsDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.addonsComponentsDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.addonsComponentsDirectory, "\w+")

	def testResourcesDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.resourcesDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.resourcesDirectory, "\w+")

	def testPatchesFileAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.patchesFile` attribute.
		"""

		self.assertRegexpMatches(Constants.patchesFile, "\w+")

	def testDatabaseFileAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.databaseFile` attribute.
		"""

		self.assertRegexpMatches(Constants.databaseFile, "\w+")

	def testSettingsFileAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.settingsFile` attribute.
		"""

		self.assertRegexpMatches(Constants.settingsFile, "\w+")

	def testLoggingFileAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.loggingFile` attribute.
		"""

		self.assertRegexpMatches(Constants.loggingFile, "\w+")

	def testDatabaseMigrationsFilesExtensionAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.databaseMigrationsFilesExtension` attribute.
		"""

		self.assertRegexpMatches(Constants.databaseMigrationsFilesExtension, "\w+")

	def testLibrariesDirectoryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.librariesDirectory` attribute.
		"""

		self.assertRegexpMatches(Constants.librariesDirectory, "\w+")

	def testFreeImageLibraryAttribute(self):
		"""
		Tests :attr:`sibl_gui.globals.constants.Constants.freeImageLibrary` attribute.
		"""

		self.assertRegexpMatches(Constants.freeImageLibrary, "\w+")

if __name__ == "__main__":
	unittest.main()
