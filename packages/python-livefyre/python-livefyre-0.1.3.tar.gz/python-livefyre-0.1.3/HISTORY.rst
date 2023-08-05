.. :changelog:

History
-------

0.1.2 (2014-01-20)
++++++++++++++++++

* Fixes broken imports introduced in PyJWT v0.1.7 by pinning to 0.1.6.

0.1.2 (2014-01-15)
++++++++++++++++++

* Detect if '.fyre.co' in `network` and remove accordingly
* Dial down the URL validation for `ping_to_pull` to handle the non-standard format
* Add a `Livefyre.list_sites` method to list as sites and auth credentials for the network
* Fix `livefyre._create_auth_token` to properly accept a `display_name` parameter
* Remove some debug `print` calls and add some documentation

0.1.1 (2014-01-14)
++++++++++++++++++

* Fix broken installs due to poorly writtens setup.py

0.1.0 (2014-01-14)
++++++++++++++++++

* First release on Github.
* Implements the follow Livefyre APIs:
    * Ping to Pull
    * Register Profile Pull Interface
    * Create Collection
