
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

0) Installation of dependecies will be done inside a python virtualenv

> sudo apt-get install python3-venv
> python3 -m venv pyenv
> source pyenv/bin/activate

1) Clone eloipool repo

> git clone https://github.com/rootstock/eloipool.git

2) Install dependecies

> cd eloipool

2.1) python-bitcoinrpc

> pip install -e git+https://github.com/jgarzik/python-bitcoinrpc.git#egg=python-bitcoinrpc

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

RootstockPollPeriod = 20.0

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


