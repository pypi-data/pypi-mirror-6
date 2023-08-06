from pipeline.compilers import SubProcessCompiler
from os.path import dirname
from django.conf import settings


class BrowserifyCompiler(SubProcessCompiler):
    output_extension = 'browserified.js'

    def match_file(self, path):
        return path.endswith('.browserify.js')

    def compile_file(self, infile, outfile, outdated=False, force=False):
        command = "%s %s %s > %s" % (
            getattr(settings, 'PIPELINE_BROWSERIFY_BINARY', '/usr/bin/env browserify'),
            getattr(settings, 'PIPELINE_BROWSERIFY_ARGUMENTS', ''),
            infile,
            outfile
        )
        return self.execute_command(command, cwd=dirname(infile))

