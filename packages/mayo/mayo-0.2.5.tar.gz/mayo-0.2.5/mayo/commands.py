import os
import argparse

import mayo.repositories
import mayo.fetcher
import mayo.errors

class WhatIsThisCommand(object):
    def create_parser(self, subparser):
        subparser.add_argument("directory", nargs="?")
    
    def execute(self, args):
        directory = args.directory if args.directory is not None else os.getcwd()
        repository = mayo.repositories.find_repository(directory)
        if repository is None:
            print "Could not find source control repository"
        else:
            print "{0}+file://{1}".format(repository.type, repository.working_directory)

class FetchCommand(object):
    def create_parser(self, subparser):
        subparser.add_argument("repository_uri", metavar="repository-uri")
        subparser.add_argument("local_path", metavar="local-path")
        subparser.add_argument("--use-cache", default=False, help=argparse.SUPPRESS, action="store_true")
    
    def execute(self, args):
        try:
            mayo.fetcher.fetch(args.repository_uri, args.local_path, args.use_cache)
        except (mayo.errors.MayoUserError, mayo.util.NoSuchCommandError) as error:
            print "fetch failed: {0}".format(error.message)
            exit(-1)

class ArchiveCommand(object):
    def create_parser(self, subparser):
        subparser.add_argument("repository_uri", metavar="repository-uri")
        subparser.add_argument("local_path", metavar="local-path")
    
    def execute(self, args):
        try:
            mayo.fetcher.archive(args.repository_uri, args.local_path)
        except (mayo.errors.MayoUserError, mayo.util.NoSuchCommandError) as error:
            print "archive failed: {0}".format(error.message)
            exit(-1)


commands = {
    "what-is-this": WhatIsThisCommand(),
    "fetch": FetchCommand(),
    "archive": ArchiveCommand()
}
