from functools import partial
import time
from decorator import decorator

# Inspired by https://github.com/invl/retry/blob/master/retry/api.py, but without the py dependency


def __retry_internal(
    f, exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1
):
    """
    Executes a function and retries it if it failed.

    :param f: the function to execute.
    :type f: callable
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :type exceptions: BaseException
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :type tries: int
    :param delay: initial delay between attempts. default: 0.
    :type delay: int
    :param max_delay: the maximum value of delay. default: None (no limit).
    :type max_delay: int
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :type backoff: int
    :returns: the result of the f function.
    :rtype: any
    """
    _tries, _delay = tries, delay
    while _tries:
        try:
            return f()
        except exceptions:
            _tries -= 1
            if not _tries:
                raise

            time.sleep(_delay)
            _delay *= backoff

            if max_delay is not None:
                _delay = min(_delay, max_delay)


def retry(exceptions=Exception, tries=-1, delay=0, max_delay=None, backoff=1):
    """Returns a retry decorator.

    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :type exceptions: BaseException
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :type tries: int
    :param delay: initial delay between attempts. default: 0.
    :type delay: int
    :param max_delay: the maximum value of delay. default: None (no limit).
    :type max_delay: int
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :type backoff: int
    :return: a retry decorator.
    :rtype: decorator
    """

    @decorator
    def retry_decorator(f, *fargs, **fkwargs):
        """Wrapper executing ``f`` with retry logic applied."""
        args = fargs if fargs else list()
        kwargs = fkwargs if fkwargs else dict()
        return __retry_internal(
            partial(f, *args, **kwargs), exceptions, tries, delay, max_delay, backoff
        )

    return retry_decorator
