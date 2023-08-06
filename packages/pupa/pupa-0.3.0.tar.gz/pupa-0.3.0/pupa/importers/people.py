from pupa.models import Person
from .base import BaseImporter, db


class PersonImporter(BaseImporter):
    _type = 'person'
    _model_class = Person

    def __init__(self, jurisdiction_id):
        super(PersonImporter, self).__init__(jurisdiction_id)
        # get list of all people w/ memberships in this org
        self.person_ids = db.memberships.find(
            {'jurisdiction_id': jurisdiction_id}).distinct('person_id')

    def prepare_object_from_json(self, obj):
        if 'party' in obj:
            obj.pop('party')
        return obj

    def get_db_spec(self, person):
        spec = {'$or': [{'name': person.name},
                        {'other_names': person.name}],
                '_id': {'$in': self.person_ids}}

        if hasattr(person, 'chamber') and person.chamber is not None:
            spec['chamber'] = person.chamber

        if hasattr(person, 'post_id') and person.post_id is not None:
            spec['post_id'] = person.post_id

        return spec
