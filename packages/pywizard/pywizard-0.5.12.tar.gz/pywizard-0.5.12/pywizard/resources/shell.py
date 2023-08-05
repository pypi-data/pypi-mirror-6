from logging import debug
import os
import subprocess
from tempfile import NamedTemporaryFile
from pywizard.utils.process import run
from pywizard.resources.python import PythonResource
from pywizard.templating import compile_content
from pywizard.worker import worker


def shell(
        code,
        rollback=None,
        if_not=None,
        only_if=None,
        ignore_errors=False,
        user=None
):

    def exec_bash_script(script):
        script = compile_content(script)

        if "\n" in script:
            f = NamedTemporaryFile(delete=False)
            f.write(script)
            f.close()
            if user:
                subprocess.call(['chown', user, f.name])
            command = 'bash %s' % f.name
            if user:
                command = 'su -c "%s" - %s ' % (command, user)

            debug('bash$ %s' % command)
            debug('\n\n%s\n' % script)
            run(command, ignore_errors=ignore_errors)
            os.unlink(f.name)
        else:
            if user:
                script = 'su -c "%s" - %s ' % (script, user)
            run(script, log_output=True, ignore_errors=ignore_errors)

    def _apply():
        exec_bash_script(code)

    def _rollback():
        exec_bash_script(rollback)

    worker.register_resource(
        PythonResource(
            _apply,
            _rollback,
            if_not,
            only_if,
            description='Shell script'
        )
    )
