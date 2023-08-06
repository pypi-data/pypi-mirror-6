Agha: Another GitHub API
========================

Yes, Agha is another GitHub API library for Python 2.x development.

Support basic CRUD operations throw the
official REST API v3: http://developer.github.com/v3/

Example:

.. code:: python

    from agha import GitHubApi
    api = GitHubApi("myuser", "mypass")

    # Create a repository
    api.create_repo({'name': 'mytestrepo1', 'description': 'Github Test 1', 'auto_init': True}

    # Edit the repo description
    api.edit_myrepo("mytestrepo1", {'description': 'Another description for my repo'})

    # List my repositories
    for repo in api.get_myrepos():
        print "NAME: %(name)s, DESCRIPTION: %(description)s, URL: %(html_url)s" % repo

    # Delete the repo
    api.delete_myrepo("mytestrepo1")

   # Show my profile information
   print "USER: %(login)s, NAME: %(name)s, EMAIL: %(email)s" % api.get_myprofile()


Requirements
------------

* Python 2.6+
* Requests library


About
-----

This source code is available in https://github.com/mrsarm/python-agha

Developed by Mariano Ruiz <mrsarm@gmail.com>

License: LGPL-3 (C) 2014
