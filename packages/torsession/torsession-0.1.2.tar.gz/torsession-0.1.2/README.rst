==========
Torsession
==========

:Info: Torsession is an asynchronous session backend with Mongodb for Tornado
:Author: Lime YH.Shi

.. image:: https://pypip.in/v/torsession/badge.png
        :target: https://crate.io/packages/torsession

.. image:: https://pypip.in/d/torsession/badge.png
        :target: https://crate.io/packages/torsession


Installation
============
    
.. code-block:: bash

    $ pip install git+https://github.com/mongodb/motor.git
    $ pip install torsession
    
Dependencies
============

* tornado 3+
* motor 0.1+

Example
=======

1. Create a new session after login::

    yield session.new_session()

2. Clear current session when logout::

    yield session.delete_session()

3. Get a value::

    yield session.get(key)

4. Set a value::

    yield session.set(key, value)

5. Delete a value::

    yield session.delete(key)

6. Refresh session id::

    yield session.refresh_session()

7. Get session id::

    session.session_id

8. Set session id::

    session.session_id = new_session_id
    