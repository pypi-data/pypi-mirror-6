opengever.mysqlconfig
=====================


``opengever.mysqlconfig`` configures mysql as database used by ogds and
global index. The configuration bases on ``z3c.saconfig``.

Configuration
--------------

:Username: opengever
:Password: opengever
:Database: opengever
:Hostname: localhost
:Engine: mysql
:Engine name: opengever.db
:Session name: opengever

Installation
-------------

There is a script ``create_database.sql`` which creates a new the database
and grants access for the user on the database.

Just run following command on your shell::

    $ cd src/opengever.mysqlconfig/opengever/mysqlconfig
    $ mysql -uroot -p < create_database.sql

Links
=====

* Main github project repository: https://github.com/4teamwork/opengever.mysqlconfig 
* Issue tracker: https://github.com/4teamwork/opengever.mysqlconfig/issues

Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``opengever.mysqlconfig`` is licensed under GNU General Public License, version 2.
