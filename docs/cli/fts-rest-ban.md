% FTS-REST-CLI(1) fts-rest-ban
% fts-devel@cern.ch
% May 21, 2019
# NAME

fts-rest-ban

# SYNOPIS

Usage: fts-rest-ban [options]

# DESCRIPTION

Ban and unban storage elements and users

# OPTIONS

-h/--help
:	Show this help message and exit

-v/--verbose
:	Verbose output. 

-s/--endpoint
:	FTS3 REST endpoint. 

-j/--json
:	Print the output in json format. 

--key
:	The user certificate private key. 

--cert
:	The user certificate. 

--capath
:	Use the specified directory to verify the peer

--insecure
:	Do not validate the server certificate

--access-token
:	Oauth2 access token (supported only by some endpoints, takes precedence)

--storage
:	Storage element

--user
:	User dn

--unban
:	Unban instead of ban

--status
:	Status of the jobs that are already in the queue: cancel or wait

--timeout
:	The timeout for the jobs that are already in the queue if status is wait

--allow-submit
:	Allow submissions if status is wait

# EXAMPLE
```
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample
No jobs affected
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample --unban
$

```
