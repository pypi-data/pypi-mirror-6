"""
To configure a skin we have skin configurator objects. Skin
configurators are dict-like objects that provide data to the
skin. Then skins are organized in layers each layer overriding all the
previous. To define your project create a skin and it's configurator
so that people can use your package independently.
"""

import json


class JsonSkinConfig(object):
    def __init__(self, filename):
        self.filename = filename
        self.data = None

    def get(self, attr):
        try:
            return self.data.get(attr)
        except AttributeError:
            with open(self.filename) as fd:
                self.data = json.reads(fd.read())

            return self.data.get(attr)

class Skin(object):
    """
    A hierarchy of layers of skins. There are 3 sources of attributes
    for this.

    - Previous skins
    - Current config
    - Programmatically set configs.
    """

    def __init__(self, config=None, local=None, parent_skin=None):
        """
        config needs to implement get and set. Create a configuration skin.
        """
        self.local = local
        self.config = config
        self.parent_skin = parent_skin


    def get(self, attr, parent=True, local=True, config=True, append=True):
        """
        Resolve the value of attr. Look in local storage (programmatically
        created) then in loaded configuration (from file possibly) and
        finally pass the question to the parent skin. You may omit any
        of the above lookups with the corresponding attrubute.

        If an attribute is of type list or dict and append is True
        then I will concatenate all the values I find.
        """

        ret = None
        sources = [ i for i in
                    (local and self.local,
                     config and self.config,
                     parent and self.parent_skin)
                    if i]

        for s in sources:
            # Assume attribute types are consistent
            val = s.get(attr)

            if val:
                if type(ret) is list and append:
                    ret += val
                elif type(ret) is dict and append:
                    ret.update(val)
                elif ret is None:   # If nothing useful was found.
                    ret = val

        return ret

    def append(self, attr, val, dict_like=False):
        """
        Append the attribute to the value. This only affects local
        configuration. Append will assume val is supposed to be an
        empty list if unset. If `dict_like` is True, `val` should be a
        pair of (key, value) that is set to a dict like attr value.
        """

        value = dict_like and dict([val]) or [val]
        attribute = self.local.get(attr)

        if attribute is not None:
            dict_like and attribute.update(value) or attribute.append(value)
        else:
            self.set(attr, value)

    def set(self, attr, val, depth=0):
        """
        Set the value for the programmatic interface. Depth show how deep
        in the parent skins to set it. Use `append` to populate list
        or dict variables.
        """

        if depth == 0:
            try:
                self.local[attr] = val
            except TypeError:
                self.local = dict([(attr,val)])
            else:
                if self.parent_skin is None:
                    self.parent_skin = Skin()

        else:
            self.parent_skin.set(attr, val, dapth-1)

        return val

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, val):
        return self.set(key, val)
