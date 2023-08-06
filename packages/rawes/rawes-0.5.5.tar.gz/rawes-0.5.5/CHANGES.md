History
=========

0.5.5 (2014-1)
--------------
* Removed tests package from setup.py (thanks [alisaifee](https://github.com/alisaifee))


0.5.4 (2014-1)
----------------
* Added connection pooling from [elasticsearch-py](https://github.com/elasticsearch/elasticsearch-py) (thanks [mishu-](https://github.com/mishu-))

0.5.3 (2013-7-4)
----------------
* Added JSON decoder support (thanks [adisbladis](https://github.com/adisbladis))
* Added JSON encoder argument to rawes.Elastic constructor

0.5.2 (2013-5-17)
----------------
* Python 2.6 compatibility fix (thanks [Simon Kelly](https://github.com/snopoke)!)

0.5.1 (2013-5-15)
----------------
* Added Python 3 http & https support (no thrift support yet for python 3) (thanks [adisbladis](https://github.com/adisbladis))
* Removed python-dateutil requirement in favor of pytz (due to Python 3 not supporting python-dateutil)

0.5.0 (2013-4-25)
----------------
* rawes now throws a rawes.elastic_exception.ElasticException on http status codes of >=400 by default.  Removed rawes.Elastic "except_on_error" argument.

0.4.0 (2013-4-21)
----------------
* Simplified Elastic constructor by removing connection_type param and incorporating in to url (Thanks [nvie](https://github.com/nvie)!)
* Added optional **kwargs to Elastic constructor.  Useful for specifying things like basic authentication or specific headers

0.3.6 (2013-1-8)
----------------
* Fixed requests >1.0 incompatibilities, changed requirement back to 'requests>=0.11.1'

0.3.5 (2013-1-8)
----------------
* Timeout bug fix for HTTP and Thrift

0.3.4 (2013-1-7)
----------------
* Added 'except_on_error' boolean option to rawes.Elastic constructor.  If set to True, rawes.Elastic will throw an exception when elasticsearch returns a status code of >= 400 (i.e., when there is an error)

0.3.3 (2012-12-21)
------------------
* Restricted "requests" requirement from >=0.11.1 to '>=0.11.1, <1.0.0'

0.3.2 (2012-12-11)
----------------
* Thrift bug fix (Thanks [anathomical](https://github.com/anathomical)!)
* Relaxed "requests" requirement from ==0.14.2 to >=0.11.1

0.3.1 (2012-11-26)
----------------
* Changed python-dateutil version dependency from ==2.1 to >=1.0

0.3 (2012-11-12)
----------------
* Added automatic datetime encoding (Thanks [atkinson](https://github.com/atkinson)!)
* Added support for custom json encoderings

0.2 (2012-08-10)
----------------
* Current Release
