
"""Search for a key inside a dictionary, visiting it in a recursive way
and return the value of this key.

d: dictionary to search into
kname: key name to search for
"""

def dict_search_value(d, kname):
    if type(d)==dict:
        for k,v in d.items():
            if type(v)==dict:
                value = dict_search_value(v, kname)
                if value:
                    return value
            if type(v)==list:
                if len(v) > 0:
                    if type(v[0])==dict:
                        value = dict_search_value(v[0], kname)
                        if value:
                            return value
            if k==kname:
                return v


"""Given a list of fields/keys and two dictionaries, it searches for each key in both
dictionaries and assert as equal the found value.

fields: a list of fields/keys to verify
dict_1: first dictionary
dict_2: second dictionary
"""

def compare_assert_dicts(self, fields, dict_1, dict_2):
        for f in fields:
            value_dict1 = dict_search_value(dict_1, f)
            value_dict2 = dict_search_value(dict_2, f)
            self.assertEqual(value_dict1, value_dict2,
                "Returned value: %s, expected value: %s" % (str(value_dict1), str(value_dict2)))
