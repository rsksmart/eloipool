
Pre requisites
-------------

* A machine running linux (tested with Ubuntu 14.04 LTS)
* Python 3 (tested with python 3.4)
* A python virtualenv updated to most recent packages.
* Bitcoind (in the example located at 192.168.0.118, port 21591, rpc port 22591)
* RoostockJ (in the example located at 192.168.0.118, rpc port 4445)


Installation
------------

This instructions are partially based on https://github.com/luke-jr/eloipool/issues/3

0) Installation of dependencies will be done inside a python virtualenv

> sudo apt-get install python3-venv
> python3 -m venv pyenv
> source pyenv/bin/activate

1) Clone eloipool repo

> git clone https://github.com/rootstock/eloipool.git

2) Install dependencies

> cd eloipool

2.1) python-bitcoinrpc

> pip install -e git+https://github.com/jgarzik/python-bitcoinrpc.git#egg=python-bitcoinrpc

After commit df459b7c00d6a9320fe7adcfa11e9c812127ffa3 there's an extra check for the Content-Type "application/json"

> pip install -e git+https://github.com/jgarzik/python-bitcoinrpc.git@df459b7c00d6a9320fe7adcfa11e9c812127ffa3#egg=python_bitcoinrpc

2.2) python-base58

(Doesn't have an installer)

> git clone https://gitlab.com/bitcoin/python-base58.git
> ln -s python-base58/base58.py base58.py


Configuration
-------------

Important: Eloipool only uses IPv6 sockets, to address an IPv4 server it should be changed
from 192.168.0.118 to ::FFFF:192.168.0.118.

Make a copy of the example configuration to edit

> cp config.py.example config.py


The fields that should be customized:

* ShareTarget

The default target that will be sent to miners. Default target is 
0x00000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffff,
which is difficult 1.0.

* CoinbaserCmd 

Command called before sending a solved block to bitcoind. Used to split the block rewards.
Assign a value of None.

CoinbaserCmd = None

* TemplateSources

This is a list of the bitcond servers that will be queried for new blocks to mine.
The uri field is the address of the rpc interface of bitcoind.

TemplateSources = (
	{
		'name': 'primary',
		'uri': 'http://admin:admin@127.0.0.1:22591',
		'priority': 0,
		'weight': 1,
	},
)

* TemplateChecks

Assign a value of None.

TemplateChecks = None

* BlockSubmissions

Assign a value of None.

BlockSubmissions = None

* UpstreamBitcoindNode

Point to p2p port bitcoind, or None

UpstreamBitcoindNode = None

* StratumAddresses

Address where the pool will listen to stratum requests from miners

StratumAddresses = (
    ('::FFFF:192.168.0.121', 3333),
	('::FFFF:127.0.0.1', 3333),
)

* ShareLogging

Keep the logfile logger, remove all others 

ShareLogging = (
	{
		'type': 'logfile',
		'filename': 'share-logfile',
		'format': "{time} {Q(remoteHost)} {username} {YN(not(rejectReason))} {dash(YN(upstreamResult))} {dash(rejectReason)} {solution}\n",
	},
)


* LogFile

Here we specify the filename of the log 

LogFile = {
	'filename': 'eloipool.log',
	'when': 'midnight',
	'backupCount': 7,
}

Roostock configuration
----------------------

* RootstockSources

Similar to TemplateSources, points to Rskd server 

RootstockSources = (
	{
		'name': 'primary',
		'uri': 'http://user:pass@192.168.0.118:4445',
		'priority': 0,
		'weight': 1,
	},
)

* RootstockPollPeriod

Time in seconds betweeen request to Rskd server

RootstockPollPeriod = 2.0

* RootstockNotifyPolicy

The policy to use when new work arrive from Rskd

RootstockNotifyPolicy = 2



Run Eloipool
------------


It can be launched like this

> python eloipool.py


Shutdown Eloipool
-----------------

In the console running Eloipool.py we can press Enter to access a python console.
It will display a >>> as a prompt. We can shutdown eloipool from there typing exit().

This console is running inside the pool and can be used to debug or inspect its state.
For example: 
>>> print(MM.Rootstock.target) 

will print the target of the last work from RSKD


Parsing eloipool logs
=====================

Prerequisites
-------------

Install parse ( https://pypi.python.org/pypi/parse )

> pip install parse


Execution
---------

Calling it without arguments will display a usage text

> python3 logparser.py

usage: logparser.py [-h] [-o OUTPUT] [-s] logFile                  
logparser.py: error: the following arguments are required: logFile 

With -o OUTPUT will extract the logged actions from the log file and will
write it to in CSV format to the file specified.

> python3 logparser.py ../eloipool.log -o actions.csv

The fields logged are: action name, start time, duration, id

> python3 logparser.py ckpool.log -s -o actions.csv > summary.csv

With the -s flag will display a summary of the high level operations

The fields logged are: action name, start time, duration, jobid, clients, notification duration

Output example
--------------

An example of the output file is the following

getblocktemplate, 2016-04-21 16:06:13.505723, 3.71, 1461265573_288
mining.notify, 2016-04-21 16:06:13.909000, 0.0, 1461265573_288:139910978322384
mining.submit, 2016-04-21 16:06:36.478000, 0.0, 1461265573_287:7f866c8d
getblocktemplate, 2016-04-21 16:06:33.800235, 3.664, 1461265596_289
submitblock, 2016-04-21 16:06:36.480304, 16.67, 1461265573_287:7f866c8d
mining.notify, 2016-04-21 16:06:36.496000, 1.0, 1461265596_289:139910978322384
getblocktemplate, 2016-04-21 16:06:38.825879, 4.112, 1461265598_290
mining.notify, 2016-04-21 16:06:38.834000, 6.0, 1461265598_290:139910978322384
getblocktemplate, 2016-04-21 16:06:38.825879, 4.112, 1461265599_291


Example of summary generated
----------------------------

submitblock, 2016-04-21 16:05:23.170000, 42.063, 1461265523_275, 1, 30.42
getblocktemplate, 2016-04-21 16:05:23.009555, 3.67, 1461265523_276, 1, 212.78
getblocktemplate, 2016-04-21 16:05:28.055781, 3.731, 1461265528_277, 1, 4.49
getblocktemplate, 2016-04-21 16:05:28.055781, 3.731, 1461265528_278, 1, 402.49
submitblock, 2016-04-21 16:05:46.359000, 2.386, 1461265528_277, 1, 11.937
getblocktemplate, 2016-04-21 16:05:43.265002, 3.673, 1461265546_279, 1, 3098.33
submitblock, 2016-04-21 16:05:47.224000, 3.21, 1461265546_279, 1, 9.273
getblocktemplate, 2016-04-21 16:05:43.265002, 3.673, 1461265547_280, 1, 3963.33
getblocktemplate, 2016-04-21 16:05:48.340647, 3.565, 1461265548_281, 1, 3.79
getblocktemplate, 2016-04-21 16:05:48.340647, 3.565, 1461265548_282, 1, 391.79


Analysis
--------

For now there are two operations being logged: getblocktemplate and submitblock.

* getblocktemplate

We interpret the following line:

getblocktemplate, 2016-04-21 16:05:43.265002, 3.673, 1461265546_279, 1, 3098.33

action: getblocktemplate
start: 2016-04-21 16:05:43.265
	The time that the getblocktemplate call was made to bitcoind
duration: 3.673
	The duration in miliseconds of the getblocktemplate call
jobid: 1461265546_279
	The jobid assigned by eloipool
clients: 1
	The numbers of clients who received the mining.notify for the jobid
elapsed: 3098.33
	The time elapsed until the last notification was sent to a miner, in miliseconds

* submitblock

This line can be interpreted as

submitblock, 2016-04-21 16:05:46.359000, 2.386, 1461265528_277, 1, 11.937

action: submitblock
start: 2016-04-21 16:05:46.359
	The time the mining.submit was received by bitcoind
duration: 2.386
	The time elapsed until the block is sent to bitcoind, in miliseconds
jobid: 1461265528_277
	The jobid being submitted to bitcoind
clients: 1
	This is always 1 for submitblock
elapsed: 11.937
	The duration in miliseconds of the submitblock call to bitcoind
