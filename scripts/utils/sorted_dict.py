class SortedDict(dict):
    """
    A dictionary that returns its items in sorted order.
    """
    def __iter__(self):
        return iter(sorted(super().items()))  # Sort items before iterating

    def items(self):
        return list(sorted(super().items()))  # Sort and return items as a list

    def keys(self):
        return list(sorted(super().keys()))  # Sort and return keys as a list

    def values(self):
        return [self[key] for key in sorted(super().keys())]  # Sort keys and get values
