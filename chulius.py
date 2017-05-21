from subprocess import Popen, PIPE
from threading import Thread, Lock
import re


class JuliusServerError(Exception):
    """
    Raised when failed to start Julius server.
    """
    pass


class RecognitionError(Exception):
    """
    Raised when recognition error occures.
    """
    pass


class JuliusServer(Thread):
    """
    Start recognition using by Julius and extract recognized sentence and score from result text.
    """

    def __init__(self, julius='julius.exe', conf='', grammar=''):
        """
        Args:
            See class Julius
        """

        super().__init__()
        self.daemon = True
        self._lock = Lock()
        self._running = False
        self._result = None
        self._popen = Popen(
            [julius, '-C', conf, '-gram', grammar, '-input', 'mic'],
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True)
        # Remove initial stdout text and check error.
        while True:
            line = self._popen.stdout.readline()
            if re.match(r'^ERROR:.*', line):
                raise JuliusServerError(
                    'Check configure file or grammar file name.')
            if re.match(r'.*System Information end.*', line):
                break

    def run(self):
        """
        Run Julius.
        """

        self._running = True
        while self._running:
            out = self._popen.stdout.readline()
            m = re.match(r'^(sentence|cmscore)1: (.*)', out)
            if not m:
                continue
            attr = m.group(1)
            val = m.group(2)
            if attr == 'sentence':
                sentence = val.split()
            elif attr == 'cmscore':
                score = [float(v) for v in val.split()]
                with self._lock:
                    self._result = {'sentence': sentence, 'score': score}

    def stop(self):
        """
        Stop Julius.
        """

        if self._running:
            self._running = False
            self.join()
        self._popen.kill()

    def recognize(self):
        """
        Recognize by Julius.
        """

        while not self._result:
            pass
        tmp = self._result
        with self._lock:
            self._result = None
        return tmp


class Chulius(object):
    """
    A class for recognition using by Julius.
    This can choose high score recognition.
    """

    def __init__(self, julius='julius', conf='', grammar='', target_score=0):
        """
        Args:
            julius: A path of Julius executable file.
            conf: A path conf file.
            grammar: Grammar file name.
            target_score: Minimum score for correct recognition. If 0 (default) , all recognition result are correct.
        """

        super().__init__()
        self.target_score = target_score
        self._server = JuliusServer(julius, conf, grammar)
        self._server.start()

    def recognize(self):
        """
        Recognize onece.
        Raise RecognitionError if a recognition score is lower than target score.
        """

        result = self._server.recognize()
        if min(result['score']) > self.target_score:
            return result['sentence']
        else:
            raise RecognitionError('Score is lower than target_score.')

    def __del__(self):
        try:
            self._server.stop()
        except AttributeError:
            pass
