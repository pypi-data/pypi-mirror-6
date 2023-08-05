#!/usr/bin/env python
"""
s3tos3backup.runner
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by YD Technology.
:license: MIT, see LICENSE for more details.
"""
import sys
import traceback
import logging
import locale
import os
import ConfigParser

from s3tos3backup import PkgInfo

from optparse import OptionParser, IndentedHelpFormatter

default_verbosity = logging.ERROR

CONFIG_TEMPLATE = """[default]
access_key = %(access_key)s
secret_key = %(secret_key)s
bucket_name = %(bucket_name)s
remove_older_days = %(remove_older_days)s
"""


def generate_settings():
    """
    This command is run when ``default_path`` doesn't exist, or ``init`` is
    run and returns a string representing the default data to put into their
    settings file.
    """

    return CONFIG_TEMPLATE


INFO_TEXT = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    An unexpected error has occurred.
  Please try reproducing the error using
  the latest s3tos3backup code from the git master
  branch found at:
    https://github.com/YD-Technology/s3tos3backup
  If the error persists, please report the
  following lines (removing any private
  info as necessary) at:
   https://github.com/YD-Technology/s3tos3backup/issues
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

"""


def report_exception(e):
        sys.stderr.write(INFO_TEXT)
        s = ' '.join(sys.argv)
        sys.stderr.write("""Invoked as: %s""" % s)

        tb = traceback.format_exc(sys.exc_info())
        e_class = str(e.__class__)
        e_class = e_class[e_class.rfind(".") + 1: -2]
        sys.stderr.write(u"Problem: %s: %s\n" % (e_class, e))
        try:
            sys.stderr.write("s3tos3backup:   %s\n" % PkgInfo.version)
        except NameError:
            sys.stderr.write("s3tos3backup:   unknown version. Module import problem?\n")
        sys.stderr.write("python:   %s\n" % sys.version)
        sys.stderr.write("\n")
        sys.stderr.write(unicode(tb, errors="replace"))

        if type(e) == ImportError:
            sys.stderr.write("\n")
            sys.stderr.write("Your sys.path contains these entries:\n")
            for path in sys.path:
                sys.stderr.write(u"\t%s\n" % path)
            sys.stderr.write("Now the question is where have the s3tos3backup modules been installed?\n")

        sys.stderr.write(INFO_TEXT)


def output(message):
    sys.stdout.write(message + "\n")
    sys.stdout.flush()


def main():
    optparser = OptionParser(formatter=IndentedHelpFormatter())
    preferred_encoding = locale.getpreferredencoding() or "UTF-8"
    optparser.set_defaults(encoding=preferred_encoding)
    config_file = os.path.join(os.getenv("HOME"), ".s3tos3backup")
    optparser.set_defaults(config=config_file)
    optparser.set_defaults(verbosity=default_verbosity)

    optparser.add_option("-c", "--config", dest="config", metavar="FILE", help="Config file name. Defaults to %default")
    optparser.add_option("--access_key", dest="access_key", help="AWS Access Key")
    optparser.add_option("--secret_key", dest="secret_key", help="AWS Secret Key")
    optparser.add_option("-b", "--bucket", dest="bucket_name", help="Bucket name")
    optparser.add_option("-o", "--remove-older-days", dest="remove_older_days",
                         help="Remove backups older than days")
    optparser.add_option("-v", "--verbose", dest="verbosity", action="store_const", const=logging.INFO,
                         help="Enable verbose output.")
    optparser.add_option("-d", "--debug", dest="verbosity", action="store_const", const=logging.DEBUG,
                         help="Enable debug output.")
    optparser.add_option("--remove-only", dest="backup", action="store_false", default=True,
                         help="Remove only old backups. Do not do a backup")
    optparser.add_option("--backup-only", dest="remove", action="store_false", default=True,
                         help="Do a backup. Do not remove only old backups")
    optparser.add_option("--configure", dest="configure", action="store_true",
                         help="Save configuration and exit.")
    optparser.add_option("--version", dest="show_version", action="store_true",
                         help="Show s3tos3backup version (%s) and exit." % (PkgInfo.version))

    optparser.set_description('s3tos3backup is a tool for managing backups for Amazon S3 storage.')
    optparser.epilog = ("\nFor more information see the project homepage:\n%s\n" % PkgInfo.url)

    (options, args) = optparser.parse_args()

    logging.basicConfig(level=options.verbosity,
                        format='%(levelname)s: %(message)s',
                        stream=sys.stderr)

    if options.show_version:
        output(u"s3tos3backup version %s" % PkgInfo.version)
        sys.exit(0)

    if options.configure:
        with open(config_file, 'w') as f:
            f.write(CONFIG_TEMPLATE % dict(access_key=options.access_key,
                                           secret_key=options.secret_key,
                                           bucket_name=options.bucket_name,
                                           remove_older_days=options.remove_older_days))
        output(u"Config saved to: %s" % config_file)
        sys.exit(0)

    if not options.config:
        logging.error(u"Can't find a config file. Please use --config option.")
        sys.exit(1)

    logging.root.setLevel(options.verbosity)

    config = ConfigParser.ConfigParser()
    if not config.read(options.config):
        raise EnvironmentError("You need to configure s3tos3backup, 's3tos3backup --configure'")

    bucket_name = options.bucket_name or config.get('default', 'bucket_name')
    if not bucket_name:
        logging.error(u"Bucket name is required. Please use --bucket option.")
        sys.exit(1)

    aws_key = options.access_key or config.get('default', 'access_key')
    aws_secret_key = options.secret_key or config.get('default', 'secret_key')
    remove_older_days = options.remove_older_days or config.get('default', 'remove_older_days') or 7

    try:
        from .backup import run_backup
        run_backup(options.backup, options.remove, aws_key, aws_secret_key, remove_older_days)
    except ImportError, e:
        report_exception(e)
        sys.exit(1)

if __name__ == '__main__':
    main()
