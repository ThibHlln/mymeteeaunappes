import collections.abc
import toml
import os

from ._convert import parse_rga_content, parse_gar_content


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
        raise KeyError(
            f"settings {repr(tuple(keys))} were not found "
            f"in Gardenia tree"
        )


class GardeniaTree(collections.abc.Mapping):
    def __init__(self, catchment: str = None, settings: str = None):
        """Initialise a configuration tree gathering all the settings
         and parameters for the Gardenia model.

        :Parameters:

            catchment: `str`, optional
                The path to the TOML file containing the information about
                the simulation data for the catchment to simulate.

            settings: `str`, optional
                The path to the TOML file containing the settings and
                the parameters configuring the simulation with the
                Gardenia model.

        :Returns:

            `GardeniaTree`

        **Examples**

        Generating a configuration tree with default values:

        >>> t = GardeniaTree()

        Generating a configuration tree with default values except for
        those settings and parameters whose values are contained in the
        given TOML files:

        >>> t = GardeniaTree(
        ...     catchment='examples/my-example/config/bassin.toml',
        ...     settings='examples/my-example/config/reglages.toml'
        ... )
        """

        self._root = _create_branch(
            toml.load(
                os.sep.join(
                    [os.path.dirname(__file__), "default", "catchment.toml"]
                )
            )
            | toml.load(
                os.sep.join(
                    [os.path.dirname(__file__), "default", "settings.toml"]
                )
            )
        )
        if catchment:
            self._root.update(toml.load(catchment))
        if settings:
            self._root.update(toml.load(settings))

    @classmethod
    def from_rga_gar(cls, rga: str, gar: str):
        """Initialise a configuration tree from the RGA and GAR files
        of Gardenia v8.8.

        :Parameters:

            rga: `str`, optional
                The path to the RGA file containing the information about
                the simulation data for the catchment to simulate.

            gar: `str`, optional
                The path to the GAR file containing the settings and
                the parameters configuring the simulation with the
                Gardenia model.

        :Returns:

            `GardeniaTree`

        **Examples**

        >>> t = GardeniaTree.from_rga_gar(
        ...     rga='examples/my-example/config/exemple.rga',
        ...     gar='examples/my-example/config/exemple.gar'
        ... )
        """
        inst = cls()
        inst.update(
            parse_rga_content(rga) | parse_gar_content(gar)
        )
        return inst

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

    def update(self, updates: dict):
        """Update the existing values in the configuration tree.

        :Parameters:

            updates: `dict`
                The configuration updates to overwrite the existing
                values contained in the Gardenia tree.

        :Returns:

            `None`

        **Examples**

        Generating a configuration tree with default values, then
        updating some of the default values it contains:

        >>> t = GardeniaTree()
        >>> t.update(
        ...     {
        ...         'data': {
        ...             'simulation': {
        ...                 'rainfall': 'pluie.prn',
        ...                 'pet': 'etp.prn'
        ...             },
        ...             'observation': {
        ...                 'streamflow': 'debit.prn',
        ...                 'piezo-level': 'niveau.prn'
        ...             }
        ...         }
        ...     }
        ... )

        Generating a configuration tree with default values, then
        trying to update some of the default values it contains with
        erroneous dictionary keys:

        >>> t = GardeniaTree()
        >>> t.update(
        ...     {
        ...         'data': {
        ...             'simulations': {
        ...                 'rainfall': 'pluie.prn',
        ...                 'pet': 'etp.prn'
        ...             },
        ...             'observations': {
        ...                 'streamflow': 'debit.prn',
        ...                 'piezo-level': 'niveau.prn'
        ...             }
        ...         }
        ...     }
        ... )  # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        KeyError: "settings ('simulations', 'observations') were not found in Gardenia tree"
        """
        _rename_branch(self._root, updates)


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
