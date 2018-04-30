VERBOSE_COLOR = '\x1B[1;34m'
ERROR_COLOR = '\x1B[1;31m'
DEFAULT_COLOR = '\x1B[0m'


def verbose_print(string):
    print(VERBOSE_COLOR + str(string) + DEFAULT_COLOR)


def error_print(string):
    print(ERROR_COLOR + str(string) + DEFAULT_COLOR)