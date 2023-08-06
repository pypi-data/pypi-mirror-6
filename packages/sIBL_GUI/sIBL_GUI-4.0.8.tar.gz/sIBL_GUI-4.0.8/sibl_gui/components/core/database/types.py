#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**types.py**

**Platform:**
	Windows, Linux, Mac Os X.

**Description:**
	Defines Application Database types: :class:`IblSet`, :class:`Template`
	and :class:`Collection` classes.

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
import sqlalchemy.ext.declarative
from sqlalchemy import ForeignKey

#**********************************************************************************************************************
#***	Internal imports.
#**********************************************************************************************************************
import foundations.exceptions
import foundations.parsers
import foundations.verbose
from foundations.parsers import SectionsFileParser

#**********************************************************************************************************************
#***	Module attributes.
#**********************************************************************************************************************
__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2008 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["LOGGER", "Base", "IblSet", "Template", "Collection"]

LOGGER = foundations.verbose.installLogger()

#**********************************************************************************************************************
#***	Module classes and definitions.
#**********************************************************************************************************************
Base = sqlalchemy.ext.declarative.declarative_base()

class IblSet(Base):
	"""
	Defines the Database IblSets type.
	"""

	__tablename__ = "IblSets"
	"""
	:param __tablename__: Table name.
	:type __tablename__: unicode
	"""

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	path = sqlalchemy.Column(sqlalchemy.String)
	osStats = sqlalchemy.Column(sqlalchemy.String)
	collection = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("Collections.id"))
	title = sqlalchemy.Column(sqlalchemy.String)
	author = sqlalchemy.Column(sqlalchemy.String)
	link = sqlalchemy.Column(sqlalchemy.String)
	icon = sqlalchemy.Column(sqlalchemy.String)
	previewImage = sqlalchemy.Column(sqlalchemy.String)
	backgroundImage = sqlalchemy.Column(sqlalchemy.String)
	lightingImage = sqlalchemy.Column(sqlalchemy.String)
	reflectionImage = sqlalchemy.Column(sqlalchemy.String)
	location = sqlalchemy.Column(sqlalchemy.String)
	latitude = sqlalchemy.Column(sqlalchemy.String)
	longitude = sqlalchemy.Column(sqlalchemy.String)
	date = sqlalchemy.Column(sqlalchemy.String)
	time = sqlalchemy.Column(sqlalchemy.String)
	comment = sqlalchemy.Column(sqlalchemy.String)

	def __init__(self,
			name=None,
			path=None,
			osStats=None,
			collection=None,
			title=None,
			author=None,
			link=None,
			icon=None,
			previewImage=None,
			backgroundImage=None,
			lightingImage=None,
			reflectionImage=None,
			location=None,
			latitude=None,
			longitude=None,
			date=None,
			time=None,
			comment=None):
		"""
		Initializes the class.

		:param name: Ibl Set name.
		:type name: unicode
		:param path: Ibl Set file path.
		:type path: unicode
		:param osStats: Ibl Set file statistics.
		:type osStats: unicode
		:param collection: Ibl Set collection.
		:type collection: unicode
		:param title: Ibl Set title.
		:type title: unicode
		:param author: Ibl Set author.
		:type author: unicode
		:param link: Ibl Set online link.
		:type link: unicode
		:param icon: Ibl Set icon path.
		:type icon: unicode
		:param previewImage: Ibl Set preview image path.
		:type previewImage: unicode
		:param backgroundImage: Ibl Set background image path.
		:type backgroundImage: unicode
		:param lightingImage: Ibl Set lighting image path.
		:type lightingImage: unicode
		:param reflectionImage: Ibl Set reflection image path.
		:type reflectionImage: unicode
		:param location: Ibl Set location.
		:type location: unicode
		:param latitude: Ibl Set latitude.
		:type latitude: unicode
		:param longitude: Ibl Set longitude.
		:type longitude: unicode
		:param date: Ibl Set shot date.
		:type date: unicode
		:param time: Ibl Set shot time.
		:type time: unicode
		:param comment: Ibl Set comment.
		:type comment: unicode
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		# --- Setting class attributes. ---
		self.name = name
		self.path = path
		self.osStats = osStats
		self.collection = collection
		self.title = title
		self.author = author
		self.link = link
		self.icon = icon
		self.previewImage = previewImage
		self.backgroundImage = backgroundImage
		self.lightingImage = lightingImage
		self.reflectionImage = reflectionImage
		self.location = location
		self.latitude = latitude
		self.longitude = longitude
		self.date = date
		self.time = time
		self.comment = comment

	@foundations.exceptions.handleExceptions(foundations.exceptions.FileStructureParsingError)
	def setContent(self):
		"""
		Initializes the class attributes.

		:return: Method success.
		:rtype: bool
		"""

		sectionsFileParser = SectionsFileParser(self.path)
		sectionsFileParser.parse()

		if sectionsFileParser.sections:
			self.title = sectionsFileParser.getValue("Name", "Header")
			self.author = sectionsFileParser.getValue("Author", "Header")
			self.link = sectionsFileParser.getValue("Link", "Header")
			self.icon = os.path.normpath(os.path.join(os.path.dirname(self.path),
										sectionsFileParser.getValue("ICOfile", "Header"))) \
										if sectionsFileParser.getValue("ICOfile", "Header") else None
			self.previewImage = os.path.normpath(os.path.join(os.path.dirname(self.path),
								 				sectionsFileParser.getValue("PREVIEWfile", "Header"))) \
								 				if sectionsFileParser.getValue("PREVIEWfile", "Header") else None
			self.backgroundImage = os.path.normpath(os.path.join(os.path.dirname(self.path),
													sectionsFileParser.getValue("BGfile", "Background"))) \
													if sectionsFileParser.getValue("BGfile", "Background") else None
			self.lightingImage = os.path.normpath(os.path.join(os.path.dirname(self.path),
												sectionsFileParser.getValue("EVfile", "Enviroment"))) \
												if sectionsFileParser.getValue("EVfile", "Enviroment") else None
			self.reflectionImage = os.path.normpath(os.path.join(os.path.dirname(self.path),
													sectionsFileParser.getValue("REFfile", "Reflection"))) \
													if sectionsFileParser.getValue("REFfile", "Reflection") else None
			self.location = sectionsFileParser.getValue("Location", "Header")
			self.latitude = sectionsFileParser.getValue("GEOlat", "Header")
			self.longitude = sectionsFileParser.getValue("GEOlong", "Header")
			self.date = sectionsFileParser.getValue("Date", "Header")
			self.time = sectionsFileParser.getValue("Time", "Header")
			self.comment = sectionsFileParser.getValue("Comment", "Header")

			return True
		else:
			raise foundations.exceptions.FileStructureParsingError(
			"{0} | '{1}' no sections found, file structure seems invalid!".format(self.__class__.__name__, self.path))

class Template(Base):
	"""
	Defines the Database Template type.
	"""

	__tablename__ = "Templates"
	"""
	:param __tablename__: Table name.
	:type __tablename__: unicode
	"""

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	path = sqlalchemy.Column(sqlalchemy.String)
	osStats = sqlalchemy.Column(sqlalchemy.String)
	collection = sqlalchemy.Column(sqlalchemy.Integer, ForeignKey("Collections.id"))
	helpFile = sqlalchemy.Column(sqlalchemy.String)
	title = sqlalchemy.Column(sqlalchemy.String)
	author = sqlalchemy.Column(sqlalchemy.String)
	email = sqlalchemy.Column(sqlalchemy.String)
	url = sqlalchemy.Column(sqlalchemy.String)
	release = sqlalchemy.Column(sqlalchemy.String)
	date = sqlalchemy.Column(sqlalchemy.String)
	software = sqlalchemy.Column(sqlalchemy.String)
	version = sqlalchemy.Column(sqlalchemy.String)
	renderer = sqlalchemy.Column(sqlalchemy.String)
	outputScript = sqlalchemy.Column(sqlalchemy.String)
	comment = sqlalchemy.Column(sqlalchemy.String)

	def __init__(self,
			name=None,
			path=None,
			osStats=None,
			collection=None,
			helpFile=None,
			title=None,
			author=None,
			email=None,
			url=None,
			release=None,
			date=None,
			software=None,
			version=None,
			renderer=None,
			outputScript=None,
			comment=None):
		"""
		Initializes the class.

		:param name: Template name.
		:type name: unicode
		:param path: Template file path.
		:type path: unicode
		:param osStats: Template file statistics.
		:type osStats: unicode
		:param collection: Template collection.
		:type collection: unicode
		:param helpFile: Template help file path.
		:type helpFile: unicode
		:param title: Template title.
		:type title: unicode
		:param author: Template author.
		:type author: unicode
		:param email: Template author email.
		:type email: unicode
		:param url: Template online link.
		:type url: unicode
		:param release: Template release version.
		:type release: unicode
		:param date: Template release date.
		:type date: unicode
		:param software: Template target software.
		:type software: unicode
		:param version: Template target software version.
		:type version: unicode
		:param renderer: Template target renderer.
		:type renderer: unicode
		:param outputScript: Template loader script name.
		:type outputScript: unicode
		:param comment: Template comment.
		:type comment: unicode
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		# --- Setting class attributes. ---
		self.name = name
		self.path = path
		self.osStats = osStats
		self.collection = collection
		self.helpFile = helpFile
		self.title = title
		self.author = author
		self.email = email
		self.url = url
		self.release = release
		self.date = date
		self.software = software
		self.version = version
		self.renderer = renderer
		self.outputScript = outputScript
		self.comment = comment

	@foundations.exceptions.handleExceptions(foundations.exceptions.FileStructureParsingError)
	def setContent(self):
		"""
		Initializes the class attributes.

		:return: Method success.
		:rtype: bool
		"""

		sectionsFileParser = SectionsFileParser(self.path)
		sectionsFileParser.parse(rawSections=("Script"))

		if sectionsFileParser.sections:
			self.helpFile = foundations.parsers.getAttributeCompound("HelpFile",
							sectionsFileParser.getValue("HelpFile", "Template")).value and \
							os.path.join(os.path.dirname(self.path),
										foundations.parsers.getAttributeCompound("HelpFile",
										sectionsFileParser.getValue("HelpFile", 	"Template")).value) or None
			self.title = foundations.parsers.getAttributeCompound("Name",
						sectionsFileParser.getValue("Name", 	"Template")).value
			self.author = foundations.parsers.getAttributeCompound("Author",
						sectionsFileParser.getValue("Author", "Template")).value
			self.email = foundations.parsers.getAttributeCompound("Email",
						sectionsFileParser.getValue("Email", "Template")).value
			self.url = foundations.parsers.getAttributeCompound("Url",
						sectionsFileParser.getValue("Url", "Template")).value
			self.release = foundations.parsers.getAttributeCompound("Release",
							sectionsFileParser.getValue("Release", "Template")).value
			self.date = foundations.parsers.getAttributeCompound("Date",
						sectionsFileParser.getValue("Date", "Template")).value
			self.software = foundations.parsers.getAttributeCompound("Software",
							sectionsFileParser.getValue("Software", "Template")).value
			self.version = foundations.parsers.getAttributeCompound("Version",
							sectionsFileParser.getValue("Version", "Template")).value
			self.renderer = foundations.parsers.getAttributeCompound("Renderer",
							sectionsFileParser.getValue("Renderer", "Template")).value
			self.outputScript = foundations.parsers.getAttributeCompound("OutputScript",
								sectionsFileParser.getValue("OutputScript", "Template")).value
			self.comment = foundations.parsers.getAttributeCompound("Comment",
							sectionsFileParser.getValue("Comment", "Template")).value

			return True

		else:
			raise foundations.exceptions.FileStructureParsingError(
			"{0} | '{1}' no sections found, file structure seems invalid!".format(self.__class__.__name__, self.path))

class Collection(Base):
	"""
	Defines the Database Collection type.
	"""

	__tablename__ = "Collections"
	"""
	:param __tablename__: Table name.
	:type __tablename__: unicode
	"""

	id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
	name = sqlalchemy.Column(sqlalchemy.String)
	type = sqlalchemy.Column(sqlalchemy.String)
	comment = sqlalchemy.Column(sqlalchemy.String)

	def __init__(self, name=None, type=None, comment=None):
		"""
		Initializes the class.

		:param name: Collection name.
		:type name: unicode
		:param type: Collection type.
		:type type: unicode
		:param comment: Collection comment.
		:type comment: unicode
		"""

		LOGGER.debug("> Initializing '{0}()' class.".format(self.__class__.__name__))

		# --- Setting class attributes. ---
		self.name = name
		self.type = type
		self.comment = comment
