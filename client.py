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
import time
import datetime

def help():
    """
    Print the help menu
    """
    print("The following commands are available:")
    print("1. help - Print the help menu")
    print("2. query - Query the DNS server")
    print("The query type is of 2 types: A and CNAME")
    print("The recursion desired from server can be set via Y or N")
    print("3. exit - Exit the program")

def display_metrics(time_req, current_time, msg_size):
    """
    Display the metrics
    """
    print(f";; Query time: {time_req} msec")
    
    current_time_str = current_time.strftime("%a %b %d %H:%M:%S %Z %Y")
    print(f";; WHEN: {current_time_str}") 
    print(f";; MSG SIZE  rcvd: {msg_size}")

def main():
    """
    Main function for the DNS client
    """
    #1. Take input from the user
    #2. Send the query to the resolver
    #3. Print the response
    while True:
        print(f"\033[92mdns> \033[0m", end = "", flush = True)
        try:
            opt = sys.stdin.readline()
            if opt == "exit\n":
                print("Exiting...")
                break
            elif opt == "help\n":
                help()
            elif opt == "query\n":
                print("Enter the query type: ")
                
                query_type = sys.stdin.readline().strip()
                print("Enter if recursion desired: (Y/N)")
                recursion_desired = sys.stdin.readline().strip()
                
                if recursion_desired == "Y":
                    rd = True
                else:
                    rd = False
                print("Enter the domain name: ")
                domain_name = sys.stdin.readline().strip()
                start_time = time.time()
                current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
                rrs = resolver.run_dns_search(domain_name, rd, query_type)
                if rrs:
                    resolver.print_fn(rrs)
                    end_time = time.time()
                    display_metrics(end_time - start_time, current_time, sys.getsizeof(rrs))
            else:
                print("Invalid option. Please try again")
                continue
                
        except Exception as e:
            print("Error reading input. Please try again\n", e)
            continue


if __name__ == "__main__":
    main()

