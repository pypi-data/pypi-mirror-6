#-*- coding: utf-8 -*-
class Error(Exception):
    pass

class Timeout(Error):
    pass

class TooLong(Error):
    pass
