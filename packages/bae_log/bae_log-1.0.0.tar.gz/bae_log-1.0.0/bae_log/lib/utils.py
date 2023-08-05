from logchain.ttypes import *
import logging

def getbaelevel(levelno):
    if levelno == logging.FATAL:
        return BaeLogLevel.FATAL
    if levelno == logging.ERROR:
        return BaeLogLevel.FATAL
    if levelno == logging.WARNING:
        return BaeLogLevel.WARNING
    if levelno == logging.INFO:
        return BaeLogLevel.NOTICE
    if levelno == logging.DEBUG:
        return BaeLogLevel.DEBUG
    else:
        return BaeLogLevel.TRACE
