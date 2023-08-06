# tab-width: 4; indent-tabs-mode: nil;
#!/usr/bin/env python
'''
This module provides helpers for creating and managing databases.

This technique may be helpful in production code, and it's especially relevant
to functional tests which depend on test databases.

Note that this package is more "persistent" than you might expect. The
Postgres
servers created by this module will remain alive after this module terminates.
A future instance of this module, running in a different process, can adopt
that postgres server and manage it without a hitch.

Thus this module can create a postgres server at one time, then be reborn in
another process at another time and continue to manage that server. It can
also
manage postgres servers and databases that were created elsewhere.

This capability is useful for production code, where many things may happen
between server launch and server shutdown.

The key to this flexibility is that the DBMS can be located by pathname to the
storage directory. That pathname handle leads to the server's PID, status,
etc.

Warning: These methods are inconsistent about the exceptions that they raise.
Some errors provoke OSError, whereas other similar errors might provoke
CalledProcessError or RuntimeError.  This should be made consistent.
'''

"""
The type checking machinery here is something of an experiment, using the
`typecheck` package. If it turns out to be a headache,
disable it by overriding the @accepts decorator, turning it into a no-op.
"""

from __future__ import absolute_import, print_function

import glob
import os
import shutil
import signal
import subprocess
import tempfile
import time
import importlib
import itertools
import types
import re

from typecheck import accepts, IsOneOf, Self
from typecheck.typeclasses import String

from . import paths

DEV_NULL = open(os.path.devnull, 'r+')


class NotInitializedError(Exception):
    "An exception raised when an uninitialized DBMS is asked to do something"

