#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Address(dict):
    """
    Dictionary class that provides some convenience wrappers for accessing
    commonly used data elements on an Address.
    """

    def __init__(self, address_dict):
        super(Address, self).__init__(address_dict)

    @property
    def accuracy(self):
        """
        Returns a tuple represneting the location of the address in a
        GIS coords format, i.e. (longitude, latitude).
        """
        try:
            return self["accuracy"]
        except KeyError:
            return None

    @property
    def coords(self):
        """
        Returns a tuple represneting the location of the address in a
        GIS coords format, i.e. (longitude, latitude).
        """
        try:
            return (self["location"]["lng"], self["location"]["lat"])
        except KeyError:
            return None


class Location(dict):
    """
    Dictionary class that provides some convenience accessors to commonly used
    data elements.
    """

    def __init__(self, result_dict):
        super(Location, self).__init__(result_dict)
        try:
            self.best_match = Address(self["results"][0])
        # A KeyError would be raised if an address could not be parsed or
        # geocoded, i.e. from a batch address geocoding process. An index error
        # would be raised under similar circumstances, e.g. the 'results' key
        # just refers to an empty list.
        except (KeyError, IndexError):
            self.best_match = Address({})

    @property
    def coords(self):
        """
        Returns a tuple represneting the location of the first result in a
        GIS coords format, i.e. (longitude, latitude).
        """
        return self.best_match.coords

    @property
    def accuracy(self):
        """
        Returns a tuple represneting the location of the first result in an
        everyday (latitude, longitude) format.
        """
        return self.best_match.accuracy


class LocationCollection(list):
    """
    A list of Location objects, with dictionary lookup by address.
    """
    lookups = {}

    def __init__(self, results_dict):
        """
        Loads the individual responses into an internal list and uses the query
        values as lookup keys.
        """
        results = []
        for index, result in enumerate(results_dict['results']):
            results.append(Location(result['response']))
            self.lookups[result['query']] = index
        super(LocationCollection, self).__init__(results)

    def get(self, key):
        """
        Returns an individual Location by formatted address lookup
        """
        return self[self.lookups[key]]

    @property
    def coords(self):
        """
        Returns a list of tuples for the best matched coordinates.
        """
        return [l.coords for l in self]
