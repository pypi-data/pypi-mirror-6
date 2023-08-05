import UserDict
from collections import Mapping
from ordereddict import OrderedDict



class Choice(object):
    def __init__(self, value, label):
        self.value = value
        self.label = label

    def __eq__(self, other):
        if isinstance(other, Choice):
            return self.value == other.value
        return self.value == other

    def __ne__(self, other):
        return not (self == other)


class ChainMap(UserDict.DictMixin):
    """Combine multiple mappings for sequential lookup.

    For example, to emulate Python's normal lookup sequence:

        import __builtin__
        pylookup = ChainMap(locals(), globals(), vars(__builtin__))
    """
    def __init__(self, *maps):
        self.maps = maps
    def __getitem__(self, key):
        for mapping in self.maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)
    def keys(self):
        return list(self.iterkeys())
    def iterkeys(self):
        return (k for m in self.maps for k in m.iterkeys())
    def values(self):
        return list(self.itervalues())
    def itervalues(self):
        return (v for m in self.maps for v in m.itervalues())


class Choices(OrderedDict):
    def __getitem__(self, key):
        try:
            OrderedDict.__getitem__(self, key)
        except KeyError:
            for choice in self.choices:
                if isinstance(choice, Mapping):
                    try:
                        return choice[key]
                    except KeyError:
                        pass
        raise KeyError(key)


class Choices2(object):
    def __init__(self, choices, label=''):
        self.choices = list(map(
            choice_factory,
            choices
        ))
        self.label = label

    def __add__(self, other):
        if isinstance(other, Choice):
            return Choices(self.choices + [other])
        elif isinstance(other, Choices):
            return ChoicesChain(self, other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, Choice):
            return Choices([other] + self.choices)
        return NotImplemented

    @property
    def values(self):
        for choice in self.choices:
            if isinstance(choice, Choices):
                for value in choice.values:
                    yield value
            else:
                yield choice.value

    def __len__(self):
        return len(self.choices)

    def __getitem__(self, key):
        for choice in self.choices:
            if isinstance(choice, Choice):
                if choice.key == six.text_type(key):
                    return choice.value
            else:
                try:
                    return choice[key]
                except KeyError:
                    pass
        raise KeyError(key)

    def __iter__(self):
        for choice in self.choices:
            yield choice

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, list(self.choices))
