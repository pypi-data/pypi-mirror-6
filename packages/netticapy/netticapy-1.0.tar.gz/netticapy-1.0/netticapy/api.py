import base64
import collections
import urllib
import urllib2

from suds.client import Client


DomainRecord = collections.namedtuple(
    'DomainRecord',
    'record_type, domain_name, host_name, priority, ttl, data'
)


ServiceResult = collections.namedtuple(
    'ServiceResult',
    'remaining_credits, total_credits, service_renewal_date'
)


class DnsApi(object):
    """
    A python wrapper for Nettica's SOAP API.
    """
    endpoint = "https://www.nettica.com/DNS/DnsApi.asmx?WSDL"

    def __init__(self, username, password):
        self.username = username
        self.encoded_password = base64.b64encode(password)

    def _get_client(self):
        return Client(self.endpoint)

    def get_service_info(self):
        """
        Returns the service info as a named tuple.
        Raises a RuntimeError on error.
        """
        client = self._get_client()
        response = client.service.GetServiceInfo(self.username,
                                                 self.encoded_password)

        if response.Result.Status != 200:
            msg = "%d: %s" % (response.Result.Status,
                              response.Result.Description)
            raise RuntimeError(msg)
        else:
            return ServiceResult(
                remaining_credits=response.RemainingCredits,
                total_credits=response.TotalCredits,
                service_renewal_date=response.ServiceRenewalDate,
            )

    def list_domain(self, domain_name):
        """
        Returns all domain records for the given domain name as
        named tuples.
        Raises a RuntimeError on error.
        """
        client = self._get_client()
        response = client.service.ListDomain(self.username,
                                             self.encoded_password,
                                             domain_name)

        if response.Result.Status != 200:
            msg = "%d: %s" % (response.Status, response.Description)
            raise RuntimeError(msg)
        else:
            for domain_record in response.Record[0]:
                yield DomainRecord(
                    record_type=domain_record.RecordType,
                    domain_name=domain_record.DomainName,
                    host_name=domain_record.HostName,
                    priority=domain_record.Priority,
                    ttl=domain_record.TTL,
                    data=domain_record.Data,
                )

    def list_zones(self):
        """
        Returns the zones (domain names) as a list of strings.
        Raises a RuntimeError on error.
        """
        client = self._get_client()
        response = client.service.ListZones(self.username,
                                            self.encoded_password)

        if response.Result.Status != 200:
            msg = "%d: %s" % (response.Status, response.Description)
            raise RuntimeError(msg)
        else:
            return response.Zone[0]

    def create_record(self, domain_record):
        """
        Creates a domain record.
        Raises a RuntimeError on error.
        """
        client = self._get_client()
        response = client.service.AddRecord(
            self.username,
            self.encoded_password,
            {
                'DomainName': domain_record.domain_name,
                'HostName': domain_record.host_name,
                'RecordType': domain_record.record_type,
                'Data': domain_record.data,
                'TTL': domain_record.ttl,
                'Priority': domain_record.priority,
            },
        )

        if response.Status != 200:
            msg = "%d: %s" % (response.Status, response.Description)
            raise RuntimeError(msg)

    def read_record(self, domain_name, host_name):
        """
        Reads a domain record and returns it, if it exists.
        """
        for domain_record in self.list_domain(domain_name):
            if domain_record.host_name == host_name:
                return domain_record

    def update_record(self, updated_domain_record):
        """
        Updates a domain record.
        Raises a RuntimeError on error.
        """
        old_domain_record = self.read_record(
            domain_name=updated_domain_record.domain_name,
            host_name=updated_domain_record.host_name
        )
        if not old_domain_record:
            msg = "You need to create this domain record, it does not exist."
            raise RuntimeError(msg)

        client = self._get_client()
        response = client.service.UpdateRecord(
            self.username,
            self.encoded_password,
            {
                'DomainName': old_domain_record.domain_name,
                'HostName': old_domain_record.host_name,
                'RecordType': old_domain_record.record_type,
                'Data': old_domain_record.data,
                'TTL': old_domain_record.ttl,
                'Priority': old_domain_record.priority,
            },
            {
                'DomainName': updated_domain_record.domain_name,
                'HostName': updated_domain_record.host_name,
                'RecordType': updated_domain_record.record_type,
                'Data': updated_domain_record.data,
                'TTL': updated_domain_record.ttl,
                'Priority': updated_domain_record.priority,
            },
        )
        if response.Status != 200:
            msg = "%d: %s" % (response.Status, response.Description)
            raise RuntimeError(msg)

    def delete_record(self, domain_name, host_name):
        """
        Deletes a domain record.
        Raises a RuntimeError on error.
        """
        domain_record = self.read_record(
            domain_name=domain_name,
            host_name=host_name
        )
        if not domain_record:
            msg = "Domain record already missing. No deletion required."
            raise RuntimeError(msg)

        client = self._get_client()
        response = client.service.DeleteRecord(
            self.username,
            self.encoded_password,
            {
                'DomainName': domain_record.domain_name,
                'HostName': domain_record.host_name,
                'RecordType': domain_record.record_type,
                'Data': domain_record.data,
                'TTL': domain_record.ttl,
                'Priority': domain_record.priority,
            },
        )
        if response.Status != 200:
            msg = "%d: %s" % (response.Status, response.Description)
            raise RuntimeError(msg)


class UpdateApi(object):
    """
    A python wrapper for Nettica's Update API.
    """
    endpoint = "https://www.nettica.com/Domain/Update.aspx"

    def __init__(self, username, password):
        self.username = username
        self.encoded_password = base64.b64encode(password)

    def update_ip_address(self, domain_name, new_ip_address):
        """
        Updates thte ip address of a fully qualified domain name.
        """
        data = urllib.urlencode({
            "U": self.username,
            "P": self.encoded_password,
            "FQDN": domain_name,
            "N": new_ip_address,
        })
        url = "%s?%s" % (self.endpoint, data)

        urllib2.urlopen(url)
