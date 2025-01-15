class SortedDict(dict):
    """
    A dictionary that returns its items in sorted order, even recursively.
    """

    def __iter__(self):
        # Sort items before iterating
        return iter(sorted(self.items_recursive()))

    def items(self):
        # Sort and return items as a list
        return list(sorted(self.items_recursive()))

    def keys(self):
        # Sort and return keys as a list
        return list(sorted(self.keys_recursive()))

    def values(self):
        # Sort keys and get values
        return [self[key] for key in sorted(self.keys_recursive())]

    def items_recursive(self):
        # Recursively sort items
        for key, value in sorted(super().items()):
            if isinstance(value, dict):
                value = SortedDict(value)  # Create a new SortedDict instance
                yield key, value.items()
            elif isinstance(value, list):
                value = [sorted(value)]
                yield key, value
            else:
                yield key, value

    def keys_recursive(self):
        for key, _ in sorted(self.items_recursive()):
            yield key



#####################################
# Example:
#
# Note: Elements in an array must be of the same type to be comparable
if __name__ == "__main__":

    test = SortedDict({
        'a': 1,
        'c': 2,
        'b': 66,
        'f': "abc",
        'd': {
            'mensch': 1,
            'katze': 2,
            'ufo': 3,
            'flugzeug': [
                1, 5, 9, 2
            ]
        }
    })

    print(test.items())