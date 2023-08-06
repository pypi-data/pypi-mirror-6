from pupa.core import db
from pupa.models import Organization
from .base import BaseImporter


class OrganizationImporter(BaseImporter):
    _type = 'organization'
    _model_class = Organization

    def get_db_spec(self, org):
        spec = {'classification': org.classification,
                'name': org.name,
                'parent_id': org.parent_id}

        if org.classification not in ("party", ):  # just party for now
            spec['jurisdiction_id'] = org.jurisdiction_id

        return spec

    def _resolve_org_by_chamber(self, jurisdiction_id, chamber):
        """
        This is used by the Bill importer to match an org purely based on
        ``chamber`` if it exists.
        """

        orgs = db.organizations.find({
            "classification": "legislature",
            "jurisdiction_id": jurisdiction_id,
            "chamber": chamber
        })

        if orgs.count() == 1:
            return orgs[0]  # Neato! We found one!
        elif orgs.count() == 0:
            raise ValueError("Chamber `%s' isn't giving us an org in `%s'" % (
                chamber, jurisdiction_id
            ))
        else:
            raise ValueError("Chamber `%s' isn't a unique org in `%s'" % (
                chamber, jurisdiction_id
            ))

    def resolve_json_id(self, json_id):
        # handle special party:* and jurisdiction:* ids first
        for type_, key in (('party', 'name'),
                           ('jurisdiction', 'jurisdiction_id')):
            if json_id.startswith(type_ + ':'):
                id_piece = json_id.split(':', 1)[1]
                org = db.organizations.find_one(
                    {'classification': type_, key: id_piece})
                if not org:
                    raise ValueError('attempt to create membership to unknown '
                                     + type_ + ': ' + id_piece)
                else:
                    return org['_id']

        # just resolve the normal way
        return super(OrganizationImporter, self).resolve_json_id(json_id)
