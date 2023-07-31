from cmd.services.cloud.aws.session_manager import SessionManager


def checkifDnsRecordExist(domain_name, dns_record):
    '''
    (str, str) --> (str)
    Read your domain-name and dns_record and check if it exists or not
    Returns recordSet and it's value in return

    #If record exist
    >>> checkifDnsRecordExist("domain_name.com", "mail.domain_name.com")
    mail.domain_name.com : 5.3.5.3

    #If record doesn't exist
    >>> checkifDnsRecordExist("domain_name.com", "mail.domain_name.com")
    0
    '''
    session = SessionManager.create_session()
    r53_client = session.client('route53')
    record_sets = r53_client.list_hosted_zones()
    for recordset in record_sets.get_records():
        if recordset.name == dns_record + ".":
            return recordset.name + " : " + recordset.to_print()
    return 0
