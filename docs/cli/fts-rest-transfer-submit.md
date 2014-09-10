% FTS-REST-CLI(1) fts-rest-transfer-submit
% fts-devel@cern.ch
% July 15, 2014
# NAME

fts-rest-transfer-submit

# SYNOPIS

Usage: fts-rest-transfer-submit [options] SOURCE DESTINATION [CHECKSUM]

# DESCRIPTION

This command can be used to submit new jobs to FTS3. It supports simple and bulk submissions. The bulk
format is as follows:

```json
{
  "files": [
    {
      "sources": [
        "gsiftp://source.host/file"
      ],
      "destinations": [
        "gsiftp://destination.host/file"
      ],
      "metadata": "file-metadata",
      "checksum": "ADLER32:1234",
      "filesize": 1024
    },
    {
      "sources": [
        "gsiftp://source.host/file2"
      ],
      "destinations": [
        "gsiftp://destination.host/file2"
      ],
      "metadata": "file2-metadata",
      "checksum": "ADLER32:4321",
      "filesize": 2048
    }
  ]
}
```


# OPTIONS

-h/--help
:	Show this help message and exit

-v/--verbose
:	Verbose output. 

-s/--endpoint
:	Fts3 rest endpoint. 

-j/--json
:	Print the output in json format. 

--key
:	The user certificate private key. 

--cert
:	The user certificate. 

--insecure
:	Do not validate the server certificate

-b/--blocking
:	Blocking mode. Wait until the operation completes. 

-i/--interval
:	Interval between two poll operations in blocking mode. 

-e/--expire
:	Expiration time of the delegation in minutes. 

-o/--overwrite
:	Overwrite files. 

-r/--reuse
:	Enable session reuse for the transfer job. 

--job-metadata
:	Transfer job metadata. 

--file-metadata
:	File metadata. 

--file-size
:	File size (in bytes)

-g/--gparam
:	Gridftp parameters. 

-t/--dest-token
:	The destination space token or its description. 

-S/--source-token
:	The source space token or its description. 

-K/--compare-checksum
:	Compare checksums between source and destination. 

--copy-pin-lifetime
:	Pin lifetime of the copy in seconds. 

--bring-online
:	Bring online timeout in seconds. 

--fail-nearline
:	Fail the transfer is the file is nearline. 

--dry-run
:	Do not send anything, just print the json message. 

-f/--file
:	Name of configuration file

--retry
:	Number of retries. If 0, the server default will be used. If negative, there will be no retries. 

-m/--multi-hop
:	Submit a multihop transfer. 

# EXAMPLE
```
$ fts-rest-transfer-submit -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file gsiftp://destination.host/file
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

$ fts-rest-transfer-submit -s https://fts3-devel.cern.ch:8446 -f bulk.json
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

```