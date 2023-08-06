# coding: utf-8


class config(object):
    def __init__(self, targets):
        self.targets = targets


class PigrateError(Exception):
    pass

