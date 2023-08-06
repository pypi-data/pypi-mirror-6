#! /usr/bin/env python
'''
Created on Mar 11, 2014

Author: zxzhang

This module defines specific exceptions.

'''

import configure

class DownloadException(Exception):

    def __init__(self, resp = None, msg = None):
        self.resp = resp
        if resp:
            self.args = (resp.status, resp.headers)
            self.status = resp.status
            self.body = resp.body
            self.headers = resp.headers
        self.msg = msg
    def __str__(self):
        if not self.resp:
            return self.msg
        else:
            return 'status: %s \n headers: %s' % \
                (self.status, self.headers)

class ParamException(Exception):

    def __init__(self, msg = ''):
        self.args = msg
        self.msg = msg
        self.msg += '\nsupported image size: '
        for size in configure.IMAGE_WIDTH:
            self.msg += ('%s: %d\n' % (size, configure.IMAGE_WIDTH[size]))

    def __str__(self):
        return self.msg

class ConfigParamInvalidException(Exception):

    def __init__(self, msg = ''):
        self.args = msg
        self.msg = msg
        self.msg += '''\nconfig is supposed to be dictionary type, \
                    including 'BUCKET', 'USERNAME', 'PASSWORD' keys at least'''
    
    def __str__(self):
        return self.msg


class UpYunServiceException(Exception):
    def __init__(self, error):
        self.args = (error.status, error.msg, error.err)
        self.status = error.status
        self.msg = error.msg
        self.err = error.err


class UpYunClientException(Exception):
    def __init__(self, error):
        self.args = (error.msg)
        self.msg = error.msg

