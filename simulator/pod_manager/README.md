PodManager Mocked Up Environment

# Introduction

As we know, PodManager now has two announced API spec versions 1.2.1 and 2.1 ,
so we mocked up both of them to match valence's whole requirement.

Please note that the mocked up date just use for test and development. The
two mocked up PodManager environment are use same Flask framework with same layout
logic. Understand on can easily understand another.


# How to Deploy

### Install dependencies
```
pip install -r pod_manager/requirement.txt
```

### Test run
First run the Flask webservice
```
python pod_manager/run.py
```
Then test the api by following python codes' running result

```python
import requests

auth=(name='admin',password='Passw0rd')
requests.get('https://localhost/redfish/v1', auth=auth)

```



# How to Use
