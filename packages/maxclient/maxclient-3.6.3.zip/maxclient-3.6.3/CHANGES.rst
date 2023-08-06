CHANGELOG
==========

3.6.3 (2014-03-25)
------------------

* Updated use case HEAD returning 404 and returning as it's not implemented when in fact, it is but simply the resource does not exist. [Victor Fernandez de Alba]

3.6.2 (2014-03-24)
------------------

* Separate common features into BaseClient [Carles Bruguera]
* Default for contexts [Victor Fernandez de Alba]
* Update resources [Carles Bruguera]
* Update resources [Carles Bruguera]
* Updated resources from max [Carles Bruguera]
* Wrapper for user [Carles Bruguera]
* SYntax fix [Carles Bruguera]
* upload file base on file object, not content [Carles Bruguera]
* Add support to file uploads [Carles Bruguera]
* Add support for dict-based query strings [Carles Bruguera]
* Document variable pass syntax [Carles Bruguera]
* Move helper methods to utils.py [Carles Bruguera]
* expand key.subkey and key_subkey dict keys as nested dicts [Carles Bruguera]
* Make dict updates recursive [Carles Bruguera]
* Add defaults definition system [Carles Bruguera]
* Add debug method for raw requests [Carles Bruguera]
* Wrap non-hashes {hash} variables into hashes [Carles Bruguera]
* Typo [Carles Bruguera]
* Documentation [Carles Bruguera]
* Catch bad gateway errors [Carles Bruguera]
* Update resources definitions [Carles Bruguera]
* First version of generic rest-like maxclient [Carles Bruguera]
* Add getUser endpoint wrapper [Carles Bruguera]
* Better bad password error [Carles Bruguera]

3.6.1 (2014-02-24)
------------------

* Add both endpoints wrappers, grant and revoke [Victor Fernandez de Alba]
* Add security grant role wrapper [Victor Fernandez de Alba]

3.6 (2014-01-20)
----------------

* Added get_context, grant permission, revoke permission [Victor Fernandez de Alba]

3.5.3 (2013-10-29)
------------------

* Methods to manage context tags [Carles Bruguera]

3.5.2 (2013-10-08)
------------------

* Fix bug that returned None when max returned [] [Carles Bruguera]

3.5.1 (2013-10-03)
------------------

 * Added mod operation for context [Carles Bruguera]

3.5 (2013-09-13)
----------------

 * Update Manifest [Victor Fernandez de Alba]
 * New wraper for conversation tokens endpoint. [Victor Fernandez de Alba]
 * Added wrapper for post activity as a context endpoint [Victor Fernandez de Alba]
 * Added new method for identify current actor [Victor Fernandez de Alba]
 * Update sensible defaults for maxclient [Victor Fernandez de Alba]

3.4.1 (2013-08-02)
------------------

 * Added wrapper for upload users avatar [Victor Fernandez de Alba]

3.4 (2013-07-25)
----------------

 * Add more verbose errors [Victor Fernandez de Alba]
 * Updated minor version to match the MAX minor version [Victor Fernandez de Alba]

3.3.3 (2013-07-10)
------------------

 * Fix latter endpoint added and better handling for delete operations. [Victor Fernandez de Alba]
 * Merge branch 'master' of github.com:UPCnet/maxclient [Victor Fernandez de Alba]
 * Add new endpoint wrapper [Victor Fernandez de Alba]
 * Better propagation of the information about what happened [Victor Fernandez de Alba]

3.3.2 (2013-07-01)
------------------
* Added endpoint wrapper for returning the subscirbers for a given context
* Added endpoint wrapper for unsubscribing a user from a context

3.3.1 (2013-06-04)
------------------
* Added fallback to work with osiris oauth servers and legacy ones

3.3 (2013-06-04)
----------------
* Updated to 3.3 MAX

3.0 (2013-04-15)
----------------
* Updated to latest implementations

1.0 (Unreleased)
----------------
*  Initial version
