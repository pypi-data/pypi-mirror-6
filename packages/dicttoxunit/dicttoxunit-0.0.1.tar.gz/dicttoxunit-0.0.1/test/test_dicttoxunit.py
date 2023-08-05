from nose.tools import assert_false, assert_true, assert_equal
from dicttoxunit import validate_dict, dict_to_xunit

# correct_dictionary = {}
# wrong_dictionary_1 = {}

correct_dictionary = {
    'tests': '12',
    'failures': '3',
    'failed': '6',
    'duration': '125',
    'timestamp': '2014-01-20 13:51:14.908799',
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

correct_result = '<?xml version="1.0" encoding="UTF-8"?><testsuite name="Test suite" tests="12" failures="3" errors="6" skip="0" timestamp="2014-01-20 13:51:14.908799" time="125"><testcase name="Name of the testcase" time="0"/><testcase name="Name of the testcase" time="0"><error type="Type of the error" message="Error message"></error></testcase></testsuite>'

wrong_dictionary_1 = {
    'failures': '3',
    'failed': '6',
    'duration': '125',
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

wrong_dictionary_2 = {
    'tests': '12',
    'failed': '6',
    'duration': '125',
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


wrong_dictionary_3 = {
    'tests': '12',
    'failures': '3',
    'duration': '125',
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

wrong_dictionary_3 = {
    'tests': '12',
    'failures': '3',
    'failed': '6',
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

wrong_dictionary_4 = {
    'tests': '12',
    'failures': '3',
    'failed': '6',
    'duration': '125'
}

wrong_dictionary_5 = {
    'tests': '12',
    'failures': '3',
    'failed': '6',
    'duration': '125',
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


def test_converter_is_working():
    assert_true(dict_to_xunit(correct_dictionary))


def test_dictionary_is_valid():
    assert_true(validate_dict(correct_dictionary))


def test_dictionary_is_invalid_1():
    assert_false(validate_dict(wrong_dictionary_1))


def test_dictionary_is_invalid_2():
    assert_false(validate_dict(wrong_dictionary_2))


def test_dictionary_is_invalid_3():
    assert_false(validate_dict(wrong_dictionary_3))


def test_dictionary_is_invalid_4():
    assert_false(validate_dict(wrong_dictionary_4))


def test_converter_works_correctly():
    assert_equal(dict_to_xunit(correct_dictionary), correct_result)
