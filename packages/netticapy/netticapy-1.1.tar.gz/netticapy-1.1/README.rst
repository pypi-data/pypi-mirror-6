NetticaPy
=========
NetticaPy is a python wrapper around Nettica_'s `SOAP DNS API`_.
It supports CRUD operations on domain records, reading the nettica
service information (your account settings) and listing zones (
your mapped domains).

I wanted to gain scriptable DNS control over existing zones only.
Feel free to add further zone support (create, update, delete and create
a secondary zone) and/or template support. Those are available as SOAP
endpoints as well.

.. _Nettica: http://www.nettica.com/
.. _SOAP DNS API: https://www.nettica.com/DNS/DnsApi.asmx

*****
Usage
*****

Create a CNAME record
---------------------
**Create a CNAME record fabian.schneevonmorgen.com that forwards to
www.topfstedt.com**
::

    from netticapy.api import DomainRecord
    from netticapy.api import DnsApi

    api = DnsApi(username='fabian', password='topsecret')
    api.create_record(DomainRecord(
        record_type="CNAME",
        host_name="fabian",
        domain_name="schneevonmorgen.com",
        priority=0,
        ttl=1,
        data="www.topfstedt.com",
    ))


Read a domain record
--------------------
**Read the domain record fabian.schneevonmorgen.com**
::

    from netticapy.api import DnsApi

    api = DnsApi(username='fabian', password='topsecret')
    api.read_record(domain_name="schneevonmorgen.com", host_name="fabian")

The read record method returns a named tuple:
::

    DomainRecord(record_type=CNAME, domain_name=schneevonmorgen.com,
    host_name=fabian, priority=0, ttl=1, data=www.topfstedt.com)


List all domain records
-----------------------
**List all domain records of schneevonmorgen.com**
::

    from netticapy.api import DnsApi

    api = DnsApi(username='fabian', password='topsecret')
    for domain_record in api.list_domain(domain_name='schneevonmorgen.com'):
        pass  # do sth. with DomainRecord (named tuple) objects


Update a domain record
----------------------
**Update the domain record fabian.schneevonmorgen.com to be a A-record
pointing to 1.2.3.4**
::

    from netticapy.api import DomainRecord
    from netticapy.api import DnsApi

    api = DnsApi(username='fabian', password='topsecret')
    api.update_record(DomainRecord(
        record_type="A",
        host_name="fabian",
        domain_name="schneevonmorgen.com",
        priority=0,
        ttl=1,
        data="1.2.3.4",
    ))


Delete a domain record
----------------------
**Delete the domain record fabian.schneevonmorgen.com**
::

    from netticapy.api import DnsApi

    api = DnsApi(username='fabian', password='topsecret')
    api.delete_record(domain_name='schneevonmorgen.com', host_name='fabian')


List all zones (domains):
-------------------------
**List all zone entries that are managed on nettica**
::

    from netticapy.api import DnsApi

    api = DnsApi(username='fabian', password='topsecret')
    api.list_zones()

The list_zones method returns a list of strings:
::

    ['schneevonmorgen.com', 'topfstedt.com']


Get service info
----------------
**Read the service info of my account**
::

    from netticapy.api import DnsApi

    api = DnsApi(username='fabian', password='topsecret')
    api.get_service_info()

The get_service_info method returns a named tuple:
::

    ServiceResult(remaining_credits=48, total_credits=50,
    service_renewal_date=datetime.datetime(2014, 11, 30, 13, 5, 0, 000))
