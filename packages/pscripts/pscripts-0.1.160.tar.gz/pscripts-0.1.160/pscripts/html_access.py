#!/usr/bin/env python
import logging as log
root_logger = log.getLogger()
root_logger.setLevel(log.DEBUG)

import requests

# we may need to interact with a domain like craigslists for several
# calls.  To prevent having to login with each call, we create a
# =connection= object that we pass into each call.  If the connection
# isn't setup it tries to login


def test_local_nginx():
    url = 'https://github.com/timeline.json'
    url = 'http://127.0.0.1'
    
    r = requests.get(url)
    log.debug(r.text)

def _test():
    log.debug("test message")
if __name__ == '__main__':
    test_local_nginx()
