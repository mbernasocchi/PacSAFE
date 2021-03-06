# -*- coding: utf-8 -*-
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**metadata module.**

Contact: ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = 'f16353426abc9c5fd8f65e2eb0e87e11c4159468'
__date__ = '27/05/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from safe.common.exceptions import InvalidProvenanceDataError
from safe.metadata.provenance.provenance_step import ProvenanceStep


class IFProvenanceStep(ProvenanceStep):
    """
    Class to store a provenance step from an impact function.

    all impact_functions_fields need to be passed in the data dict

    .. versionadded:: 3.2

    """

    impact_functions_fields = [
        'start_time',
        'finish_time',
        'hazard_layer',
        'exposure_layer',
        'impact_function_id',
        'impact_function_version',
        'host_name',
        'user',
        'qgis_version',
        'gdal_version',
        'qt_version',
        'pyqt_version',
        'os',
        'inasafe_version',
        'exposure_pixel_size',
        'hazard_pixel_size',
        'impact_pixel_size',
        'analysis_extent',
        'parameter'
    ]

    def __init__(self, title, description, data, timestamp=None):
        for key in self.impact_functions_fields:
            # check we have all the wanted keys
            if key not in data:
                message = ('Key %s is missing in the passed IF provenance '
                           'data. Found: %s' % (key, data))
                raise InvalidProvenanceDataError(message)

        super(IFProvenanceStep, self).__init__(
            title, description, timestamp, data)

    def __getattr__(self, key):
        """
        Dynamically generate getter for each _standard_properties.
        """

        if key in self.impact_functions_fields:
            return self.data(key)
        else:
            return super(IFProvenanceStep, self).__getattr__(key)

    @property
    def xml(self):
        """
        the xml string representation.

        :return: the xml
        :rtype: str
        """

        xml = self._get_xml(False)
        for key in self.impact_functions_fields:
            value = self.data(key)
            xml += '<{0}>{1}</{0}>\n'.format(key, value)

        xml += '</provenance_step>\n'
        return xml
