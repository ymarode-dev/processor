# filters.py
import logging

class InfoFilter(logging.Filter):
    """Filter for 'info' level logs."""
    def filter(self, record):
        return record.levelno == logging.INFO


class ErrorFilter(logging.Filter):
    """Filter for 'error' level logs."""
    def filter(self, record):
        return record.levelno == logging.ERROR


class DebugFilter(logging.Filter):
    """Filter for 'debug' level logs."""
    def filter(self, record):
        return record.levelno == logging.DEBUG
    

class WarnFilter(logging.Filter):
    """Filter for 'warn' level logs."""
    def filter(self, record):
        return record.levelno == logging.WARN


class TraceFilter(logging.Filter):
    """Filter for trace level logs (custom level 9)."""
    def filter(self, record):
        return record.levelno == 9


class ResponseFilter(logging.Filter):
    """Filter for response level logs (custom level 15)."""
    def filter(self, record):
        return record.levelno == 15


class PCFilter(logging.Filter):
    """Filter for PC level logs (custom level 14)."""
    def filter(self, record):
        return record.levelno == 14    

class DBTraceFilter(logging.Filter):
    """Filter for db trace level logs (custom level 24)."""
    def filter(self, record):
        return record.levelno == 24

class ScheduleFilter(logging.Filter):
    """Filter for schedule level logs (custom level 24)."""
    def filter(self, record):
        return record.levelno == 26
    
class PytestFilter(logging.Filter):
    """Filter for pytest level logs (custom level 24)."""
    def filter(self, record):
        return record.levelno == 27

class AQIFilter(logging.Filter):
    """Filter for aqi level logs (custom level 24)."""
    def filter(self, record):
        return record.levelno == 28
