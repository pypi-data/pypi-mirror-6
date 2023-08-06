from .base import BaseModel
from .utils import add_associated_link
from .schemas.event import schema


class EventAgendaItem(dict):
    event = None
    _add_associated_link = add_associated_link

    def __init__(self, description, event):
        super(EventAgendaItem, self).__init__({
            "description": description,
            "related_entities": [],
            "subjects": [],
            "media": [],
            "notes": [],
            "order": None,
        })
        self.event = event

    def add_subject(self, what):
        self['subjects'].append(what)

    def add_committee(self, committee, id=None, note='participant'):
        self.add_entity(name=committee, type='committee', id=id, note=note)

    def add_bill(self, bill, id=None, note='consideration'):
        self.add_entity(name=bill, type='bill', id=id, note=note)

    def add_person(self, person, id=None, note='participant'):
        self.add_entity(name=person, type='person', id=id, note=note)

    def add_media_link(
        self, name, url, type='media',
        mimetype=None,
        offset=None,
        on_duplicate='error'
    ):
        return self._add_associated_link(
            collection='media',
            name=name,
            url=url,
            type=type,
            offset=offset,
            mimetype=mimetype,
            on_duplicate=on_duplicate)

    def add_entity(self, name, type, id, note):
        self['related_entities'].append({
            "name": name,
            "type": type,
            "id": id,
            "note": note,
        })


class Event(BaseModel):
    """
    Details for an event in .format
    """
    _type = 'event'
    _schema = schema
    _collection = 'events'
    __slots__ = ("when", "all_day", "name", "description", "documents",
                 "end", "links", "location", "participants",
                 "agenda", "sources", "status", "type", 'session',
                 "media", '_openstates_id', 'jurisdiction_id',
                 'identifiers',)

    def __init__(self, name, when, location, session=None, **kwargs):
        super(Event, self).__init__()
        self.when = when
        self.name = name
        self.all_day = False
        self.documents = []
        self.description = None
        self.end = None
        self.links = []
        self.location = {"name": location,
                         "note": None,
                         "coordinates": None}
        self.participants = []
        self.media = []
        self.agenda = []
        self.sources = []
        self.status = "confirmed"
        self.type = "event"
        self._related = []
        self.session = session

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return u'{0} {1}'.format(self.when, self.name.strip())
    __unicode__ = __str__

    def set_coordinates(self, lat, lon):
        self.location['coordinates'] = {
            "latitude": lat,
            "longitude": lon
        }

    def add_location_url(self, url):
        self.location['url'] = url

    def add_source(self, url, note=None):
        info = {"url": url, "note": note}
        self.sources.append(info)

    def add_link(self, url, note=None):
        info = {"url": url, "note": note}
        self.links.append(info)

    def add_document(self, name, url, mimetype, **kwargs):
        data = kwargs.copy()
        data.update({
            "name": name,
            "url": url,
            "mimetype": mimetype,
        })
        self.documents.append(data)

    def add_person(self, name, note='participant', chamber=None, id=None):
        return self.add_participant(
            name=name,
            type='person',
            chamber=chamber,
            note=note)

    def add_participant(self, name, type, note='participant', chamber=None,
                        id=None):
        self.participants.append({
            "chamber": chamber,
            "type": type,
            "note": note,
            "name": name,
            "id": id,
        })

    def add_agenda_item(self, description):
        obj = EventAgendaItem(description, self)
        self.agenda.append(obj)
        return obj

    _add_associated_link = add_associated_link

    def add_media_link(
        self, name, url, type='media',
        mimetype=None,
        offset=None,
        on_duplicate='error'
    ):
        return self._add_associated_link(
            collection='media',
            name=name,
            url=url,
            type=type,
            offset=offset,
            mimetype=mimetype,
            on_duplicate=on_duplicate)
