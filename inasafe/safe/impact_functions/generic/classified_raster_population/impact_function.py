# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - ** Generic Impact
Function on Population for Classified Hazard.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'lucernae'
__date__ = '24/03/15'
__revision__ = '03d01890920b07c702f377c171c42a50bcb8f74f'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import numpy
import itertools

from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding,
    has_no_data)
from safe.storage.raster import Raster
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.utilities.i18n import tr
from safe.common.tables import Table, TableRow
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.generic.\
    classified_raster_population.metadata_definitions import \
    ClassifiedRasterHazardPopulationMetadata
from safe.impact_functions.impact_function_manager\
    import ImpactFunctionManager
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters
from safe.common.exceptions import (
    FunctionParametersError, ZeroImpactException)


class ClassifiedRasterHazardPopulationFunction(ImpactFunction):
    # noinspection PyUnresolvedReferences
    """Plugin for impact of population as derived by classified hazard."""

    _metadata = ClassifiedRasterHazardPopulationMetadata()

    def __init__(self):
        super(ClassifiedRasterHazardPopulationFunction, self).__init__()
        self.impact_function_manager = ImpactFunctionManager()

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)

    def _tabulate(self, high, low, medium, minimum_needs, no_impact, question,
                  total_impact):
        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([tr('Total Population Affected '),
                                '%s' % format_int(total_impact)],
                               header=True),
                      TableRow([tr('Population in High hazard class areas '),
                                '%s' % format_int(high)]),
                      TableRow([tr('Population in Medium hazard class areas '),
                                '%s' % format_int(medium)]),
                      TableRow([tr('Population in Low hazard class areas '),
                                '%s' % format_int(low)]),
                      TableRow([tr('Population Not Affected'),
                                '%s' % format_int(no_impact)]),
                      TableRow(
                          tr('Table below shows the minimum needs for all '
                             'evacuated people'))]
        total_needs = evacuated_population_needs(
            total_impact, minimum_needs)
        for frequency, needs in total_needs.items():
            table_body.append(TableRow(
                [
                    tr('Needs should be provided %s' % frequency),
                    tr('Total')
                ],
                header=True))
            for resource in needs:
                table_body.append(TableRow([
                    tr(resource['table name']),
                    format_int(resource['amount'])]))
        return table_body, total_needs

    def _tabulate_action_checklist(self, table_body, total, no_data_warning):
        table_body.append(
            TableRow(tr('Action Checklist:'), header=True))
        table_body.append(
            TableRow(tr('How will warnings be disseminated?')))
        table_body.append(
            TableRow(tr('How will we reach stranded people?')))
        table_body.append(
            TableRow(tr('Do we have enough relief items?')))
        table_body.append(
            TableRow(
                tr('If yes, where are they located and how will we distribute '
                   'them?')))
        table_body.append(
            TableRow(
                tr('If no, where can we obtain additional relief items from '
                   'and how will we transport them to here?')))
        # Extend impact report for on-screen display
        table_body.extend([
            TableRow(tr('Notes'), header=True),
            tr('Map shows the numbers of people in high, medium, and low '
               'hazard class areas'),
            tr('Total population: %s') % format_int(total)
        ])
        if no_data_warning:
            table_body.extend([
                tr('The layers contained `no data`. This missing data was '
                   'carried through to the impact layer.'),
                tr('`No data` values in the impact layer were treated as 0 '
                   'when counting the affected or total population.')
            ])
        return table_body

    def run(self, layers=None):
        """Plugin for impact of population as derived by classified hazard.

        Input
        :param layers: List of layers expected to contain

              * hazard_layer: Raster layer of classified hazard
              * exposure_layer: Raster layer of population data

        Counts number of people exposed to each class of the hazard

        Return
          Map of population exposed to high class
          Table with number of people in each class
        """
        self.validate()
        self.prepare(layers)

        # The 3 classes
        # TODO (3.2): shouldnt these be defined in keywords rather? TS
        low_class = self.parameters['low_hazard_class']
        medium_class = self.parameters['medium_hazard_class']
        high_class = self.parameters['high_hazard_class']

        # The classes must be different to each other
        unique_classes_flag = all(
            x != y for x, y in list(
                itertools.combinations(
                    [low_class, medium_class, high_class], 2)))
        if not unique_classes_flag:
            raise FunctionParametersError(
                'There is hazard class that has the same value with other '
                'class. Please check the parameters.')

        # Identify hazard and exposure layers
        hazard_layer = self.hazard  # Classified Hazard
        exposure_layer = self.exposure  # Population Raster

        # Extract data as numeric arrays
        hazard_data = hazard_layer.get_data(nan=True)  # Class
        no_data_warning = False
        if has_no_data(hazard_data):
            no_data_warning = True

        # Calculate impact as population exposed to each class
        population = exposure_layer.get_data(scaling=True)

        # Get all population data that falls in each hazard class
        high_hazard_population = numpy.where(
            hazard_data == high_class, population, 0)
        medium_hazard_population = numpy.where(
            hazard_data == medium_class, population, 0)
        low_hazard_population = numpy.where(
            hazard_data == low_class, population, 0)
        affected_population = (
            high_hazard_population + medium_hazard_population +
            low_hazard_population)

        # Carry the no data values forward to the impact layer.
        affected_population = numpy.where(
            numpy.isnan(population),
            numpy.nan,
            affected_population)
        affected_population = numpy.where(
            numpy.isnan(hazard_data),
            numpy.nan,
            affected_population)

        # Count totals
        total_population = int(numpy.nansum(population))
        total_high_population = int(numpy.nansum(high_hazard_population))
        total_medium_population = int(numpy.nansum(medium_hazard_population))
        total_low_population = int(numpy.nansum(low_hazard_population))
        total_affected = int(numpy.nansum(affected_population))
        total_not_affected = total_population - total_affected

        # check for zero impact
        if total_affected == 0:
            table_body = [
                self.question,
                TableRow(
                    [tr('People affected'),
                     '%s' % format_int(total_affected)], header=True)]
            message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(message)

        minimum_needs = [
            parameter.serialize() for parameter in
            self.parameters['minimum needs']
        ]

        table_body, total_needs = self._tabulate(
            population_rounding(total_high_population),
            population_rounding(total_low_population),
            population_rounding(total_medium_population),
            minimum_needs,
            population_rounding(total_not_affected),
            self.question,
            population_rounding(total_affected))

        impact_table = Table(table_body).toNewlineFreeString()

        table_body = self._tabulate_action_checklist(
            table_body,
            population_rounding(total_population),
            no_data_warning)
        impact_summary = Table(table_body).toNewlineFreeString()

        # Create style
        colours = [
            '#FFFFFF', '#38A800', '#79C900', '#CEED00',
            '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        classes = create_classes(affected_population.flat[:], len(colours))
        interval_classes = humanize_class(classes)
        style_classes = []

        for i in xrange(len(colours)):
            style_class = dict()
            if i == 1:
                label = create_label(
                    interval_classes[i],
                    tr('Low Population [%i people/cell]' % classes[i]))
            elif i == 4:
                label = create_label(
                    interval_classes[i],
                    tr('Medium Population [%i people/cell]' % classes[i]))
            elif i == 7:
                label = create_label(
                    interval_classes[i],
                    tr('High Population [%i people/cell]' % classes[i]))
            else:
                label = create_label(interval_classes[i])
            style_class['label'] = label
            style_class['quantity'] = classes[i]
            if i == 0:
                transparency = 100
            else:
                transparency = 0
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        style_info = dict(
            target_field=None,
            style_classes=style_classes,
            style_type='rasterStyle')

        # For printing map purpose
        map_title = tr('Population affected by each class')
        legend_notes = tr(
            'Thousand separator is represented by %s' %
            get_thousand_separator())
        legend_units = tr('(people per cell)')
        legend_title = tr('Number of People')

        # Create raster object and return
        raster_layer = Raster(
            data=affected_population,
            projection=exposure_layer.get_projection(),
            geotransform=exposure_layer.get_geotransform(),
            name=tr('Population which %s') % (
                self.impact_function_manager
                .get_function_title(self).lower()),
            keywords={
                'impact_summary': impact_summary,
                'impact_table': impact_table,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'total_needs': total_needs},
            style_info=style_info)
        self._impact = raster_layer
        return raster_layer
