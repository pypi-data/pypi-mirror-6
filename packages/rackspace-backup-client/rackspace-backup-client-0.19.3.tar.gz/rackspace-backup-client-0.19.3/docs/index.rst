.. Rackspace Cloud Backup Client documentation master file, created by
   sphinx-quickstart on Thu Dec 12 20:43:52 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Rackspace Cloud Backup Client's documentation!
=========================================================

Welcome to the Python bindings to the Rackspace Cloud Backup
API. These bindings will help you make the most of the Cloud Backup
system and integrate it into your workflows.

Contents:

.. toctree::
   :maxdepth: 2

.. code-block:: python

    from rcbu.client.client import Client
    from rcbu.client.connection import Connection
    import rcbu.client.backup_configuration as backup_config
    
    conn = Connection('username', region='dfw',
                      apikey='981263y1hq82yh8y9q38q2')
    client = Client(conn)
    myconf = backup_config.from_file('backup_config.json', conn)
    
    # Upload a new backup configuration to the Backup API
    myconf.create()
    
    backup = client.create_backup(myconf)
    status = backup.start()
    
    # block here until the backup completes
    # polls API once a minute by default
    backup.wait_for_completion(poll_interval=.5)
    
    # easy reporting and checking for success
    report = backup.report
    report.raise_if_not_ok()


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
