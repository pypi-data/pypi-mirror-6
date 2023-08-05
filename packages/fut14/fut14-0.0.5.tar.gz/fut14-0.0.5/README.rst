fut14
=====

.. image:: https://travis-ci.org/oczkers/fut14.png?branch=master
        :target: https://travis-ci.org/oczkers/fut14

fut14 is a simple library for managing Fifa 14 Ultimate Team.
It is written entirely in Python.



Usage
-----

.. code-block:: pycon

    >>> import fut14
    >>> fut = fut14.Core('email', 'password', 'secret answer')

    >>> items = fut.searchAuctions('development',  # search items
    ...     level='gold', category='fitness', min_price=300,  # optional parametrs
    ...     max_price=600, min_buy=300, max_buy=400,  # optional parametrs
    ...     start=0, page_size=50)  # optional parametrs

    >>> for item in items:
    ...     trade_id = item['tradeId']
    ...     buy_now_price = item['buyNowPrice']
    ...     trade_state = item['tradeState']
    ...     bid_state = item['bidState']
    ...     starting_bid = i['startingBid']
    ...     item_id = i['id']
    ...     timestamp = i['timestamp']  # auction start
    ...     rating = i['rating']
    ...     asset_id = i['assetId']
    ...     resource_id = i['resourceId']
    ...     item_state = i['itemState']
    ...     rareflag = i['rareflag']
    ...     formation = i['formation']
    ...     injury_type = i['injuryType']
    ...     suspension = i['suspension']
    ...     contract = i['contract']
    ...     playStyle = i['playStyle']  # used only for players
    ...     discardValue = i['discardValue']
    ...     itemType = i['itemType']
    ...     owners = i['owners']
    ...     offers = i['offers']
    ...     current_bid = i['currentBid']
    ...     expires = i['expires']  # seconds left

    >>> fut.credits  # returns credits amount
    600

    >>>     fut.bid(item[0]['trade_id'], 600)  # make a bid

    >>> fut.credits  # it's updated automatically on every request
    0
    >>> fut.tradepile_size
    80
    >>> fut.watchlist_size
    30

    >>> items = fut.tradepile()  # get all items from trade pile
    >>> items = fut.unassigned()  # get all unassigned items

    >>> for item in items:
    ...     fut.sell(item['item_id'], 150,  # put item on auction
    ...              buy_now=0, duration=3600)  # optional parametrs

    >>> fut.sendToTradepile(trade_id)  # add card to tradepile
    >>> fut.tradepileDelete(trade_id)  # removes item from tradepile
    >>> fut.watchlistDelete(trade_id)  # removes item from watch list

    >>> fut.keepalive()  # send keepalive ping to avoid timeout

    to be continued ;-)
    ...


CLI examples
------------
.. code-block:: bash

    not yet
    ...


License
-------

GNU GPLv3
