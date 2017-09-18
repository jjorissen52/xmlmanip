import xmltodict, json
import xml.etree.ElementTree as ET

from collections import OrderedDict
from bs4 import BeautifulSoup

def try_compare(obj, key, comparison, search_value, override_value=""):
    value = override_value if override_value else obj[key]
    try:
        return getattr(value, comparison)(search_value)
    except KeyError:
        return False
    except NotImplemented:
        return False


class BadSchemaError(BaseException):
    pass


class BadTagError(BaseException):
    pass


class SearchableList(list):
    def search(self, *args, **kwargs):
        comparison = f"__{kwargs.get('comparison')}__" if kwargs.get('comparison') else '__eq__'
        try:
            key, value = args[0], args[1]
        except IndexError:
            for key in kwargs.keys():
                if '__' in key:
                    comparison = f'__{key.split("__")[1]}__'
                key, value = key.split("__")[0], kwargs[key]
        return SearchableList(list(filter(lambda x: try_compare(x, key, comparison, value), self)))

    def _locate(self, *args, path_string="", paths=None, **kwargs):
        comparison = f"__{kwargs.get('comparison')}__" if kwargs.get('comparison') else '__eq__'
        try:
            search_key, search_value = args[0], args[1]
        except IndexError:
            for key in kwargs.keys():
                if '__' in key:
                    comparison = f'__{key.split("__")[1]}__'
                search_key, search_value = key.split("__")[0], kwargs[key]

        for i in range(len(self)):
            if issubclass(type(self[i]), dict):
                for key, value in self[i].items():
                    new_path_string = f'{path_string}__{i}__{key}'
                    if key == search_key:
                        if isinstance(value, str) and isinstance(search_value, str):
                            value, search_value = value.upper(), search_value.upper()
                        if try_compare(self[i], key, comparison, search_value, override_value=value):
                            paths.append(new_path_string)
                    if '_locate' in self[i][key].__dir__():
                        self[i][key]._locate(*args, paths=paths, path_string=new_path_string, **kwargs)

    def locate(self, *args, **kwargs):
        """
        user-friendly search function that calls _locate
        """
        paths, path_string = [], ""
        self._locate(*args, paths=paths, path_string=path_string, **kwargs)
        return paths

    def _retrieve(self, obj, keys):
        # test to see if the object has a __getitem__ method and if it doesnt we return
        retrieval_method = getattr(obj, '__getitem__', None)
        if retrieval_method:
            if len(keys) != 0 and not isinstance(obj, str):
                current_key = keys.pop(0)
                if issubclass(type(obj), list):
                    try:
                        new_obj = retrieval_method(int(current_key))
                    except ValueError:
                        raise ValueError(f'_retrieve expected an int as an index to a list,'
                                         f' got str "{current_key}" instead. Are you sure your key path is'
                                         'valid?')
                else:
                    new_obj = retrieval_method(current_key)
                return self._retrieve(new_obj, keys)
            else:
                return obj
        else:
            return obj

    def retrieve(self, string="", from_string=True, keypath_list=None):
        keypath_list = string[2:].split("__")
        return self._retrieve(self, keypath_list)

    def __getitem__(self, key):
        item = super(SearchableList, self).__getitem__(key)
        if isinstance(item, OrderedDict):
            return SchemaInnerDict(item)
        if isinstance(item, list):
            return SearchableList(item)
        else:
            return item


class SchemaInnerDict(OrderedDict):
    def _locate(self, *args, paths=None, path_string="", **kwargs):
        """
        modifies the list "paths" to be returned via the "locate" method
        """
        comparison = f"__{kwargs.get('comparison')}__" if kwargs.get('comparison') else '__eq__'
        try:
            search_key, search_value = args[0], args[1]
        except IndexError:
            for key in kwargs.keys():
                if '__' in key:
                    comparison = f'__{key.split("__")[1]}__'
                search_key, search_value = key.split("__")[0], kwargs[key]

        for key, value in self.items():
            new_path_string = f'{path_string}__{key}'
            if key == search_key:
                if isinstance(value, str) and isinstance(search_value, str):
                    value, search_value = value.upper(), search_value.upper()
                if getattr(value, comparison)(search_value):
                    paths.append(new_path_string)
            if '_locate' in self[key].__dir__():
                self[key]._locate(*args, paths=paths, path_string=new_path_string, **kwargs)

    def locate(self, *args, **kwargs):
        """
        user-friendly search function that calls _locate
        """
        paths, path_string = [], ""
        self._locate(*args, paths=paths, path_string=path_string, **kwargs)
        return paths

    def _retrieve(self, obj, keys):
        # test to see if the object has a __getitem__ method and if it doesnt we return
        retrieval_method = getattr(obj, '__getitem__', None)
        if retrieval_method:
            if len(keys) != 0 and not isinstance(obj, str):
                current_key = keys.pop(0)
                if issubclass(type(obj), list):
                    try:
                        new_obj = retrieval_method(int(current_key))
                    except ValueError:
                        raise ValueError(f'_retrieve expected an int as an index to a list,'
                                         f' got str "{current_key}" instead. Are you sure your key path is'
                                         'valid?')
                else:
                    new_obj = retrieval_method(current_key)
                return self._retrieve(new_obj, keys)
            else:
                return obj
        else:
            return obj

    def retrieve(self, string="", from_string=True, keypath_list=None):
        keypath_list = string[2:].split("__")
        return self._retrieve(self, keypath_list)

    def to_json(self):
        return json.dumps(self, indent=2)

    def __str__(self):
        return f'{self.to_json()}'

    def __getitem__(self, key):
        item = super(SchemaInnerDict, self).__getitem__(key)
        if isinstance(item, list):
            return SearchableList(item)
        if issubclass(type(item), dict):
            return SchemaInnerDict(item)
        else:
            return item


