# -*- coding: utf-8 -*-
"""
About: Project #6 of CSCI-651-FoundationsOfComputerNetworks course.
Description: This program serves as the DNS resolver implementation.
"""

__author__      = "Khushi Mahesh (km1139)"
__author__      = "Shreenidhi Vittala Acharya (sa8267)"
__author__      = "Anurag Chandra (ac5068)"
__instructor__  = "Minseok Kwon"
__filename__    = "dns_resolver.py"

import socket
import random
import struct
import time
import threading
import root_servers as root
import server_resource_records as r_records

# Constants
ID_LEN      = 16
DNS_PORT    = 53
BUF_LEN     = 1024
HEADER_LEN  = 12
OFFSET_MARK = 192
STOP_THREAD = False
# Type value constants
A           = 1
CNAME       = 5
NS          = 2
AAAA        = 28
SOA         = 6

type_lkup = {1: "A", 5: "CNAME", 2: "NS", 6: "SOA", 28: "AAAA"}

import enum
class RRTYPE(enum.Enum):
    A = 1
    CNAME = 5
    NS = 2
    SOA = 6
    HTTPS = 65
    AAAA = 28

def delete_expired_entries_continuously():
    while not STOP_THREAD:
        for domain_name in r_records.cached_records.copy():
            if STOP_THREAD:
                break
            if r_records.cached_records[domain_name]["timestamp"] <= time.time():
                del r_records.cached_records[domain_name]
delete_cache_entries = threading.Thread(target=delete_expired_entries_continuously)
delete_cache_entries.start()

# A class for resource records (RRs)


# Use an in-memory list (equivalent to cache) with each entry as a
# resource record object

# SIGALARM to ensure that the RRs are invalidated and removed from the
# cache list after TTL. TTL is received from the DNS server response and
# alarm is set to the received TTL value.        


def get_name( response: bytes, position: int ):
    """
    Fetches the name field of each Answer in RR from the received
    payload.

    :param rcvd_payload: the payload received payload from a DNS server
    :param position: the start position of name bytes
    """
    qname = ''

    while True:
        length = response[position]
        if length == 0:
            # end = 1
            position += 1
            break
        
        # offset in the name
        if length == OFFSET_MARK:
            qname += '.' if qname else ''
            qname_temp, position_temp = \
                get_name ( response, response[position + 1] )
            qname += qname_temp

            # skip the \x0c and pointer address as well
            position += 2
            break

        qname += '.' if qname else ''
        qname += response[position+1:position+1+length].decode()
        position += ( 1 + length )

    return qname, position

def query_construct(domain: str, qtype='A', server='8.8.8.8'):
    """
    Creates query for a domain name

    :param domain: The domain name for which the DNS query is to be run.
    :param qtype: Query type like A, CNAME, AAAA, NS.
    :param server: DNS Server IP or URL, if not provided, default to
                   8.8.8.8 ( Google's DNS ). 
    """
    # construct DNS query message
    
    # a random 16-bit value for each query
    transaction_id = random.getrandbits( ID_LEN )

    # Standard query with recursion desired and one query count
    q_header = struct.pack('!HHHHHH', transaction_id, 0x0100, \
                           0x0001, 0x0000, 0x0000, 0x0000)
    # q_header = struct.pack('!HHHHHH', id, id,id,id,id,id)

    # print('DNS query header:', q_header.hex())

    flags       = 0b0000000100000000  # standard query, with recursion

    questions   = 1     # Number of queries
    answers     = 0     # Number of answers
    authority   = 0     # Authority bits clear as a query
    additional  = 0     # Additional section in the query
    qname       = b''   # The domain name to store in bitwise notation

    
    for label in domain.split('.'):
        qname += bytes([len(label)]) + label.encode()

    qname += b'\x00'  # terminate domain name with null byte

    qtype = {'A': A, 'AAAA': AAAA, 'CNAME': CNAME, 'NS': NS,\
             'SOA': SOA}.get(qtype, 1)  # default to A record

    qclass = 1  # internet (IN) class
    query = (transaction_id).to_bytes(2, byteorder='big') + \
            (flags).to_bytes(2, byteorder='big') + \
            (questions).to_bytes(2, byteorder='big') + \
            (answers).to_bytes(2, byteorder='big') + \
            (authority).to_bytes(2, byteorder='big') + \
            (additional).to_bytes(2, byteorder='big') + \
            qname + \
            (qtype).to_bytes(2, byteorder='big') + \
            (qclass).to_bytes(2, byteorder='big')
    
    # print(f"Query: {query}")

    return query


