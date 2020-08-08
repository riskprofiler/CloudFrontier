from azure.common.credentials import ServicePrincipalCredentials


def get_credentials(client, secret_key, tenant_id):
    credentials = ServicePrincipalCredentials(
        client_id=client,
        secret=secret_key,
        tenant=tenant_id,
    )
    return credentials
