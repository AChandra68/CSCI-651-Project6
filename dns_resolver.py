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

# Constants
ID_LEN      = 16
DNS_PORT    = 53
BUF_LEN     = 1024
HEADER_LEN  = 12
# A class for resource records (RRs)


# Use an in-memory list (equivalent to cache) with each entry as a
# resource record object

# SIGALARM to ensure that the RRs are invalidated and removed from the
# cache list after TTL. TTL is received from the DNS server response and
# alarm is set to the received TTL value.

def get_name( response, position: int ):
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
        if length == 192:
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
    """
    # construct DNS query message
    
    # a random 16-bit value for each query
    transaction_id = random.getrandbits(ID_LEN)

    # Standard query with recursion desired and one query count
    q_header = struct.pack('!HHHHHH', transaction_id, 0x0100, 0x0001, 0x0000, 0x0000, 0x0000)
    # q_header = struct.pack('!HHHHHH', id, id,id,id,id,id)

    print('DNS query header:', q_header.hex())

    flags = 0b0000000100000000  # standard query, no recursion
    questions = 1
    answers = 0
    authority = 0
    additional = 0
    qname = b''

    for label in domain.split('.'):
        qname += bytes([len(label)]) + label.encode()

    qname += b'\x00'  # terminate domain name with null byte

    # to-do other record types
    qtype = {'A': 1, 'AAAA': 28, 'CNAME': 5}.get(qtype, 1)  # default to A record

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
    
    print(f"Query: {query}")

    return query

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
        # rrtype, rrclass, ttl, rdlength = \
        #     [int.from_bytes(response[i:i+2], byteorder='big') for i in range(i, i+8, 2)]
        rrtype = int.from_bytes(response[i:i+2], byteorder='big')
        i += 2

        rrclass = int.from_bytes(response[i:i+2], byteorder='big')
        i += 2

        ttl = int.from_bytes(response[i:i+4], byteorder='big')
        i += 4

        rdlength = int.from_bytes(response[i:i+2], byteorder='big')
        i += 2

        print(f"rrtype: {rrtype}\trrclas:{rrclass}\tttl:{ttl}\trdlength:{rdlength}")

        rdata = response[i : i + rdlength]

        if rrtype == 1:  # A record
            answer = socket.inet_ntoa(rdata)
        elif rrtype == 28:  # AAAA record
            answer = socket.inet_ntop(socket.AF_INET6, rdata)
        elif rrtype == 5:
            answer = get_name( response, i )
        else:
            answer = rdata.hex()
        answers_rr.append((rrname, rrtype, rrclass, ttl, answer))
        i += rdlength

        # print(answers_rr)
    
    return answers_rr


def resolve(domain, qtype='A', server='8.8.8.8'):
    """
    """

    query = query_construct(domain, qtype, server)

    # send DNS query over UDP to specified server and receive response
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # wait up to 5 seconds for response

    try:
        sock.sendto(query, (server, DNS_PORT))
        response, _ = sock.recvfrom( BUF_LEN )
    except socket.timeout:
        print( "Request Timedout" )

    finally:
        sock.close()

    print(f"Rcvd response: {response}")

    # parse DNS response message
    transaction_id, flags, questions, answers, authority, additional = \
        [int.from_bytes(response[i:i+2], byteorder='big') for i in range(0, 12, 2)]
    
    qr = (flags & 0b1000000000000000) >> 15
    opcode = (flags & 0b0111100000000000) >> 11
    aa = (flags & 0b0000010000000000) >> 10
    tc = (flags & 0b0000001000000000) >> 9
    rd = (flags & 0b0000000100000000) >> 8
    ra = (flags & 0b0000000010000000) >> 7
    z  = (flags & 0b0000000001000000) >> 6
    rcode = (flags & 0b0000000000111111)
    
    # qname = 

    # 12 bytes headers are parsed, so skip them
    i = HEADER_LEN

    # Extract the domain name from response
    qname, i = get_name( response, i )

    # qtype: 1 for A type and 5 for CNAME type
    qtype, qclass = [int.from_bytes(response[i:i+2], byteorder='big') for i in range(i, i+4, 2)]

    i += 4  # skip question section (qtype and qclass)
    
    print(f"i={i}\t{response[i]}\t{response[i+1]}\t{response[i+2]}")

    answers_rr = get_rrs( response, i, answers )
    
    print(answers_rr)

    if rcode != 0:
        print(f"Error: DNS server returned error code {rcode}")
        return []
    elif answers == 0:
        print(f"Error: no {qtype} records found for {domain}")
        return []
    else:
        return [answer for _, _, _, _, answer in answers_rr]

if __name__ == '__main__':

    ip_addresses = resolve( "image.google.com" )