# CSCI-651-Project6
Final project for the course  CSCI-651-FoundationsOfComputerNetworks (Spring 2023)

Further details can be found in [this](https://drive.google.com/drive/folders/1XYPKPuYym2mWvAl_ioeTcntkWOzzrO7S?usp=share_link) Google document.

## Team Members
1. Khushi Mahesh (km1139)
2. Shreenidhi Vittala Acharya (sa8267)
3. Anurag Chandra (ac5068)


## Project Description
The project is to implement DNS client and server using UDP to fetch records for A and CNAME type of queries.

## Steps to run the code
1. Clone the repository
2. Run the server code using the command `python3 dns_server.py`
3. Run the client code using the command `python3 client.py` which opens an interactive terminal
4. There are 3 options - query, help and exit
5. Enter `help` to see the list of commands
6. Enter `query` to fetch the records for a domain name
7. Enter `exit` to exit the terminal
8. In the query command, enter the type of query - A or CNAME
10. Also enter if recursion is desired or not
9. Then enter the domain name for which you want to fetch the records
10. The records are displayed on the terminal
