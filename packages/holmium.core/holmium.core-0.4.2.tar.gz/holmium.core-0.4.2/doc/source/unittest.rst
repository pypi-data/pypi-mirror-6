*********************
Unit Test Integration
*********************
.. automodule:: holmium.core 

Holmium provides two utilities to ease integration with automated tests. 


.. _testing-unittest:

The :class:`TestCase` base class.
=================================
This base class extends :class:`unittest.TestCase` and adds the following functionality:
    
    * automatically provision a selenium webdriver :attr:`driver` to the testcase which is selected based on the environment variable HO_BROWSER. 
    * A remote selenium server can also be used by setting the value of HO_REMOTE to the fully qualified url to the selenium server (e.g. http://localhost:4444/wd/hub)
    * clears the browser cookies between each test case 
    * quits the driver at the end of the test class.

The following environment variables are respected by :class:`TestCase` when :meth:`unittest.TestCase.setUpClass` is executed.

===========================  ===========================================================================================================================================
variable                     description
===========================  ===========================================================================================================================================
``HO_BROWSER``               one of chrome,firefox,opera,ie,phantomjs,android,iphone or ipad
``HO_REMOTE``                the full qualified url of the selenium server. If not provided the browsers will be attempted to be launched using the built in webdrivers.
``HO_USERAGENT``             useragent to use as an override. only works with firefox & chrome 
``HO_IGNORE_SSL_ERRORS``     ignore ssl errors when accessing pages served under untrusted certificates.
===========================  ===========================================================================================================================================

.. note::

   These environment variables may also be used when using the :ref:`testing-nose`.
   The options passed to nose however will take precedence.


Example test case
-----------------

.. code-block:: python

    import unittest
    import holmium.core

    class SimpleTest(holmium.core.TestCase):
        def setUp(self):
            self.driver.get("http://www.google.com")

        def test_title(self):
            self.assertEquals(self.driver.title, "Google")

    if __name__ == "__main__":
        unittest.main()

Execution
---------

.. code-block:: bash 
    
    # against the builtin firefox driver 
    export HO_BROWSER=firefox;python test_simple.py 
    # against a firefox instance under a remote selenium server 
    export HO_BROWSER=firefox;export HO_REMOTE=http://localhost:5555/wd/hub;python test_simple.py 

.. _testing-nose:

Plugin for nosetest
===================

This plugin registers the following command line options to nose:

===============================     ===========================================================================================================================================
option                              description
===============================     ===========================================================================================================================================
``--with-holmium``                  to enable the use of the holmium plugin
``--holmium-browser``               one of chrome,firefox,opera,ie,phantomjs,android,iphone or ipad
``--holmium-remote``                the full qualified url of the selenium server. If not provided the browsers will be attempted to be launched using the built in webdrivers.
``--holmium-useragent``             useragent to use as an override. only works with firefox & chrome 
``--holmium-capabilities``          a json dictionary of extra desired capabilities to pass to the webdriver. 
``--holmium-ignore-ssl-errors``     ignore ssl errors when accessing pages served under untrusted certificates. 
===============================     ===========================================================================================================================================

Example test case
-----------------

.. code-block:: python 

    import unittest 

    class SimpleTest(unittest.TestCase):
        def setUp(self):
            self.driver.get("http://www.google.com")

        def test_title(self):
            self.assertEquals(self.driver.title, "Google")


Execution
---------

.. code-block:: bash 

    # against the builtin firefox driver 
    nosetest test_simple.py --with-holmium --holmium-browser=firefox 
    # against a firefox instance under a remote selenium server 
    nosetest test_simple.py --with-holmium --holmium-browser=firefox --holmium-remote=http://localhost:5555/wd/hub 



