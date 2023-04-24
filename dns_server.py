# -*- coding: utf-8 -*-
"""
About: Project #6 of CSCI-651-FoundationsOfComputerNetworks course.
Description: This program serves as the DNS server implementation.
"""

__author__      = "Khushi Mahesh (km1139)"
__author__      = "Shreenidhi Vittala Acharya (sa8267)"
__author__      = "Anurag Chandra (ac5068)"
__instructor__  = "Minseok Kwon"
__filename__    = "dns_server.py"

# Add the code below this line
import socket
import dns_constants as const
import dns_resolver as resolver

def populate_cache():
    """
    Cache is a list of tuples. Each tuple has the type, name,  value, and TTL associated
    """
    const.CACHED_ENTRIES["chat.google.com"] = ["A", "142.251.40.238", 100]

def parse_dns_query(request):
    """
    Extract the domain name from the DNS query and what type of query it is.
    """
    #1. extract the header
    header = request[:const.HEADER_LEN]
    question_count = int.from_bytes(header[4:6], byteorder='big')

    #2. extract the question
    queries = request[const.HEADER_LEN:]
    
    # domain name is followed by 2 bytes of type and 2 bytes of class
    # extract domain name and decode it
    qname = ''
    count = 0
    # keep appending till we hit null byte
    offset = const.HEADER_LEN
    while True:
        label_length = request[offset]
        if label_length == 0:
            # End of QNAME
            # Increment offset by 1 to move past the null byte
            offset += 1
            break
        qname += request[offset + 1:offset + 1 + label_length].decode(const.ENCODING) + '.'
        offset += 1 + label_length

    # Remove the trailing dot
    qname = qname[:-1]
    
    query_type = int.from_bytes(request[offset:offset+2], byteorder='big')

    offset += 2
    query_class = int.from_bytes(request[offset:offset+2], byteorder='big')
    return qname, query_type, query_class

def construct_header_question(request, error=False):
    #1. extract the header
    header = request[:const.HEADER_LEN]
    # print("header", header)
    #1.a change the header to indicate that the response is a response
    # in the 2nd byte of the header, the first bit is 1 for response
    
    if not error:
        rcode = header[3]
    else:
        rcode = header[3] | 0b00000011
    
    new_header = header[:2] + bytes([header[2] | 0b10000000]) + bytes(rcode) + header[4:7] + (const.NUM_A_RR).to_bytes(2, byteorder='big') + header[8:]
    
    #2. extract the question
    question = request[const.HEADER_LEN:]
    return new_header + question


def construct_error_response(request):
    """
    Construct the error response to be sent to the client.
    """
    new_header_question = construct_header_question(request, True)
    return new_header_question

def construct_response(request, query_type, query_class, answer: str):
    """
    Construct the response to be sent to the client.
    """
    #1, construct the header and question
    new_header_question = construct_header_question(request)
    #2.b convert the IP address in answer to the format required by the DNS response
    answer_bytes = bytes(map(int, answer.split('.')))
    #2.c construct the answer
    # pointer to the domain name in the question
    # type of query
    # class of query
    # TTL
    # length of the answer
    # answer
    answer_length = const.IP_LENGTH.to_bytes(2, byteorder='big')
    if query_type == 1:
        answer_length = const.IP_LENGTH.to_bytes(2, byteorder='big')
    answer_format = const.NAME_POINTER + \
                    (query_type).to_bytes(2, byteorder='big') + \
                    (query_class).to_bytes(2, byteorder='big') + \
                    (const.INITIAL_TTL).to_bytes(4, byteorder='big') + \
                    answer_length + \
                    answer_bytes
    #3. construct the response
    response = new_header_question + answer_format
    #4. send the response back to the client
    return response

def check_domain_name_entry(domain_name_to_query, query_type, query_class):
    """
    Check if the domain name is present in the master zone file.
    """
    return const.CACHED_ENTRIES[domain_name_to_query][1]

def parse_resolver_request(dns_server_socket):
    while True:
        # 2. When a connection is received, parse the request
        # 2.1. Read the request from the socket
        request, client_address = dns_server_socket.recvfrom(const.BUF_LEN)
        # 2.2. Extract the domain name and the type of query
        domain_name_to_query, query_type, query_class = parse_dns_query(request)


        # 2.3. Check if the domain name is present in the cache

        # let cache be a list of most recently used domain names

        # 2.4. If not, check if the domain name is present in the master zone file
        answer = check_domain_name_entry(domain_name_to_query, query_type, query_class)
        # 2.5. Send the response back to the client if the domain name is present in the master zone file else send an error message
        if answer:
            # 2.6. construct the response
            print(request)
            print(domain_name_to_query, query_type, query_class, answer)
            response = construct_response(request, query_type, query_class, answer)
            print(response)
            # 2.7. send the response back to the client
            dns_server_socket.sendto(response, client_address)
        else:
            # 2.8. send an error message
            construct_error_response(request)


def main():
    print("DNS Server")
    populate_cache()
    # TODO: Implement the DNS server
    # 1. Create a socket that is always listening for incoming connections and bind it to port 53
    dns_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_server_socket.bind(('', const.DNS_PORT))
    # for maintainence queries use the SOCK_STREAM since it is a connection oriented protocol - TODO as multi threaded server
    # 2. When a connection is received, parse the request
    parse_resolver_request(dns_server_socket)

if __name__ == '__main__':
    main()