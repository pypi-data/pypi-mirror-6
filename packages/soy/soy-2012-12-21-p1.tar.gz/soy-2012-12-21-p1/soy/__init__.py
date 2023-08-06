import os
import subprocess
import tempfile


class SoyError(Exception):
    pass


class SoyFileSet(object):

    SOY_TO_PY_COMPILER_JAR = 'SoyToPySrcCompiler.jar'
    SOY_TO_JS_COMPILER_JAR = 'SoyToJsSrcCompiler.jar'

    class Builder(object):

        def __init__(self):
            self.files = []

        def add(self, file):
            self.files.append(file)
            return self

        def build(self):
            return SoyFileSet(self.files)

    def __init__(self, files):
        self.files = files

    def _findSoyCompiler(self, compilerJarName, compilerJarPath=None):
        possiblePaths = []
        if compilerJarPath is not None:
            possiblePaths.append(compilerJarPath)
            possiblePaths.append(os.path.join(compilerJarPath, compilerJarName))
        for path in os.environ.get('SOY_COMPILER_PATH', os.getcwd()).split(os.pathsep):
            possiblePaths.append(os.path.join(path, compilerJarName))
        for path in possiblePaths:
            if os.path.isfile(path):
                return path
        raise Exception('could not find {0}'.format(compilerJarName))

    def _compile(self, fileName, compilerJarName, compilerJarPath):
        command = [
            'java', '-jar',
            self._findSoyCompiler(compilerJarName, compilerJarPath),
            '--outputPathFormat', fileName,
        ]
        for file in self.files:
            command.append('--srcs')
            command.append(file)
        status = subprocess.call(command)
        if status != 0:
            raise SoyError("soy template compilation failed")

    def compileToJsFile(self, fileName, compilerJarPath=None):
        self._compile(fileName, self.SOY_TO_JS_COMPILER_JAR, compilerJarPath)

    def compileToPyFile(self, fileName, compilerJarPath=None):
        self._compile(fileName, self.SOY_TO_PY_COMPILER_JAR, compilerJarPath)

    def compileToTofu(self, compilerJarPath=None):
        from soy.tofu import SoyTofu
        with tempfile.NamedTemporaryFile(prefix='soy_', suffix='.py') as file:
            self.compileToPyFile(file.name, compilerJarPath)
            return SoyTofu.fromFile(file)

