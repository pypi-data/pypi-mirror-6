# -*- coding: utf-8 -*-
"""
sphinxcontirb.autorun2
~~~~~~~~~~~~~~~~~~~~~~

Run the code and insert stdout after the code block.

"""
import io
import os
import sys

from docutils import nodes
from sphinx.util.compat import Directive
from sphinx.errors import SphinxError

class PyConRunner(object):
    def __init__(self):
        self.reset("<unknown>")

    def reset(self, fname):
        self.globals = {
            "__builtins__": globals()["__builtins__"],
            "__file__": fname,
            "__package__": None,
        }

    def run(self, directive, config, code):
        old_stdout, old_stderr = sys.stderr, sys.stdout
        try:
            return "\n".join(self._run(directive, config, code))
        finally:
            sys.stderr, sys.stdout = old_stdout, old_stderr
    
    def _run(self, directive, config, code):
        show_code = config.get("show_code", True)
        self.reset_outs()
        for hunk in self.iter_code_hunks(code):
            if hunk and hunk[0] == True:
                if show_code:
                    yield hunk[1]
                continue
            try:
                res = eval(hunk, self.globals, self.globals)
            except SyntaxError:
                res = None
                exec hunk in self.globals, self.globals
            outs_bytes = self.outs.getvalue().rstrip("\n")
            if outs_bytes:
                yield outs_bytes
                self.reset_outs()
            if res is not None:
                yield repr(res)

    def reset_outs(self):
        self.outs = io.BytesIO()
        sys.stdout = self.outs
        sys.stderr = self.outs

    def iter_code_hunks(self, code):
        block = ""
        for line in code:
            prefix, _, code = line.lstrip().partition(" ")
            if prefix == ">>>":
                if block:
                    yield block
                block = code + "\n"
            elif prefix == "...":
                block += code + "\n"
            else:
                continue
            yield (True, line)
        if block:
            yield block


class RunBlockError(SphinxError):
    category = 'runblock error'

class AutoRun(object):
    here = os.path.abspath(__file__)
    pycon = os.path.join(os.path.dirname(here),'pycon.py')
    config = {
        'pycon': PyConRunner(),
    }
    @classmethod
    def builder_init(cls,app):
        cls.config.update(app.builder.config.autorun_languages)


def flag(val):
    return True


class RunBlock(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'linenos': flag,
        'reset': flag,
    }

    def run(self):
        config = AutoRun.config
        language = self.arguments[0]

        if language not in config:
            raise RunBlockError('Unknown language %s' % language)

        
        # Get configuration values for the language
        runner = config[language]
        lang_key = language + "_"
        runner_config = dict(
            (key[len(lang_key):], val)
            for (key, val) in config.items()
            if key.startswith(lang_key)
        )
        runner_config.update(self.options)
        code_out = runner.run(self, runner_config, self.content)

        literal = nodes.literal_block(code_out, code_out)
        literal['language'] = language
        literal['linenos'] = self.options.get("linenos")
        return [literal]



def setup(app):
    app.add_directive('runblock', RunBlock)
    app.connect('builder-inited',AutoRun.builder_init)
    app.add_config_value('autorun_languages', AutoRun.config, 'env')

# vim: set expandtab shiftwidth=4 softtabstop=4 :
