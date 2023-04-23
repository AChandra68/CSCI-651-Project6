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


def populate_cache():
    """
    Cache is a list of tuples. Each tuple has the type, name,  value, and TTL associated
    """
    const.CACHED_ENTRIES["www.google.com"] = ["A", "142.251.40.238", 100]

def parse_dns_query(request):
    """
    Extract the domain name from the DNS query and what type of query it is.
    """
    #1. extract the header
    header = request[:const.HEADER_LEN]
    question_count = int.from_bytes(header[4:6], byteorder='big')

    #2. extract the question
    question = request[const.HEADER_LEN:]
    # first byte indicates the length of the domain name
    domain_name_len = question[0]
    # domain name is followed by 2 bytes of type and 2 bytes of class
    # extract domain name and decode it
    domain_name_to_query = ""
    count = 0
    # keep appending till we hit null byte
    while question[domain_name_len+1] != 0:
        domain_name_to_query += question[1+count:domain_name_len+1].decode(const.ENCODING)
        domain_name_to_query += "."
        count += domain_name_len
        domain_name_len = question[domain_name_len+1]
        
    # remove the last dot
    domain_name_to_query = domain_name_to_query[:-1]

    #3. extract the type of query
    query_type = question[domain_name_len+1:domain_name_len+3]

    #4. extract the class of query
    query_class = question[domain_name_len+3:domain_name_len+5]

    print("Domain name to query: ", domain_name_to_query)
    return domain_name_to_query, query_type, query_class


def construct_error_response(request):
    """
    Construct the error response to be sent to the client.
    """
    #1. extract the header
    header = request[:const.HEADER_LEN]
    #1.a change the header to indicate that the response is a response
    # in the 2nd byte of the header, the first bit is 1 for response
    header[2] = header[2] | 0b10000000

    #1.b number of answer records in the response
    header[6] = 0  # 0 answer records
    #2. extract the question
    question = request[const.HEADER_LEN:]
    #3. construct the response
    response = header + question
    #4. send the response back to the client
    return response

def construct_response(request, answer: str):
    """
    Construct the response to be sent to the client.
    """
    #1. extract the header
    header = request[:const.HEADER_LEN]
    #1.a change the header to indicate that the response is a response
    # in the 2nd byte of the header, the first bit is 1 for response
    header[2] = header[2] | 0b10000000

    #1.b number of answer records in the response
    header[6] = const.NUM_A_RR  # 1 answer record
    #2. extract the question
    question = request[const.HEADER_LEN:]
    #2.b convert the IP address in answer to the format required by the DNS response
    answer_bytes = bytes(map(int, answer.split('.')))
    #2.c construct the answer
    # pointer to the domain name in the question
    # type of query
    # class of query
    # TTL
    # length of the answer
    # answer
    answer_format = b'\xc0\x0c' + b'\x00\x01' + b'\x00\x01' + b'\x00\x00\x07\x08' + b'\x00\x04' + answer_bytes
    #3. construct the response
    response = header + question + answer_format
    #4. send the response back to the client
    return response

def check_domain_name_entry(domain_name_to_query, query_type, query_class):
    """
    Check if the domain name is present in the master zone file.
    """
    const.CACHED_ENTRIES

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
            response = construct_response(request, answer)
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