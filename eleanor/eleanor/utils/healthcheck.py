import socket
import sys
import time
import traceback
import logging
from flask import current_app

# Based on https://github.com/Runscope/healthcheck


try:
    from functools import reduce
except Exception:
    pass


def get_hostname():
    hostname = (
        [
            (
                s.connect(('8.8.8.8', 80)),
                s.getsockname()[0],
                s.close()) for s in [
                    socket.socket(
                        socket.AF_INET,
                        socket.SOCK_DGRAM
                    )
            ]
        ][0][1]
    )
    return hostname


def basic_exception_handler(_, e):
    return False, str(e)


def success_handler(results):
    data = {
        'hostname': get_hostname(),
        'status': 'success',
        'results': results
    }
    return data


def failed_handler(results):
    data = {
        'hostname': get_hostname(),
        'status': 'failure',
        'results': results
    }
    return data


def check_reduce(passed, result):
    return passed and result.get('passed')


class HealthCheck(object):
    def __init__(
        self,
        success_status=200,
        failed_status=503,
        success_ttl=15,
        failed_ttl=15,
        success_handler=success_handler,
        failed_handler=failed_handler,
        exception_handler=basic_exception_handler,
        checkers=None,
        log_on_failure=True
    ):
        self.cache = dict()
        self.success_status = success_status
        self.success_handler = success_handler
        self.success_ttl = success_ttl
        self.failed_status = failed_status
        self.failed_handler = failed_handler
        self.failed_ttl = failed_ttl
        self.exception_handler = exception_handler
        self.log_on_failure = log_on_failure
        self.checkers = checkers or []

    def add_check(self, func):
        self.checkers.append(func)

    def check(self):
        results = []
        for checker in self.checkers:
            if checker in self.cache and self.cache[checker].get(
                    'expires') >= time.time():
                current_app.logger.debug("CACHE HIT")
                result = self.cache[checker]
            else:
                current_app.logger.debug("CACHE MISS")
                result = self.run_check(checker)
                self.cache[checker] = result
            results.append(result)

        passed = reduce(check_reduce, results, True)

        if passed:
            message = "OK"
            if self.success_handler:
                current_app.logger.debug(results)
                message = self.success_handler(results)

            return message, self.success_status
        else:
            message = "NOT OK"
            if self.failed_handler:
                message = self.failed_handler(results)

            return message, self.failed_status

    def run_check(self, checker):
        try:
            passed, output = checker()
        except Exception:
            traceback.print_exc()
            e = sys.exc_info()[0]
            logging.exception(e)
            passed, output = self.exception_handler(checker, e)

        if not passed:
            msg = 'Health check "{}" failed with output "{}"'.format(
                checker.__name__, output)
            if self.log_on_failure:
                logging.error(msg)

        timestamp = time.time()
        if passed:
            expires = timestamp + self.success_ttl
        else:
            expires = timestamp + self.failed_ttl

        result = {
            'checker': checker.__name__,
            'output': output,
            'passed': passed,
            'timestamp': timestamp,
            'expires': expires
        }

        return result