class XMLSchema(SchemaInnerDict):
    def is_valid_schema(self, schema):
        root = ET.fromstring(schema)
        print(root.tag, )

    def _to_dict(self):
        return xmltodict.parse(self.original_string)

    def __getitem__(self, key):
        item = super(type(self), self).__getitem__(key)
        if isinstance(item, list):
            return SearchableList(item)
        elif isinstance(item, dict):
            return SchemaInnerDict(item)
        else:
            return item

    def __init__(self, schema):
        self.original_string = schema
        self.schema = ET.fromstring(schema)
        super(XMLSchema, self).__init__(self._to_dict())


def inject_tags(schema, parent_tag="", injection_index=0, creative=True, **tags):
    """
    Injects a new tag with the specified content at the indicated parent and index
    :param schema: xml_string or xml.etree.ElementTree.Element where the tags are to be injected
    :param parent_tag: name of the parent tag where indicated tags are to be injected (leave blank for injecting to top level of schema)
    :param injection_index: indicates the index of where the tags will be inserted into their parents. 0 for first, 1 for second, so on
    :param tags: kwargs indicating tags and text of tags:
                 * thing="1" --->
                        <thing>1</thing>,
                 * provider={"text":"some text", "action":"info"} --->
                        <provider action="info">some text</provider>
                 * provider__1={"text":"some text", "action":"info"},
                   provider__2={"text":"other text", "action":"info"} --- >
                        <provider action="info">some text</provider>
                        <provider action="info">other text</provider>
    :return: modified xml_string with newly injected tags
    """
    # if the object is not an element, we treat it as an xml string
    if not isinstance(schema, ET.Element):
        schema = ET.fromstring(schema)
    # if no parent_tag is specified, the root is the parent
    if not parent_tag:
        parent = schema
    # if the specified parent_tag exists then that is our active parent
    elif schema.find(parent_tag) is not None:
        parent = schema.find(parent_tag)
    else:
        raise BadSchemaError(f"No <{parent_tag}/> tag included in the given schema.")
    for i, kword in enumerate(tags.keys()):
        # if creative then add a new tag on tag collision, if not creative then pass
        if parent.find(kword) is not None and not creative:
            pass
        else:
            if isinstance(tags[kword], dict):
                if '__inner_tag' in tags[kword].keys():
                    inner_tag = tags[kword].pop('__inner_tag')
                else:
                    inner_tag = ""
                if 'text' in tags[kword].keys() and not inner_tag:
                    text = tags[kword].pop('text')
                elif 'text' in tags[kword].keys():
                    raise BadTagError('Elements that contain elements may not also contain text'
                                              ' attributes (XML formatting does not allow it.)')
                else:
                    text = ""
                new_tag = ET.Element(kword.split('__')[0], tags[kword])

            elif isinstance(tags[kword], str):
                inner_tag = ""
                text = tags[kword]
                new_tag = ET.Element(kword.split('__')[0])
            else:
                raise TypeError(f"Passed kwarg '{kword} is {type(tags[kword])}. Must be str or dict.'")
            new_tag.text = text
            parent.insert(injection_index, new_tag)
            if inner_tag:
                inject_tags(new_tag, **inner_tag)
            injection_index += 1
    try:
        schema_str = ET.tostring(schema)
    except TypeError as e:
        raise TypeError(f"One of tags you attempted to inject is not a supported type: {e}")

    return schema_str


def print_xml(schema_str):
    print(BeautifulSoup(schema_str, "xml").prettify())