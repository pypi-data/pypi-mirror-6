import requests


class PocoLocation(object):
    id = None
    suburb = None
    area = None
    postal = None
    street = None

    def __unicode__(self):
        return '{0} - {1}'.format(self.suburb, self.area)

    def __str__(self):
        return self.__unicode__()

    @classmethod
    def from_dict(cls, dict):
        location = PocoLocation()
        location.id = dict.get('id', '')
        location.suburb = dict.get('suburb', '')
        location.area = dict.get('area', '')
        location.postal = dict.get('postal' ,'')
        location.street = dict.get('street', '')
        return location


class PocoSearcher(object):
    @classmethod
    def _perform_search(cls, term):
        payload = {'search': term}
        r = requests.get('http://poco.co.za/api/locations/', params=payload)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            r.raise_for_status()

    @classmethod
    def results_as_objects(cls, term):
        json = cls._perform_search(term)
        locations = [PocoLocation.from_dict(result) for result in json]
        return locations

    @classmethod
    def results_as_dicts(cls, term):
        json = cls._perform_search(term)
        return json
