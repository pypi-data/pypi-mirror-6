DOP: Digital Ocean API Python Wrapper
=====================================

DOP is a MIT licensed Python wrapper for Digital Ocean's API.


Features
--------

Full support for all methods listed `here`_ except (they have weird behaviour):
    - reset_root_password
    - restore_droplet
    - destroy_image

Installation
------------

To install dop, simply: ::

    $ pip install dop


Example
-------
It is pretty easy to use: ::

    from dop.client import Client

    client = Client('client_id', 'api_key')
    regions = client.regions()
    for region in regions:
        print region.to_json()



Contribute
----------
Pull requests and improvements are welcome.

.. _`here`: https://www.digitalocean.com/api


.. image:: https://d2weczhvl823v0.cloudfront.net/ahmontero/dop/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

