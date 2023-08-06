rfw - remote firewall
=====================

Remote firewall as a web service.
 
``rfw`` is the RESTful server which applies iptables rules to block or allow IP addresses on request from a remote client. ``rfw`` maintains the list of blocked IP addresses which may be updated in real time from many sources. ``rfw`` also solves the problem of concurrent modifications to iptables since the requests are serialized.

Typical use cases
-----------------
