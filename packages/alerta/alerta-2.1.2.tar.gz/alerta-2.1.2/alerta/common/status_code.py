"""
Possible alert status codes.
"""

OPEN_STATUS_CODE = 1
ACK_STATUS_CODE = 2
CLOSED_STATUS_CODE = 3
EXPIRED_STATUS_CODE = 4
UNKNOWN_STATUS_CODE = 9

OPEN = 'open'
ACK = 'ack'
CLOSED = 'closed'
EXPIRED = 'expired'
UNKNOWN = 'unknown'
NOT_VALID = 'notValid'

ALL = [OPEN, ACK, CLOSED, EXPIRED, UNKNOWN]

_STATUS_MAP = {
    OPEN: OPEN_STATUS_CODE,
    ACK: ACK_STATUS_CODE,
    CLOSED: CLOSED_STATUS_CODE,
    EXPIRED: EXPIRED_STATUS_CODE,
    UNKNOWN: UNKNOWN_STATUS_CODE,
}


def is_valid(name):
    return name in _STATUS_MAP


def name_to_code(name):
    return _STATUS_MAP.get(name, UNKNOWN_STATUS_CODE)


def parse_status(name):
    if name:
        for st in _STATUS_MAP:
            if name.lower() == st.lower():
                return st
    return NOT_VALID
