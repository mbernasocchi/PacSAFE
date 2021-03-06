# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Cell.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'marco@opengis.ch'
__revision__ = 'f16353426abc9c5fd8f65e2eb0e87e11c4159468'
__date__ = '04/06/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from message_element import MessageElement
from text import Text

# FIXME (MB) remove when all to_* methods are implemented
# pylint: disable=W0223


class Cell(MessageElement):
    """A class to model table cells in the messaging system """

    def __init__(self, *args, **kwargs):
        """Creates a cell object

        :param: Text can be Text object or string

        :param header: A flag to indicate if the cell should be treated as
            a header cell. Depending on the ouput format cells may be rendered
            differently e.g. with bold text.
        :type header: bool

        :param align: A flag to indicate if special alignment should
            be given to cells if supported in the output renderer.
            Valid options are: None, 'left', 'right', 'center'

        We pass the kwargs on to the base class after first removing the
        kwargs that we explicitly expect here so an exception is raised
        if invalid keywords were passed. See:

        http://stackoverflow.com/questions/13124961/
        how-to-pass-arguments-efficiently-kwargs-in-python
        """
        # First check if we get a header keyword arg. If we do we will
        # Format each cell with important_text, th or whatever is appropriate.
        self.header_flag = False
        if 'header' in kwargs:
            self.header_flag = kwargs['header']
            kwargs.pop('header')
        # Also check if align parameter is called before calling the ABC
        self.align = None
        if 'align' in kwargs:
            if kwargs['align'] in [None, 'left', 'right', 'center']:
                self.align = kwargs['align']
            kwargs.pop('align')

        super(Cell, self).__init__(**kwargs)

        # Special case for when we want to put a nested table in a cell
        # We dont use isinstance because of recursive imports with table
        class_name = args[0].__class__.__name__
        if class_name in ['BulletedList', 'Table']:
            self.content = args[0]
        else:
            self.content = Text(*args)

    def to_html(self):
        """Render a Cell MessageElement as html

        :returns: The html representation of the Cell MessageElement
        :rtype: basestring
        """
        # Apply bootstrap alignment classes first
        if self.align is 'left':
            if self.style_class is None:
                self.style_class = 'text-left'
            else:
                self.style_class += ' text-left'
        elif self.align is 'right':
            if self.style_class is None:
                self.style_class = 'text-right'
            else:
                self.style_classs += ' text-right'
        elif self.align is 'center':
            if self.style_class is None:
                self.style_class = 'text-center'
            else:
                self.style_class += ' text-center'
        # Check if we have a header or not then render
        if self.header_flag is True:
            return '<th%s>%s</th>\n' % (
                self.html_attributes(), self.content.to_html())
        else:
            return '<td%s>%s</td>\n' % (
                self.html_attributes(), self.content.to_html())

    def to_text(self):
        """Render a Cell MessageElement as plain text

        :returns: The plain text representation of the Cell MessageElement.
        :rtype: basestring

        """
        if self.header_flag is True:
            return '**%s**' % self.content
        else:
            return '%s' % self.content

    def to_markdown(self):
        """Render a MessageElement queue as markdown

        :returns: Markdown representation of the Text MessageElement.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')

    def to_json(self):
        """Render a MessageElement queue as JSON

        :returns: Json representation of the Text MessageElement.
        :rtype: str
        """
        raise NotImplementedError('Please Implement this method')
