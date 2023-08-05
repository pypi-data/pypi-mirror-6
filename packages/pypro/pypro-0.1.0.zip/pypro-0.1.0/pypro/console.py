import os
import sys

if sys.version_info[0] == 3:
    def raw_input(prompt):
        return input(prompt).rstrip("\n")


def ask(question, default=None):
    """
    @question: str
    @default: Any value which can be converted to string.

    Asks a user for a input.
    If default parameter is passed it will be appended to the end of the message in square brackets.
    """
    question = str(question)

    if default:
        question += ' [' + str(default) + ']'

    question += ': '

    reply = raw_input(question)
    return reply if reply else default


def ask_bool(question, default=None):
    """
    Asks user a question and yes/no answer is expected.
    Possible yes answers: Y/y/Yes/yes
    Possible no answers: N/n/No/no
    """
    return to_bool(ask(question, default), default)


def to_bool(answer, default):
    """
    Converts user answer to boolean
    """
    answer = str(answer).lower()
    default = str(default).lower()

    if answer and answer in "yes":
        return True

    return False


def ask_int(question, default=None):
    """ Ask user for integer input. """
    return to_int(ask(question, default))


def to_int(answer):
    """ Converts user input to integer if conversion is not possible None is returned. """
    try:
        answer = int(answer)
    except ValueError:
        return None

    return answer


def out(*args):
    """ Outputs its parameters to users stdout. """
    for value in args:
        sys.stdout.write(value)

    sys.stdout.write(os.linesep)


def err(*args):
    """ Outputs its parameters to users stderr. """
    for value in args:
        sys.stderr.write(value)

    sys.stderr.write(os.linesep)