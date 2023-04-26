DNS_PORT    = 53
BUF_LEN     = 1024
HEADER_LEN  = 12
ENCODING    = 'utf-8'

CACHED_ENTRIES  = {}
INITIAL_TTL     = 1800
NUM_A_RR        = 1
QUERY_TYPES     = {1: 'A', 5: 'CNAME', 2: 'NS', 6: 'SOA', 65: 'HTTPS'}
NAME_POINTER    = b'\xc0\x0c'
IP_LENGTH       = 4
RCODE_ERROR     = 3

import enum
class RRTYPE(enum.Enum):
    A = 1
    CNAME = 5
    NS = 2
    SOA = 6
    HTTPS = 65