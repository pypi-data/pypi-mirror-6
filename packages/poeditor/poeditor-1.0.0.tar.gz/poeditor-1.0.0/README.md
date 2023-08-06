python-poeditor
===============


Overview
--------

API Client Interface for [POEditor API](https://poeditor.com/api_reference/).

[POEditor](https://poeditor.com/) is a quick and sleek web-based software
localization platform, designed for happy translators and project managers.

Usage
-----

    >>> from poeditor import POEditorAPI
    >>> client = POEditorAPI(api_token='my_token')
    >>> projects = client.list_projects()

Testing
-------

To run tests, you need a POEditor account. You can create a free trial account.

All requests to the API must contain the parameter api_token. You can get this
key from your POEditor account. You'll find it in
[My Account > API Access.](https://poeditor.com/account/api)

    $ export POEDITOR_TOKEN=my_token
    $ nosetests

**Note**: there is no API method to delete a project. So, you must delete test
project by hand.
