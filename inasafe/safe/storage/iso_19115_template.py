# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -

ISO 19115 METADATA XML TEMPLATE

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'marco@opengis.ch'
__revision__ = 'f16353426abc9c5fd8f65e2eb0e87e11c4159468'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from string import Template  # pylint: disable=W0402
from safe.utilities.resources import resources_path

_xml_file = resources_path('iso_19115_template.xml')
with open(_xml_file) as f:
    _template = f.read()

# This template uses python strings.Template module to allow replacing values
# in the XML. Do not use it directly, instead use
# safe.storage.metadata_utilities.write_iso_metadata_file which will replace
# the $placeholders with the safe.defaults.get_defaults values.
# The $placeholders need to have the same name ass the keys in the DEFAULTS
# dictionary. For example $ISO19115_ORGANIZATION will be replaced by
# get_defaults('ISO19115_ORGANIZATION')
# This template was generated by http://inspire-geoportal.ec.europa.eu/editor/
ISO_METADATA_XML_TEMPLATE = Template(_template)