def recursive_search( domain: str ):
    """
    Performs a recursive look up for the domain names which couldn't
    be found in the resolver cache.

    :param domain: Domain name to be searched recursively.
    """

    # start with the last label, and find the authorative server

    labels = domain.split('.')[::-1]

    name = ""

    server = root.root_server_add[0]

    for label in labels:
        name = label + ('.' if name else '') + name
        print("\n\n\n\n")
        print(f"Domain: {name}\nServer: {server}")

        # construct a DNS query with the label found so far and NS
        rrs = resolve( name, "NS",  server)
        if not rrs:
            return None
        authority_rrs = rrs["Authority"]
        server = authority_rrs[0][-1]

    print(f"SERVER: {server}\tName: {name}")

    # resolve( name, 'A', server)
    return server


def get_rrs( response, i, answers ):
    """
    Parses the resource records section of the response and creates the
    resource records.

    :param response: response received from the DNS query
    :param position: start position of the response
    :param answers: count of the resource records in the response
    """
    answers_rr = []
    
    for _ in range(answers):
        rrname, i = get_name( response, i )
       
        rrtype = int.from_bytes(response[i:i+2], byteorder='big')
        i += 2

        rrclass = int.from_bytes(response[i:i+2], byteorder='big')
        i += 2

        ttl = int.from_bytes(response[i:i+4], byteorder='big')
        i += 4

        rdlength = int.from_bytes(response[i:i+2], byteorder='big')
        i += 2

        # print(f"rrtype: {rrtype}\trrclas:{rrclass}\tttl:{ttl}\trdlength:{rdlength}")

        rdata = response[i : i + rdlength]

        if rrtype == A:  # A record
            answer = ( socket.inet_ntoa(rdata), 0)
        elif rrtype == AAAA:  # AAAA record
            answer = socket.inet_ntop( socket.AF_INET6, rdata )
        elif rrtype == CNAME:
            answer = get_name( response, i )
        elif rrtype == NS:
            answer = get_name( response, i )
        elif rrtype == SOA:
            answer = get_name( response, i )
        else:
            answer = rdata.hex()
        
        answers_rr.append( [rrname, rrtype, rrclass, ttl, answer[0]] )
        # if type(rrtype) == int:
        #     rrtype = type_lkup[rrtype]
        # Add to the cached list, if not already present
        if rrname not in r_records.cached_records:
            r_records.cached_records[rrname] = {"rrtype": rrtype, 
                                                "rrclass": rrclass, 
                                                "ttl": ttl, 
                                                "address": answer[0],
                          "timestamp": time.time() + ttl,                      }
            
            # Start the alarm
            # print(f"Starting alarm for {rrname} for {ttl} seconds")
            # signal.signal(signal.SIGINT, partial(signal_handler, rrname))
            # signal.alarm(ttl)

        # Move the pointer ahead by rdlength
        i += rdlength

        # print(answers_rr)
    
    return answers_rr, i


def search_cached_rrs( domain_name: str, qtype: str ):
    """
    Looks for the domain name and record type in the existing valid cache.

    :param domain_name: Domain name to be searched in for the caches.
    :param qtype: Domain record type.
    """
    rrs = {}

    if (domain_name in r_records.cached_records):
        
        # Find in the list of the domain name found
        a_record = r_records.cached_records[domain_name]
        if a_record["rrtype"] == qtype: 
                rrs["Answer"] = [[domain_name, a_record["rrtype"], a_record["rrclass"], a_record["ttl"], a_record["address"]]]
                rrs["Authority"] = []
            
    
    return rrs


