import simplejson as json
import requests
from .hsapi import HSApi
from .utilities import HSProperty


class Properties(HSApi):
    BASE_URL = "https://api.hubapi.com/contacts/v1/"
    PROPERTIES_URL = BASE_URL + "properties/"
    GROUPS_URL = BASE_URL + "groups/"

    @classmethod
    def get_name(self):
        return "Properties"

    def get_all(self):
        params = self.add_authentication({})
        r = requests.get(self.PROPERTIES_URL, params=params)
        if r.status_code == 200:
            return r.json()
        else:
            return False

    def get(self, name, target=None):
        if not target:
            target = self.get_all()
        for prop in target:
            if prop["name"] == name:
                return prop
        return False

    def create_property(self, hsproperty=None, **kwargs):
        if not isinstance(hsproperty, HSProperty):
            name = kwargs.get("name")
            if not name:
                raise SyntaxError("You must supply a name value")
            hsproperty = HSProperty(name=name, **kwargs)

        r = requests.put(
            self.PROPERTIES_URL + hsproperty.name,
            params=self.add_authentication({}),
            data=hsproperty.to_json(),
            headers={'content-type': 'application/json'}
        )
        if r.status_code is 200:
            return True
        else:
            return False

    def update_property(self, hsproperty=None, **kwargs):
        if not isinstance(hsproperty, HSProperty):
            name = kwargs.get("name")
            if not name:
                raise SyntaxError("you must supply a name value")
            hsproperty = HSProperty.from_json(self.get(name))

        hsproperty.update(**kwargs)

        url = self.PROPERTIES_URL + hsproperty.name

        r = requests.post(
            url,
            params=self.add_authentication({}),
            data=hsproperty.to_json(),
            headers={'content-type': 'application/json'}
        )

        if r.status_code is 200:
            return True
        else:
            return False

    def delete_property(self, name):
        url = self.PROPERTIES_URL + name
        r = requests.delete(
            url,
            params=self.add_authentication({})
        )

        if r.status_code is 204:
            return True
        else:
            return False

    def get_property_group(self, name):
        url = self.GROUPS_URL + name

        r = requests.get(
            url,
            params=self.add_authentication({}),
        )

        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            return None
        else:
            return False

    def create_property_group(self, name, **kwargs):
        hs_property = {
            "name": name.replace(" ", "_"),
            "displayName": kwargs.get("displayName", name),
            "displayOrder": kwargs.get("displayOrder", 5)
        }

        url = self.GROUPS_URL + hs_property["name"]

        r = requests.put(
            url,
            params=self.add_authentication({}),
            data=json.dumps(hs_property),
            headers={'content-type': 'application/json'}
        )
        if r.status_code in [200, 409]:
            return True
        else:
            return False

    def update_property_group(self, name, **kwargs):
        hs_property = {
            "name": name.replace(" ", "_"),
            "displayName": kwargs.get("displayName"),
            "displayOrder": kwargs.get("displayOrder")
        }

        hs_property = dict((k, v) for k, v in hs_property.iteritems() if v)

        url = self.GROUPS_URL + hs_property["name"]

        r = requests.put(
            url,
            params=self.add_authentication({}),
            data=json.dumps(hs_property),
            headers={'content-type': 'application/json'}
        )

        if r.status_code is 200:
            return True
        else:
            return False

    def delete_property_group(self, name):
        url = self.GROUPS_URL + name
        r = requests.delete(
            url,
            params=self.add_authentication({})
        )

        if r.status_code is 204:
            return True
        else:
            return False
