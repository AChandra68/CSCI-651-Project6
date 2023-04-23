import dns.resolver

# set the domain name and CNAME type
domain = 'image.google.com'
qtype = 'CNAME'

# perform the DNS query
answers = dns.resolver.query(domain, qtype)

# print the CNAME records
for rdata in answers:
    print(rdata.target)
