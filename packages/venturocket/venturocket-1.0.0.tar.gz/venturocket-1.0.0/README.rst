venturocket-api-python
======================
The official python client library for `Venturocket's API <https://venturocket.com/api/v1>`_.

Dependencies
============
This client library uses `requests <https://github.com/kennethreitz/requests>`_ for its HTTP needs.  If venturocket is installed via ``pip``, requests should be installed automatically.

Usage
=====
Installation
------------
.. code-block:: bash

    $ pip install venturocket

Making API Calls
----------------
Initialize the client
^^^^^^^^^^^^^^^^^^^^^
.. code-block:: python

    from venturocket import Venturocket, Listing
    venturocket = Venturocket("your-api-key", "your-api-secret")

Keyword calls
^^^^^^^^^^^^^
.. code-block:: python

    # retrieve validity and synonym data for a specific keyword
    keyword = venturocket.keyword.get_keyword("php")

    # retrieve keyword suggestions based on one or more provided keywords
    suggestions = venturocket.keyword.get_suggestions("php", "python", "java")

    # parse valid keywords from raw text
    text = "We are looking for rock star web developer with expertise in Javascript and PHP."
    keywords = venturocket.keyword.parse_keywords(text)

Listing calls
^^^^^^^^^^^^^
.. code-block:: python

    # create a listing
    listing = Listing("a_user_id", "provider", "Your headline here!")
    listing.add_keyword("php", 400, 102)
    listing.add_location("94105")
    listing.add_listing_type("full-time")

    listing_id = venturocket.listing.create_listing(listing)

    # retrieve a listing
    retrieved_listing = venturocket.listing.get_listing(listing_id)

    # update a listing
    retrieved_listing['userType'] = "seeker"
    venturocket.listing.update_listing(listing_id, retrieved_listing)

    # disable a listing
    venturocket.listing.disable_listing(listing_id)

    # enable a listing
    venturocket.litsing.enable_listing(listing_id)

    # retrieve matches for a listing
    matches = venturocket.listing.get_matches(listing_id)