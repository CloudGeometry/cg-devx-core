import dns.resolver


class DNSManager:
    """DNS Registrar wrapper to standardise DNS management."""

    __civo_ns = ["ns0.civo.com", "ns1.civo.com"]
    __digital_ocean_ns = ["ns1.digitalocean.com", "ns2.digitalocean.com", "ns3.digitalocean.com"]
    __vultr_ns = ["ns1.vultr.com", "ns2.vultr.com"]

    def evaluate_domain_ownership(self, domain_name):
        """
        Check if domain is owned by user
        :return: True or False
        """
        pass

    def evaluate_permissions(self):
        """
        Check if provided credentials have required permissions
        :return: True or False
            """
        pass

    def get_domain_ns_records(self, domain_name: str, name_servers: [str]):
        # dns.name.from_text('www.dnspython.org')
        answers = dns.resolver.resolve('dnspython.org', 'NS')
        hosts = []
        for rdata in answers:
            hosts.append(rdata["Host"])

        return set(hosts).issubset(set(name_servers))
