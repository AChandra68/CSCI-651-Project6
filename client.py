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
import sys
import dns_resolver as resolver

def help():
    """
    Print the help menu
    """
    print("The following commands are available:")
    print("help - Print the help menu")
    print("query - Query the DNS server")
    print("exit - Exit the program")

def main():
    """
    Main function for the DNS client
    """
    #1. Take input from the user
    #2. Send the query to the resolver
    #3. Print the response
    while True:
        print(f"\033[92mpktsniffer> \033[0m", end = "", flush = True)
        try:
            opt = sys.stdin.readline()
            if opt == "exit\n":
                print("Exiting...")
                break
            elif opt == "help\n":
                help()
            elif opt == "query\n":
                print("Enter the query type: ")
                print("A")
                print("CNAME")
                query_type = sys.stdin.readline().strip()
                print("Enter the domain name: ")
                domain_name = sys.stdin.readline().strip()
                rrs = resolver.run_dns_search(domain_name, query_type)
                if rrs:
                    resolver.print_fn(rrs)
                
        except Exception as e:
            print("Error reading input. Please try again\n", e)
            continue


if __name__ == "__main__":
    main()

