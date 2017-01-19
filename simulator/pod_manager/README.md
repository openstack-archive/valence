PodManager Mocked Up Environment

# Introduction

As we know, PodManager now has two announced API spec versions 1.2.1 and
 2.1, so we mocked up both of them to match valence's whole requirement.

Please note that the mocked up date just use for test and development.
The two mocked up PodManager environment are use same Flask framework
with same layout logic. Understand on can easily understand another.

And our final result for this simulator would generate a PodManager
which looks like this : http://imgur.com/a/FP4c9

# How to Deploy

### Install dependencies
```
pip install -r pod_manager/requirements.txt
```

### Test run
First run the Flask webservice
```
cd valence/simulator
python pod_manager/rsd_v1_2_1/run.py
```
Then test the api by following python codes' running result

```python
import requests

auth=(name='admin',password='Passw0rd')
requests.get('https://localhost/redfish/v1', auth=auth)

```

Also , we could access the url in browser to get the api result, like:
https://localhost/redfish/v1

# How to Use
