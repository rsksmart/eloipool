# Eloipool with RSK Merged Mining Capabilities

This repository is based on [Eloipool original](https://github.com/luke-jr/eloipool) repository  and has all the neccessary changes to allow the pool to do merged mining with RSK.
Said changes can be found in the master branch, which is periodically updated with changes from CKPool original.

If you need more information about Eloipool original, please refer to its [README](https://github.com/rsksmart/eloipool/blob/master/README_original)

If you are planning to use this code, please check that is up to date with the version of Eloipool original that you are using.

## Merged Mining settings

The following settings must be configured on `config.py` to do merged mining with RSK.

```
RootstockSources = (
	{
		'name': 'primary',
		'uri': 'http://user:pass@rootstock:4444',
		'priority': 0,
		'weight': 1,
	}
)

```
`uri` is the address and port where the RskJ node is listening

`RootstockPollPeriod = 2` indicates the frequency in seconds to poll RskJ node for work.

`RootstockNotifyPolicy = 2` indicates when to trigger updates to miners. 
- 0 is only when a new bitcoin work is received 
- 1 is when an rsk work is received  
- 2 is the same as 1 but sending `clean_jobs` parameter from stratum protocol in `true` 

## Development mode

The pool has settings that allow it to override the values of difficulty sent to the miners or used to compare for a BTC or RSK solution.
Those settings should not be used in production. In order to enable them, set `DEV_MODE_ON` to `True` and the desired values for the remaining settings.


