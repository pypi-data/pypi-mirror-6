from StringIO import StringIO
import sys
from contextlib import contextmanager

from google_news_crawler.google_news_crawler import main as gnc_main
from google_news_crawler.google_news_crawler import __doc__ as gnc_docstring


# Copied from:
#   http://stackoverflow.com/questions/5974557/testing-python-scripts#answer-5977043
@contextmanager
def captured_output(stream_name):
    """Run the 'with' statement body using a StringIO object in place of a
       specific attribute on the sys module.
       Example use (with 'stream_name=stdout'):

       with captured_stdout() as s:
           print("hello")
           assert s.getvalue() == "hello"
    """
    orig_stdout = getattr(sys, stream_name)
    setattr(sys, stream_name, StringIO())
    try:
        yield getattr(sys, stream_name)
    finally:
        setattr(sys, stream_name, orig_stdout)


def captured_stdout():
    return captured_output("stdout")


def captured_stderr():
    return captured_output("stderr")


def captured_stdin():
    return captured_output("stdin")


def test_main_help():
    with captured_stdout() as out:
        try:
            gnc_main(argv='--help')
        except SystemExit:
            pass

    assert out.getvalue() == gnc_docstring
