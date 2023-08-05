#!/usr/bin/env python

from voluptuous import Schema, Required, MultipleInvalid
import datetime

__author__ = 'Majid Garmaroudi'
__version__ = '0.0.2'
__license__ = 'MIT'

"""
Acceptable format:
    {
        'tests': '12',
        'failures': '3',
        'failed': '6',
        'duration': '125',
        'timestamp' : '12345',
        'testcases': [
            {
                'name': 'Name of the testcase',
                'error': {}
            },
            {
                'name': 'Name of the testcase',
                'error': {
                    'type': 'Type of the error',
                    'message': 'Error message'
                }
            }
        ]
    }
"""


def dict_to_xunit(results):
    timestamp = datetime.datetime.now()
    if 'timestamp' in results and len(results['timestamp']) > 0:
        timestamp = results['timestamp']

    xunit_body = ''
    xunit_results = '<?xml version="1.0" encoding="UTF-8"?>'
    xunit_results += '<testsuite name="Test suite" tests="%s" failures="%s" errors="%s" skip="0" timestamp="%s" time="%s">' % (
        results['tests'], results['failures'], results['failed'], timestamp, results['duration'])
    for testcase in results['testcases']:
        if 'type' in testcase['error']:
            xunit_body += '<testcase name="%s" time="0"><error type="%s" message="%s"></error></testcase>' % (
                testcase['name'], testcase['error']['type'], testcase['error']['message'])
        else:
            xunit_body += '<testcase name="%s" time="0"/>' % testcase['name']

    xunit_results += xunit_body
    xunit_results += '</testsuite>'

    return xunit_results


def validate_dict(results):
    schema = Schema({
        Required('tests'): str,
        Required('failures'): str,
        Required('failed'): str,
        Required('duration'): str,
        'timestamp': str,
        Required('testcases'): [
            {
                Required('name'): str,
                'error': {
                    'type': str,
                    'message': str
                }
            }
        ]
    })

    try:
        return schema(results)
    except MultipleInvalid as e:
        exc = e

    return str(exc) == ""
