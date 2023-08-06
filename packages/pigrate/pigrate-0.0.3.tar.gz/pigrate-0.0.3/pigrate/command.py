# coding: utf-8

import os
import time
from pigrate import PigrateError, internal


CONFIG_PY_TEMPLATE = """
# coding: utf-8

from pigrate import config, driver

def configure(env):
    if env == 'local':
        return config({
            'default': driver.mysql(host="localhost",
                port=3306,
                db="db",
                user="user",
                passwd="passwd"),
        })
""".strip() + "\n"


MIGRATION_PY_TEMPLATE = """
# coding: utf-8

target = 'default'
""".strip() + "\n"


NOT_USED = None


def command(fn):
    fn.is_command = True
    return fn


def _ensure_pig_status_table(config):
    for target_name, target_driver in config.targets.iteritems():
        if target_driver.status() is None:
            ans = raw_input("Target '{0}' does not have a '_pig_status' table for storing migration status. Create now? [Y/n]: ".format(target_name))
            if ans.lower() not in ("", "y", "yes"):
                raise PigrateError("table '_pig_status' does not exist in target '{0}'".format(target_name))
            target_driver.pigratize()


def _collect_migration_statuses(config):
    statuses = []
    for target_name, target_driver in config.targets.iteritems():
        for status in (target_driver.status() or []):
            statuses.append((status, target_name))
    return statuses


@command
def init(basedir, env=NOT_USED, noedit=False):
    if os.path.isdir(basedir):
        raise PigrateError("directory '{0}' already exists".format(basedir))
    os.mkdir(basedir)

    fname = os.path.join(basedir, 'config.py')
    internal.util.write_lines(fname, CONFIG_PY_TEMPLATE)
    if not noedit:
        internal.util.start_editor(fname)


@command
def new(name, basedir, env, noedit=False):
    internal.load_config_module(basedir) # validate schema directory

    # avoid timestamp collision
    id = internal.util.current_utc_millis()
    while id in internal.load_migrations(basedir):
        id = id + 1
    time.sleep(0.001)

    fname = os.path.join(basedir, '{0}-{1}.pigrate.py'.format(id, name))
    internal.util.write_lines(fname, MIGRATION_PY_TEMPLATE)
    if not noedit:
        internal.util.start_editor(fname)


@command
def up(basedir, env, interactive=False):
    config = internal.load_config(basedir, env)
    _ensure_pig_status_table(config)

    migs = internal.load_migrations(basedir)
    statuses = _collect_migration_statuses(config)

    for id in sorted(migs.keys()):
        mig = migs[id]
        if filter(lambda s: s[0].id == id and s[1] == mig.script.target, statuses):
            continue # already applied

        if not interactive or raw_input('Apply {0}? [Y/n]: '.format(mig)).lower() in ("", "y", "yes"):
            config.targets[mig.script.target](mig)
        else:
            break


@command
def down(basedir, env, interactive=False):
    config = internal.load_config(basedir, env)
    _ensure_pig_status_table(config)

    migs = internal.load_migrations(basedir)
    statuses = _collect_migration_statuses(config)

    for id in sorted(migs.keys(), reverse=True):
        mig = migs[id]
        if not filter(lambda s: s[0].id == id and s[1] == mig.script.target, statuses):
            continue # not applied yet

        if not interactive or raw_input('Undo {0}? [Y/n]: '.format(mig)).lower() in ("", "y", "yes"):
            config.targets[mig.script.target](mig, undo=True)
        break
    else:
        if raw_input("Nothing to undo. Would you like to remove '_pig_status' table? It is vital to pigrate. [y/N]: ").lower() in ("y", "yes"):
            for target_name, target_driver in config.targets.iteritems():
                target_driver.unpigratize()

@command
def status(basedir, env, interactive=NOT_USED):
    config = internal.load_config(basedir, env)

    migs = internal.load_migrations(basedir)
    statuses = _collect_migration_statuses(config)
    ids = sorted(set(map(lambda s: s[0].id, statuses)) | set(migs.keys()))

    def _status_message(id):
        mig = migs.get(id, None)
        statuses_ = filter(lambda s: s[0].id == id, statuses)

        expected_target = mig.script.target if mig and hasattr(mig.script, 'target') else None
        def _judge(actual_target):
            if expected_target is None:
                return '??'
            if expected_target == actual_target:
                return 'ok'
            return '??'

        if not statuses_:
            return "pending"
        elif len(statuses_) == 1:
            return "applied to '{0}'({1})".format(statuses_[0][1], _judge(statuses_[0][1]))
        else:
            return "applied to {0}".format(', '.join(map(lambda s: "'{0}'({1})".format(s[1], _judge(s[1])), statuses_)))

    column_width_file = max(max(map(lambda m: len(str(m)), migs.values())) if migs else 0, len("(missing)"))
    column_width_id = max(max(map(lambda i: len(str(i)), ids)) if ids else 0, len("Id"))
    column_width_status = max(max(map(lambda i: len(_status_message(i)), ids)) if ids else 0, len("Status"))

    print '{0} | {1} | {2}'.format('Id'.ljust(column_width_id), 'File'.ljust(column_width_file), 'Status')
    print '{0}-+-{1}-+-{2}'.format('--'.ljust(column_width_id, '-'), '----'.ljust(column_width_file, '-'), '------'.ljust(column_width_status, '-'))
    for id in ids:
        mig = migs.get(id, None)
        print '{0} | {1} | {2}'.format(str(id).ljust(column_width_id), str(mig if mig else '(missing)').ljust(column_width_file), _status_message(id))

