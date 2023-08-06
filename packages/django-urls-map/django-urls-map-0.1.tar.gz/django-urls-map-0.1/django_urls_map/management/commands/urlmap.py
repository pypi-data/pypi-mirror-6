# -*- coding: utf-8 -*-
"""
Command line tool to browse the full urls map
"""
from optparse import make_option

from django.utils.termcolors import colorize

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand
from django.core.urlresolvers import RegexURLResolver

def startswith_in_list(src, items):
    """
    Comparaison de type "startswith" avec une liste de 'match' possibles
    """
    for k in items:
        if src.startswith(k):
            return k
    return False

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("--exclude", dest="excluded_paths", action="append", help="Excludes paths, append each excluded path with this option"),
    )
    help = "Command to list url map"

    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("Command doesn't accept any arguments")
        
        self.excluded_paths = options.get('excluded_paths')
        if not self.excluded_paths:
            self.excluded_paths = []
        self.verbosity = int(options.get('verbosity'))

        # Parcours des urls depuis la racine
        urlconf = settings.ROOT_URLCONF
        rootresolver = RegexURLResolver(r'^/', urlconf)
        self._walk_urlresolver("/", rootresolver)
    
    def _walk_urlresolver(self, parent, urlresolver, lv=0):
        for item in urlresolver.url_patterns:
            _url_name = getattr(item, 'name', None) or 'Unnamed'
            current_path = parent + self._clear_regexpath(item.regex.pattern)
            _current_path_display = current_path or 'No path'
            if startswith_in_list(current_path, self.excluded_paths):
                continue
            if not isinstance(item, RegexURLResolver):
                print "{indent}* {path} {name}".format(indent=("  "*lv), path=colorize(_current_path_display, fg='green'), name=colorize(_url_name, fg='magenta'))
            else:
                print "{indent}* {path}".format(indent=("  "*lv), path=colorize(_current_path_display, fg='blue'))
                self._walk_urlresolver(current_path, item, lv=lv+1)
    
    def _clear_regexpath(self, regex):
        path = regex
        if path.startswith('^'):
            path = path[1:]
        if path.endswith('$'):
            path = path[:-1]
        return path
