import httplib
import re


class RUDict(dict):

    def __init__(self, *args, **kw):
        super(RUDict, self).__init__(*args, **kw)

    def update(self, E=None, **F):
        if E is not None:
            if 'keys' in dir(E) and callable(getattr(E, 'keys')):
                for k in E:
                    if k in self:  # existing ...must recurse into both sides
                        self.r_update(k, E)
                    else:  # doesn't currently exist, just update
                        self[k] = E[k]
            else:
                for (k, v) in E:
                    self.r_update(k, {k: v})

        for k in F:
            self.r_update(k, {k: F[k]})

    def r_update(self, key, other_dict):
        if isinstance(self[key], dict) and isinstance(other_dict[key], dict):
            od = RUDict(self[key])
            nd = other_dict[key]
            od.update(nd)
            self[key] = od
        else:
            self[key] = other_dict[key]


def expand(kwargs):
    """
        Transforms dicts with keys in the format key_subkey
        or key.subkey, to a nested version:

        >>> expand({'key.subkey': 'value'})
        {'key': {'subkey': 'value'}}
    """
    expanded = {}
    for key, value in kwargs.items():
        subkeys = re.findall(r'([^_\.]+)[_$]?', key)
        leaf = expanded
        for subkey in subkeys[:-1]:
            leaf = leaf.setdefault(subkey, {})
        leaf[subkeys[-1]] = value
    return expanded


def patch_send():
    """
        PATCH for allowing raw debugging of requests' requests
    """
    old_send = httplib.HTTPConnection.send

    def new_send(self, data):
        print '\n' + data + '\n'
        return old_send(self, data)

    httplib.HTTPConnection.send = new_send