class PostgresDatabase(object):
    '''
    Typical usage:
        db = PostgresDatabase(db_name='test_db', user='test_user')
        db.create_user()
        db.create('CREATE TABLE foo (value text not null); ...')
        db.sql('Ad-hoc string of SQL...')
        ...
        db.drop()
        db.drop_user()
    '''
    @accepts(Self(), String, String, String, IsOneOf(int, String), String,
        String)
    def __init__(self, db_name, user='pmxtest', host='localhost',
            port=5432, superuser='postgres', template='template1'):
        '''Manage a database.  (Not a DBMS; just a database.)

        This method doesn't do anything; it just remembers its params for use
        by subsequent method calls.

        @param db_name: The name of the database.
        @type schema: str

        Note: Tested with postgresql 8.3

        WARNING: Some methods are open to SQL injection attack; don't pass
        unvetted values of <db_name>, <user>, etc.
        '''
        # Mild defense against SQL injection attacks.
        assert "'" not in user
        assert "'" not in db_name
        assert "'" not in template

        self.db_name = db_name
        self.user = user
        self.host = host
        self.port = str(port)
        self.superuser = superuser
        self.template = template

    def __repr__(self):
        return ('PostgresDatabase(db_name=%s, user=%s, host=%s, port=%s,'
            ' superuser=%s, template=%s)') % (self.db_name, self.user,
            self.host,
            self.port, self.superuser, self.template)

    __str__ = __repr__

    @accepts(Self(), IsOneOf(String, types.NoneType))
    def create(self, sql=None):
        """CREATE this DATABASE.

        @param sql: (Optional) A string of psql (such as might be generated
        by pg_dump); it will be executed by psql(1) after creating the
        database.
        @type sql: str

        @rtype: None
        """
        create_sql = 'CREATE DATABASE {self.db_name} WITH OWNER {self.user}'
        create_sql = create_sql.format(**vars())
        self.super_psql(['-c', create_sql])
        if sql: self.psql_string(sql)

    def psql_string(self, sql):
        """
        Evaluate the sql file (possibly multiple statements) using psql.
        """
        argv = [PSQL, '--quiet', '-U', self.user, '-h', self.host, '-p',
            self.port, '-f', '-', self.db_name]
        popen = subprocess.Popen(argv, stdin=subprocess.PIPE)
        popen.communicate(input=sql.encode('utf-8'))
        if popen.returncode != 0:
            raise subprocess.CalledProcessError(popen.returncode, argv)

    def create_user(self):
        """
        CREATE this USER.

        Beware that this method is open to SQL injection attack.  Don't use
        unvetted values of self.user.
        """
        #statement = '''DO $$
        #BEGIN
        #IF (SELECT count(*) FROM pg_user WHERE usename = '%s') = 0 THEN
        #create user %s;
        #END IF;
        #END;
        #$$ language plpgsql;''' % (self.user, self.user)
        #self.super_psql(['-f', '-'])  XXX Need to set up a pipe to STDIN, like .create() does
        self.super_psql(['-c', "CREATE USER %s" % self.user])

    def drop(self):
        """DROP this DATABASE, if it exists."""
        self.super_psql(['-c', "DROP DATABASE IF EXISTS %s" % self.db_name])

    # For legacy compatibility.
    drop_if_exists = drop

    def drop_user(self):
        """DROP this USER, if it exists."""
        self.super_psql(['-c', "DROP USER IF EXISTS %s" % self.user])

    @accepts(Self(), [String])
    def psql(self, args):
        """Invoke psql, passing the given command-line arguments.

        Typical <args> values: ['-c', <sql_string>] or ['-f', <pathname>].

        Connection parameters are taken from self.  STDIN, STDOUT,
        and STDERR are inherited from the parent.

        WARNING: This method uses the psql(1) program, which ignores SQL
        errors
        by default.  That hides many real errors, making our software less
        reliable.  To overcome this flaw, add this line to the head of your
        SQL:
            "\set ON_ERROR_STOP TRUE"

        @return: None. Raises an exception upon error, but *ignores SQL
        errors* unless "\set ON_ERROR_STOP TRUE" is used.
        """
        argv = [PSQL, '--quiet', '-U', self.user, '-h', self.host, '-p',
            self.port] + args + [self.db_name]
        subprocess.check_call(argv)

    def sql(self, input_string, *args):
        """Execute a SQL command using the Python DBI directly.

        Connection parameters are taken from self.  Autocommit is in effect.

        Example: .sql('SELECT %s FROM %s WHERE age > %s', 'name', 'table1',
            '45')

        @param input_string: A string of SQL.  May contain %s or %(name)s
        format specifiers; they are replaced with corresponding values taken
        from args.

        @param args: zero or more parameters to interpolate into the string.
        Note that they're passed individually, not as a single tuple.

        @return: Whatever .fetchall() returns.
        """
        """
        # I advise against using sqlalchemy here (it's more complicated than
        # what we need), but here's an implementation Just In Case.  -jps
        import psycopg2, sqlalchemy
        engine = sqlalchemy.create_engine(
            'postgres://%s@%s:%s/%s' %
            (self.user, self.host, self.port, self.db_name),
            echo=False, poolclass=sqlalchemy.pool.NullPool)
        connection = engine.connect()
        result = connection.execute(input_string, *args)
        try:
            # sqlalchemy 0.6.7 offers a result.returns_rows attribute, but
            # no prior version offers anything comparable.  A tacky
            # workaround...
            try:
                return result.fetchall()
            except psycopg2.ProgrammingError:
                return None
        finally:
            result.close()
            connection.close()
        """
        psycopg2 = importlib.import_module('psycopg2')
        importlib.import_module('psycopg2.extensions')
        connection = psycopg2.connect(user=self.user, host=self.host,
            port=self.port, database=self.db_name)
        connection.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            cursor = connection.cursor()
            cursor.execute(input_string, args)
            # No way to ask whether any rows were returned, so just try it...
            try:
                return cursor.fetchall()
            except psycopg2.ProgrammingError:
                return None
        finally:
            connection.close()

    @accepts(Self(), [String])
    def super_psql(self, args):
        """Just like .psql(), except that we connect as the database superuser
        (and we connect to the superuser's database, not the user's database).
        """
        argv = [PSQL, '--quiet', '-U', self.superuser, '-h', self.host, '-p',
            self.port] + args
        subprocess.check_call(argv)


