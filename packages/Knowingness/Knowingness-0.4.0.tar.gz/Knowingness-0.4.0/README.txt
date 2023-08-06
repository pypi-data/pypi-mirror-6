===========
Knowingness
===========

Knowingness provides insight into how a specific URL performs on a variety of social networks.  Typical usage often looks like this::

    #!/usr/bin/env python

    from knowingness.social import pinterest

    pins_count = pinterest.getPins(target_url)

Social
======

Pinterest
---------

Grabs the number of Pins for a URL.

Facebook
--------

Grabs the number of Likes, Commets, and Shares for a URL.

