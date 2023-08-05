"""Definition of the Media Event content type
"""
from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from plone.app.event.at import content  as event
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.Archetypes.atapi import DateTimeField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import BooleanField
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.Archetypes.atapi import CalendarWidget
from Products.Archetypes.atapi import StringWidget
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import BooleanWidget
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from DateTime.DateTime import *
from plone.app.event.at.interfaces import IATEvent, IATEventRecurrence

# -*- Message Factory Imported Here -*-

from Products.mediaEvent.interfaces import IMediaEvent
from Products.mediaEvent.config import PROJECTNAME

MediaEventSchema = folder.ATFolderSchema.copy() + event.ATEventSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
     StringField('exceptions',
        searchable=False,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = '',
            label = _(u'label_event_exceptions', default=u'Exceptions')
            )),
    
    StringField('location',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = '',
            label = _(u'label_event_location', default=u'Event Location')
            )),
    
      BooleanField('booking',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = BooleanWidget(
            description = '',
            label = _(u'label_event_booking', default=u'Booking'),
            default = False
            )),
        
      StringField('price',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Price of the event (leave empty in case of a free event).',
            label = _(u'label_event_price', default=u'Price'),
            default = ""
            )),
        
      StringField('link',
        required=False,
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Code or booking link for this event',
            label = _(u'label_event_booking', default=u'Booking code / link'),
            default = "",
            )),
      
      StringField('notes',
        searchable=False,
        required=True,
        write_permission = ModifyPortalContent,
        widget = TextAreaWidget(
            description = 'Include location, capacity, comp allocation requests, an account code & details of split (where relevant), and how people can attend (eg. is it drop-in, free but booking essential, standard ticketing?). Also essential that you give booker info on content/age restrictions/standing/strobes etc.',
            label = _(u'label_event_notes', default=u'Event Box Office Information')
            )),
      
      
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

MediaEventSchema['title'].storage = atapi.AnnotationStorage()
MediaEventSchema['description'].storage = atapi.AnnotationStorage() 
MediaEventSchema['text'].storage = atapi.AnnotationStorage()
MediaEventSchema['exceptions'].storage = atapi.AnnotationStorage()
MediaEventSchema['location'].storage = atapi.AnnotationStorage()
MediaEventSchema['startDate'].storage = atapi.AnnotationStorage()
MediaEventSchema['endDate'].storage = atapi.AnnotationStorage()
MediaEventSchema['notes'].storage = atapi.AnnotationStorage()


MediaEventSchema.moveField('startDate', before='text')
MediaEventSchema.moveField('endDate', before='text')
MediaEventSchema.moveField('wholeDay', after='endDate')
MediaEventSchema.moveField('recurrence', after='wholeDay')
MediaEventSchema.moveField('exceptions', before='text')


schemata.finalizeATCTSchema(
    MediaEventSchema,
    folderish=True,
    moveDiscussion=False
)


class MediaEvent(folder.ATFolder, event.ATEvent):
    """Event type that has a folderish behaviour to store media related to the event."""
    implements(IMediaEvent)

    meta_type = "MediaEvent"
    schema = MediaEventSchema
    schema['relatedItems'].widget.visible['edit'] = 'visible'
    schema['attendees'].widget.visible['edit'] = 'hidden'
    schema['contactName'].widget.visible['edit'] = 'hidden'
    schema['contactEmail'].widget.visible['edit'] = 'hidden'
    schema['contactPhone'].widget.visible['edit'] = 'hidden'
    schema['eventUrl'].widget.visible['edit'] = 'hidden'
    #TODO: Set default timezone and hide the widget
    #schema['timezone'].widget.visible['edit'] = 'hidden'

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    exceptions = atapi.ATFieldProperty('exceptions')
    location = atapi.ATFieldProperty('location')
    notes = atapi.ATFieldProperty('notes')
    
    
    def getDefaultTime(self):
            return DateTime()

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(MediaEvent, PROJECTNAME)
