"""
Because I like doing things on an interpreter.

Given that there's a settings.py in the same directory with the relevant info
    Usage: python -i start_conn.py
"""

from pprint import pprint, pformat
import logging, sys
import settings

import bigcommerce as api

logging.basicConfig(level=logging.DEBUG,
                    stream=sys.stdout,
                    format='%(asctime)s [%(name)s] %(levelname)s %(message)s',
                    datefmt='%m/%d %H:%M:%S')
log = logging.getLogger("start_conn")

conn = api.OAuthConnection(settings.CLIENT_ID, settings.STORE_HASH,
                           host=settings.API_PROXY, access_token=settings.ACCESS_TOKEN)

print "\nWe're good to go! \nOAuthConnection in conn."
print "Hint: pprint and pformat have been imported; you can do things like pprint(conn.get('products'))\n"