class PostgresServer(object):
    @accepts(Self(), String, IsOneOf(int, String),
        IsOneOf(String, types.NoneType), String)
    def __init__(self, host='localhost', port=5432, base_pathname=None,
            superuser='postgres'):
        """This class represents a DBMS server.

        This class can represent either
          - a postgres instance that's already up and running as part of
            the basic infrastructure, or
          - a temporary, local, homegrown instance that only you know about.
        It's your choice.  It depends on whether you call the .initdb()
        and .start() methods.

        @param base_pathname: (Optional) The directory wherein the server
        will store all files. If None or '', a temporary directory will be
        used.
        @type base_pathname: (str, None)

        @param schema: (Optional) A string of SQL which creates a schema,
        such as might be generated by pg_dump.
        @type schema: (str, None)

        Note: Tested with postgresql 8.3.7
        """
        self.host = str(host)
        self.port = str(port)
        self.base_pathname = base_pathname
        self.superuser = superuser

    def __repr__(self):
        tmpl = ('PostgresServer(host={host}, port={port}, '
            'base_pathname={base_pathname}, superuser={superuser})')
        return tmpl.format(**vars(self))

    def __str__(self):
        tmpl = 'PostgreSQL server at %s:%s (with  storage at %s)'
        return tmpl % (self.host, self.port, self.base_pathname)

    def destroy(self):
        """Undo the effects of initdb.

        Destroy all evidence of this DBMS, including its backing files.
        """
        self.stop()
        if self.base_pathname is not None:
            self._robust_remove(self.base_pathname)

    @staticmethod
    def _robust_remove(path):
        """
        Remove the directory specified by `path`. Because we can't determine
        directly if the path is in use, and on Windows, it's not possible to
        remove a path if it is in use, retry a few times until the call
        succeeds.
        """
        tries = itertools.count()
        max_tries = 50
        while os.path.isdir(path):
            try:
                shutil.rmtree(path)
            except WindowsError:
                if next(tries) >= max_tries:
                    raise
                time.sleep(0.2)

    def initdb(self, quiet=True):
        """Bootstrap this DBMS from nothing.

        If you're running in an environment where the DBMS is provided as part
        of the basic infrastructure, you probably don't want to call this
        method!

        @param quiet: Should we operate quietly, emitting nothing if things go
        well?
        """
        # Defining base_pathname is deferred until this point because we don't
        # want to create a temp directory unless it's needed.  And now it is!
        if self.base_pathname in [None, '']:
            self.base_pathname = tempfile.mkdtemp()
        if not os.path.isdir(self.base_pathname):
            os.mkdir(self.base_pathname)
        stdout = DEV_NULL if quiet else None
        # The database superuser needs no password at this point(!).
        subprocess.check_call([INITDB, '--auth=trust', '--username',
            self.superuser, '--pgdata', self.base_pathname], stdout=stdout)

    @accepts(Self(), int)
    def is_running(self, tries=10):
        """Is this server currently running?

        The postgres tools have critical windows during which they give
        misbehave
        or give the wrong answer.  If postgres was just launched:
            - it might not yet appear to be running, or
            - pg_ctl might think that it's running, but psql might not yet
              be able to connect to it, or
            - it might be about to abort because of a configuration problem,
            - or all three!  It might be starting up, but about to abort.
        Sadly, it's not easy to make a declaration about state if we just
        started
        or stopped postgres.  To increase confidence, we'll make repeated
        checks,
        and declare our decision only after <tries> consecutive measurements
        agree.
        """
        # We can't possibly be running if our base_pathname isn't defined.
        if not self.base_pathname:
            return False

        if tries < 1:
            raise ValueError('tries must be > 0')

        cmd = [PG_CTL, 'status', '-D', self.base_pathname]
        votes = 0
        while abs(votes) < tries:
            time.sleep(0.1)
            running = (subprocess.call(cmd, stdout=DEV_NULL) == 0)
            if running and votes >= 0:
                votes += 1
            elif not running and votes <= 0:
                votes -= 1
            else:
                votes = 0

        if votes > 0:
            # postgres now talks to pg_ctl, but it might not yet be listening
            # for connections from psql.  We don't want to claim that postgres
            # is up until psql is able to connect.  (It occasionally takes
            # 5-10 seconds for postgresql to start listening!)
            cmd = [PSQL, '-h', self.host, '-p', self.port, '-U',
                self.superuser]
            for i in range(50, -1, -1):
                res = subprocess.call(cmd, stdin=DEV_NULL, stdout=DEV_NULL,
                    stderr=DEV_NULL)
                if res == 0:
                    break
                time.sleep(0.2)
            if i == 0:
                raise RuntimeError('The %s is supposedly up, but "%s" cannot '
                    'connect'
                    % (self, ' '.join(cmd)))

        return votes > 0

    @property
    def pid(self):
        """The server's PID (None if not running).
        """
        # We can't possibly be running if our base_pathname isn't defined.
        if not self.base_pathname:
            return None

        try:
            pidfile = os.path.join(self.base_pathname, 'postmaster.pid')
            return int(open(pidfile).readline())
        except (IOError, OSError):
            return None

    @staticmethod
    def get_version():
        results = subprocess.check_output([PG_CTL, '--version'])
        match = re.search(r'(\d+\.\d+\.\d+)', results)
        if match:
            return match.group(0)

    def start(self):
        """Launch this postgres server.  If it's already running, do nothing.

        If the backing storage directory isn't configured, raise
        NotInitializedError.

        This method is optional.  If you're running in an environment
        where the DBMS is provided as part of the basic infrastructure,
        you probably want to skip this step!
        """
        if not self.base_pathname:
            raise NotInitializedError('Invalid base_pathname: %r.  '
                'Did you forget to call .initdb()?' % self.base_pathname)

        conf_file = os.path.join(self.base_pathname, 'postgresql.conf')
        if not os.path.exists(conf_file):
            raise NotInitializedError('No config file at: %r.  '
                'Did you forget to call .initdb()?' % self.base_pathname)

        if not self.is_running():
            version = self.get_version()
            if version and version.startswith('9.3'):
                socketop = 'unix_socket_directories'
            else:
                socketop = 'unix_socket_directory'
            postgres_options = [
                # When running not as root, postgres might try to put files
                #  where they're not writable (see
                #  https://paste.yougov.net/YKdgi). So set the socket_dir.
                '-c', '{}={}'.format(socketop, self.base_pathname),
                '-h', self.host,
                '-i',  # enable TCP/IP connections
                '-p', self.port,
            ]
            subprocess.check_call([
                PG_CTL, 'start',
                '-D', self.base_pathname,
                '-l', os.path.join(self.base_pathname, 'postgresql.log'),
                '-o', subprocess.list2cmdline(postgres_options),
            ])

        # Postgres may launch, then abort if it's unhappy with some parameter.
        # This post-launch test helps us decide.
        if not self.is_running():
            raise RuntimeError('%s aborted immediately after launch' % self)

    def stop(self):
        """Stop this DMBS daemon.  If it's not currently running, do nothing.

        Don't return until it's terminated.
        """
        if self.is_running():
            subprocess.check_call([PG_CTL, 'stop', '-D', self.base_pathname,
                '-m', 'fast'])
            # pg_ctl isn't reliable if it's called at certain critical times
            if self.pid:
                os.kill(self.pid, signal.SIGTERM)
        # Can't use wait() because the server might not be our child
        while self.is_running():
            time.sleep(0.1)

class PostgresFinder(paths.PathFinder):
    # Where are the postgres executables?  Consider the following pathnames in
    # order.
    candidate_paths = [
        # look on $PATH
        '',
        '/usr/local/pgsql/bin/',
        '/Program Files/pgsql/bin',
    ]
    # Prefer the highest-numbered version available.
    candidate_paths.extend(
        sorted(glob.glob('/usr/lib/postgresql/*/bin'), reverse=True)
    )
    exe = 'pg_ctl'
    args = ['--version']

PG_EXECUTABLES = PostgresFinder.find_root()
INITDB = os.path.join(PG_EXECUTABLES, 'initdb')
PG_CTL = os.path.join(PG_EXECUTABLES, 'pg_ctl')
PSQL = os.path.join(PG_EXECUTABLES, 'psql')
POSTGRES = os.path.join(PG_EXECUTABLES, 'postgres')
