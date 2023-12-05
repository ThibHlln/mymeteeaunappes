import collections.abc
import toml
import os
import warnings


def _create_branch(dictionary):
    branch = {}
    for key, val in dictionary.items():
        if isinstance(val, dict):
            branch[key] = _create_branch(val)
        else:
            branch[key] = val
    return _GardeniaBranch(branch)


def _rename_branch(branch, dictionary):
    keys = list(dictionary.keys())

    for b_key, b_val in branch.items():
        if b_key in dictionary:
            keys.remove(b_key)

            d_val = dictionary[b_key]

            if isinstance(b_val, _GardeniaBranch):
                if isinstance(d_val, dict):
                    _rename_branch(branch[b_key], d_val)
                else:
                    raise TypeError(
                        f"{repr(b_key)} is a Gardenia tree branch, "
                        f"it needs to be assigned a dictionary"
                    )
            elif isinstance(b_val, (int, float, str, bool)):
                if isinstance(d_val, (int, float, str, bool)):
                    branch[b_key] = d_val
                else:
                    raise TypeError(
                        f"{repr(b_key)} is a Gardenia tree leaf, "
                        f"it needs to be assigned a scalar"
                    )
            else:
                raise TypeError(
                    f"unsupported type for Gardenia setting "
                    f"{repr(b_key)}"
                )

    if keys:
        warnings.warn(
            f"settings {repr(tuple(keys))} were not found "
            f"in Gardenia tree"
        )


class GardeniaTree(collections.abc.Mapping):
    def __init__(self, catchment: str = None, settings: str = None):
        self._root = _create_branch(
            toml.load(os.sep.join([os.path.dirname(__file__), "default", "catchment.toml"]))
            | toml.load(os.sep.join([os.path.dirname(__file__), "default", "settings.toml"]))
        )
        if catchment:
            self._root.update(toml.load(catchment))
        if settings:
            self._root.update(toml.load(settings))

    def __str__(self):
        return self._root.__str__()

    def __repr__(self):
        return self._root.__repr__()

    def __getitem__(self, key):
        return self._root[key]

    def __len__(self):
        return len(self._root)

    def __iter__(self):
        return iter(self._root)

    def update(self, dictionary: dict):
        _rename_branch(self._root, dictionary)


class _GardeniaBranch(collections.abc.MutableMapping):
    def __init__(self, settings: dict):
        self._settings = settings

    def __getitem__(self, key):
        try:
            return self._settings[key]
        except KeyError:
            raise KeyError(
                f"{repr(key)} is not a Gardenia setting"
            )

    def __setitem__(self, key, value):
        if key not in self._settings:
            raise KeyError(
                f"{repr(key)} is not a Gardenia setting"
            )
        _rename_branch(self._settings, {key: value})

    def __delitem__(self, key):
        raise RuntimeError(
            f"Gardenia settings cannot be deleted"
        )

    def __iter__(self):
        return iter(self._settings)

    def __len__(self):
        return len(self._settings)

    def __str__(self):
        return str(self._settings)

    def __repr__(self):
        return repr(self._settings)
