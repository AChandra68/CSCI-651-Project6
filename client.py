# -*- coding: utf-8 -*-
"""
About: Project #6 of CSCI-651-FoundationsOfComputerNetworks course.
Description: This program serves as the DNS client implementation.
"""

__author__      = "Khushi Mahesh (km1139)"
__author__      = "Shreenidhi Vittala Acharya (sa8267)"
__author__      = "Anurag Chandra (ac5068)"
__instructor__  = "Minseok Kwon"
__filename__    = "dns_client.py"

# Add the code below this line



import socket

def resolve(domain, qtype='A', server='8.8.8.8'):
    # construct DNS query message
    transaction_id = 1234  # change this to a random value for each query
    flags = 0b0000000100000000  # standard query, no recursion
    questions = 1
    answers = 0
    authority = 0
    additional = 0
    qname = b''
    for label in domain.split('.'):
        qname += bytes([len(label)]) + label.encode()
    qname += b'\x00'  # terminate domain name with null byte
    qtype = {'A': 1, 'AAAA': 28}.get(qtype, 1)  # default to A record
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
    
    # send DNS query over UDP to specified server and receive response
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)  # wait up to 5 seconds for response
    try:
        sock.sendto(query, (server, 53))
        response, _ = sock.recvfrom(1024)
    except socket.timeout:
        print( "Request Timedout" )

    finally:
        sock.close()

    # parse DNS response message
    transaction_id, flags, questions, answers, authority, additional = \
        [int.from_bytes(response[i:i+2], byteorder='big') for i in range(0, 12, 2)]
    qr = (flags & 0b1000000000000000) >> 15
    opcode = (flags & 0b0111100000000000) >> 11
    aa = (flags & 0b0000010000000000) >> 10
    tc = (flags & 0b0000001000000000) >> 9
    rd = (flags & 0b0000000100000000) >> 8
    ra = (flags & 0b0000000010000000) >> 7
    z = (flags & 0b0000000001000000) >> 6
    rcode = (flags & 0b0000000000111111)
    qname = ''
    i = 12
    while True:
        length = response[i]
        if length == 0:
            break
        qname += '.' if qname else ''
        qname += response[i+1:i+1+length].decode()
        i += 1 + length
    qtype, qclass = [int.from_bytes(response[i:i+2], byteorder='big') for i in range(i, i+4, 2)]
    answers_rr = []
    i += 4  # skip question section
    for _ in range(answers):
        rrname = ''
        while True:
            length = response[i]
            if length == 0:
                break
            rrname += '.' if rrname else 'jlj'
            print(response)
            rrname += response[i+1:i+1+length].decode()
            i += 1 + length
        rrtype, rrclass, ttl, rdlength = \
            [int.from_bytes(response[i:i+2], byteorder='big') for i in range(i, i+8, 2)]
        rdata = response[i+8:i+8+rdlength]
        if rrtype == 1:  # A record
            answer = socket.inet_ntoa(rdata)
        elif rrtype == 28:  # AAAA record
            answer = socket.inet_ntop(socket.AF_INET6, rdata)
        else:
            answer = rdata.hex()
        answers_rr.append((rrname, rrtype, rrclass, ttl, answer))
        i += 8 + rdlength

    if rcode != 0:
        print(f"Error: DNS server returned error code {rcode}")
        return []
    elif answers == 0:
        print(f"Error: no {qtype} records found for {domain}")
        return []
    else:
        return [answer for _, _, _, _, answer in answers_rr]

if __name__ == '__main__':

    ip_addresses = resolve( "techiehustle.com" )