def resolve(domain, qtype='A', server='1.1.1.1'):
    """
    It gets the mapping from domain names to the IP address or CNAME
    resource.

    :param domain: Domain name to be queried for DNS.
    :param qtype: Request type in the DNS query.
    :param server: DNS server location.
    """

    query = query_construct(domain, qtype, server)

    # send DNS query over UDP to specified server and receive response
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # wait up to 5 seconds for response

    try:
        sock.sendto(query, (server, DNS_PORT))
        response, _ = sock.recvfrom( BUF_LEN )
    except socket.timeout:
        # print( "Request Timedout" )
        return None
    finally:
        sock.close()

    # parse DNS response message
    transaction_id, flags, questions, answers, authority, additional = \
        [int.from_bytes(response[i:i+2], byteorder='big') for i in range(0, 12, 2)]
    # Extract the flag bits
    qr = (flags & 0b1000000000000000) >> 15
    opcode = (flags & 0b0111100000000000) >> 11
    aa = (flags & 0b0000010000000000) >> 10
    tc = (flags & 0b0000001000000000) >> 9
    rd = (flags & 0b0000000100000000) >> 8
    ra = (flags & 0b0000000010000000) >> 7
    z  = (flags & 0b0000000001000000) >> 6
    rcode = (flags & 0b0000000000111111)
    if rcode != 0:
        print(f"Error: DNS server returned error code {rcode}")
        return []
    # 12 bytes headers are parsed, so skip them
    i = HEADER_LEN

    # Extract the domain name from response
    qname, i = get_name( response, i )

    # qtype: 1 for A type and 5 for CNAME type
    qtype, qclass = [int.from_bytes(response[i:i+2], byteorder='big')\
                      for i in range(i, i+4, 2)]

    i += 4  # skip question section (qtype and qclass) - 4 octets

    # Extract the answer section - A & CNAME type resource records
    answers_rr, i = get_rrs( response, i, answers )

    print(f"Answers: {answers_rr}" )

    authority_rr, i = get_rrs( response, i, authority )
    
    print( f"Authority Servers: {authority_rr}" )



    rrs = {"Answer": answers_rr, "Authority": authority_rr}
    return rrs


def print_fn( rrs ):
    """
    Prints the resource records in a formatted way.

    :param rrs: resource records found in the query
    """

    # Header of the output
    print("\n\nHEADER: ANSWER SECTION")

    # loop through the records and print them
    answers = rrs["Answer"]

    for a_record in answers:
        print(f"Name:\t{a_record[0]}")
        print(f"Type:\t{type_lkup[a_record[1]]}")
        print(f"Class:\t{a_record[2]}")
        print(f"TTL:\t{a_record[3]}")
        print(f"Server:\t{a_record[4]}\n")

    print("\n\nHEADER: AUTHORITY SECTION")
    ns = rrs["Authority"]

    for a_record in ns:
        print(f"Name:\t{a_record[0]}")
        print(f"Type:\t{type_lkup[a_record[1]]}")
        print(f"Class:\t{a_record[2]}")
        print(f"TTL:\t{a_record[3]}")
        print(f"Server:\t{a_record[4]}\n")

def run_dns_search( domain_name: str, qtype = "A"):
    """
    Driver function for the DNS search
    :param domain_name: the domain name to be searched
    """

    rrs = search_cached_rrs( domain_name, RRTYPE[qtype].value )

    if not len(rrs):
        # search the local server
        rrs = resolve(domain_name, qtype)
        # if error response search recursively
        if not rrs:
            authority_server = recursive_search( domain_name )
            if not authority_server:
                return
            rrs = resolve( domain_name, qtype, authority_server )

    return rrs

if __name__ == '__main__':
    pass