__author__ = 'Diego Garcia'

from ptracking_utils import PyTrackingBR, PyTrackingUSPS


BRAZIL = 'BR'
UNITED_STATES = 'US'


class PyTracking:

    def __init__(self, my_location):
        self.__my_location = my_location

    @property
    def my_location(self):
        return self.__my_location

    @my_location.setter
    def my_location(self, value):
        self.__my_location = value.upper()

    def __tracking_method_by_location(self, location):
        if location == BRAZIL:
            return PyTrackingBR.get_tracking
        elif location == UNITED_STATES:
            return PyTrackingUSPS.get_tracking

    def __extend_tracking(self, location, cod, data):
        m = self.__tracking_method_by_location(location)
        if m:
            data["tracking"].extend(m(cod))
        return True

    def tracking(self, cod):
        data = {"tracking": []}
        self.__extend_tracking(self.__my_location, cod, data)
        if self.__my_location != cod[-2:].upper():
            self.__extend_tracking(cod[-2:].upper(), cod, data)

        return data