# -*- coding: utf-8 -*-
import logging
log = logging.getLogger('seantis.dir.events')

import csv
from StringIO import StringIO
import urllib2
import json

import HTMLParser

from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.event.base import default_timezone
from plone.dexterity.utils import createContentInContainer
from plone.directives import form
from plone.namedfile import NamedFile
from plone.namedfile import NamedImage
from plone.namedfile.field import NamedFile as NamedFileField
from z3c.form import field
from z3c.form.button import buttonAndHandler

from seantis.dir.base.fieldmap import get_map
from seantis.dir.base.xlsimport import add_defaults
from seantis.dir.events.interfaces import IEventsDirectory


categories1 = {
    "any_event_type": "Alle Veranstaltungen",
    "Politik": "Politik",
    "exhibition_museum": "Ausstellung & Museum",
    "miscellaneous": "Diverses",
    "health_social": "Gesundheit & Soziales",
    "classical_concert": "Konzert Klassik",
    "pop_rock_jazz_concert": "Konzert Pop/Rock/Jazz",
    "party": "Party",
    "sports": "Sport",
    "theater": "Theater / Tanz",
    "tourism": "Tourismus",
    "talk": "Vortrag / Lesung",
    "economy": "Wirtschaft & Gewerbe",
    "brauchtum": "Brauchtum",
    "folkmusic": "Volksmusik",
}

categories2 = {

}


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


class IImportDirectorySchema(form.Schema):
    """ Define fields used on the form """
    csv_file = NamedFileField(title=u"CSV file")


class Import(form.Form):
    label = u'Import events from existing Zug events directory'
    fields = field.Fields(IImportDirectorySchema)

    grok.context(IEventsDirectory)
    grok.require('cmf.ManagePortal')
    grok.name('import_zug')

    ignoreContext = True

    parser = HTMLParser.HTMLParser()

    infos = []

    def readable_html(self, html):
        html = html.replace('<br />', '\n')
        return self.parser.unescape(html)

    @buttonAndHandler(u'Import', name='import')
    def import_csv(self, action):

        # Extract form field values and errors from HTTP request
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        # Delete all existing events
        self.context.manage_delObjects(self.context.objectIds())

        workflow_tool = getToolByName(self.context, 'portal_workflow')
        fieldmap = get_map(self.context)

        io = StringIO(data['csv_file'].data)
        reader = unicode_csv_reader(io, delimiter=';', quotechar='"')

        # Skip header line
        reader.next()
        counter = 0
        for row in reader:

            attributes = dict()
            for attr, ix in fieldmap.fieldmap.items():
                if not attr in fieldmap.readonly:
                    value = row[ix]
                    unwrapped = fieldmap.get_unwrapper(ix=ix)(value)
                    attributes[attr] = unwrapped

            # Unmapped fields are filled with defaults
            add_defaults(attributes, fieldmap)

            # Adjust coordinates
            coordinates = attributes['coordinates_json']
            if coordinates:
                coordinates = coordinates.replace("'", '"')

                cords = json.loads(coordinates)
                latitude = cords[1][0]
                longitude = cords[1][1]
                cords[1][0] = longitude
                cords[1][1] = latitude
                attributes['coordinates_json'] = json.dumps(cords)

            # "What" category
            cats1 = []
            if attributes['cat1']:
                for cat in attributes['cat1']:
                    if cat:
                        cats1.append(categories1[cat])
            attributes['cat1'] = cats1

            # "Where" category
            if attributes['town']:
                attributes['town'] = categories2.get(
                    attributes['town'], attributes['town']
                )
                attributes['cat2'] = [attributes['town']]

            # Manipulate some attributes
            attributes['timezone'] = default_timezone()
            attributes['long_description'] = self.readable_html(
                attributes['long_description']
            )

            # Fetch image form URL
            image_url = row[-3]
            if image_url:
                response = urllib2.urlopen(image_url)
                image = response.read()
                attributes['image'] = NamedImage(image)

            # Fetach PDF from URL
            pdf_url = row[-2]
            if pdf_url:
                response = urllib2.urlopen(pdf_url)
                pdf_file = response.read()
                attributes['attachment_1'] = NamedFile(pdf_file)

            # Create event
            event = createContentInContainer(
                self.context, fieldmap.typename, **attributes
            )

            # Log the events which span multiple days, they need to manually
            # adjusted by the client
            if attributes['start'].date() != attributes['end'].date():
                log.info(
                    '"%s" spans multiple days' % event.absolute_url()
                )

            # Publish event
            workflow_tool.doActionFor(event, 'submit')
            workflow_tool.doActionFor(event, 'publish')
            counter += 1

        self.status = u'Imported %s events' % counter
