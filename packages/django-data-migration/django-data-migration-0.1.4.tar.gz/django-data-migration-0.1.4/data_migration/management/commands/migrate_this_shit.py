# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError, make_option
from django.core import management

import sys

class Command(BaseCommand):
    help = 'DEPRECATED: Migrates old data into the new django schema'

    option_list = BaseCommand.option_list + (
        make_option('--commit',
            action='store_true',
            help='Commits the Changes to DB if all migrations are done right.',
            dest='commit_changes',
            default=False),
        make_option('--exclude',
            action='append',
            metavar='APP',
            help='Excludes the supplied app from beeing migrated.',
            dest='excluded_apps',
            default = []),
        make_option('--logquery',
            action='store_true',
            help='Print the corresponding Query for each migration.',
            dest='logquery',
            default=False),
    )

    def handle(self, *args, **options):

        sys.stderr.write(
            u"This command is deprecated in favour of 'migrate_legacy_data'\n\n")
        management.call_command('migrate_legacy_data', *args, **options)
