# evercam.py [![Build Status](https://travis-ci.org/evercam/evercam.py.png)](https://travis-ci.org/evercam/evercam.py)
**A Python wrapper around the Evercam API.**

## Installation

### Pip

```
pip install evercam
```

### From Souce

Extract the source distribution and run:

```
python setup.py install
```

## Basic usage


```
import evercam
vendors = evercam.Vendor.all()
print vendors
```

It will return list containing Vendor objects in a format described on http://www.evercam.io/docs/api/v1/vendors

```
$ [{u'known_macs': [u'8C:11:CB'], u'id': u'abus', u'name': u'ABUS Security-Center'}, {u'known_macs': ...
```