# coding: utf-8

import os
from datetime import datetime
from pigrate import PigrateError


class Pigration(object):
    def __init__(self, id, name, script):
        self.id = id
        self.name = name
        self.script = script

    def __repr__(self):
        return '{0}-{1}.pigrate.py'.format(self.id, self.name)


class PigrationStatus(object):
    def __init__(self, id, applied_at):
        self.id = id
        self.applied_at = applied_at

    def __repr__(self):
        return '{0}'.format(self.id)


def load_config_module(basedir):
    import imp
    from uuid import uuid4
    config_path = os.path.join(basedir, 'config.py')
    if not os.path.isfile(config_path):
        raise PigrateError("directory '{0}' does not exists or is not a valid pigrate directory".format(basedir))
    return imp.load_source(uuid4().get_hex(), os.path.join(basedir, 'config.py'))


def load_config(basedir, env):
    return load_config_module(basedir).configure(env)


def load_migrations(basedir):
    import imp
    from uuid import uuid4
    result = {}
    for filename in os.listdir(basedir):
        if not filename.endswith('.pigrate.py'):
            continue
        tokens = filename[:-len('.pigrate.py')].split('-')
        if len(tokens) < 2:
            continue
        migration = Pigration(int(tokens[0]), '-'.join(tokens[1:]), imp.load_source(uuid4().get_hex(), os.path.join(basedir, filename)))
        if migration.id in result:
            raise PigrateError("'{0}' and '{1}' have the same timestamp".format(migration, result[migration.id]))
        result[migration.id] = migration
    return result


class util(object):
    @staticmethod
    def start_editor(fname):
        editor = os.environ.get('EDITOR', 'vi')
        os.system('{0} {1}'.format(editor, fname))

    @staticmethod
    def write_lines(fname, content):
        with open(fname, 'w') as f:
            f.write(content)

    @staticmethod
    def current_utc_millis():
        return int(util.total_milliseconds(datetime.utcnow() - datetime(1970, 1, 1, tzinfo=None)))

    @staticmethod
    def total_milliseconds(delta):
        return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10**6) / 1000

