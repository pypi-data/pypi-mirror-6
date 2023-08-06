
CHANGES
=======


2014-04-09 - 1.0.0
------------------

 * Refactored all the client side
 * Use of AngularJS instead of jQuery
 * Use PureCSS framework and awesome inbox template 
 * Fixed a sqlite crash with multithread
 * Fixed the multithread kill when pressing Ctrl+C


2014-04-08 - 0.5.0
------------------

 * Updated requirements versions (tornado and peewee)


2013-08-28 - 0.4.1
------------------

 * Added this CHANGE file
 * The mail Queue is now empty once, not through the ioloop
 * The sqlite database is now stored under ~/.pylocalsmtp/inbox.db
 * Fix : 404 error favicon
 * Removed unnecessary mail primary key on the mail list
