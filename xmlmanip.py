import xmltodict, json
import xml.etree.ElementTree as ET

from collections import OrderedDict


def try_compare(obj, key, comparison, search_value, override_value=""):
    value = override_value if override_value else obj[key]
    try:
        return getattr(value, comparison)(search_value)
    except KeyError:
        return False
    except NotImplemented:
        return False


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