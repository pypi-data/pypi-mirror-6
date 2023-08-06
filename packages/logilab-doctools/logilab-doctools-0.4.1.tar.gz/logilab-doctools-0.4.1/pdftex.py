import os, subprocess, glob
from logilab.common.shellutils import ProgressBar

def bar_finish(bar):
    while bar._progress != bar._size:
        bar.update()

class TransformException(Exception):
    pass

class PdfTex(object):

    def __init__(self, texinputs=None, flags=''):
        self._texinputs = texinputs or []
        self._flags = flags

    def __call__(self, name, clean=True, progress=True):
        if progress:
            bar = ProgressBar(6, title=name)
        rerun = self._run(name, bar)
        indexfile = None
        while rerun:
            rerun, indexfile = self._run(name, bar)
        if indexfile:
            self._run(name, bar, indexfile)
        if clean:
            self.clean(name)
        if bar:
            bar_finish(bar)

    def _run(self, name, bar, indexfile=None):
        if bar:
            bar.refresh()
        if indexfile is not None:
            proc = subprocess.call('makeindex %s' % indexfile, shell=True)
        cmd = 'TEXINPUTS=%s pdflatex %s %s.tex' % (':'.join(self._texinputs), self._flags, name)
        rerun = False
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
        errors_log = []
        append_error = False
        for line in proc.stdout:
            if append_error:
                if line.strip() == "":
                    # Blank line: end of error message
                    append_error = False
                else:
                   errors_log.append(line.strip())
                   errors_log.append("")
            if line.startswith('Writing index file'):
                indexfile = line.split()[-1]
                if bar:
                    bar.update()
            if bar and line.startswith('\openout'):
                    bar.update()
            if line.startswith('LaTeX Warning'):
                if 'There were undefined references' in line:
                    pass
                elif 'Warning: Reference' in line:
                    pass
                elif 'Rerun' in line:
                    rerun = True
                else:
                    print line.strip()
            if 'LaTeX Error' in line:
                errors_log.append(line.strip())
                append_error = True
            if 'Fatal error' in line:
                errors_log.append(line.strip())
                append_error = True
                rerun = False
            if line.startswith("error occurred, no output PDF"):
                raise TransformException("Fatal error while producing PDF:\n\n"
                                         "%s" % "\n".join(errors_log))
        return rerun, indexfile

    def clean(self, name):
        for ext in 'idx log nav out snm toc vrb ilg ind'.split():
            filename = '%s.%s' % (name, ext)
            if os.path.exists(filename):
                os.remove(filename)
        for filename in glob.glob('*.aux'):
            os.remove(filename)
