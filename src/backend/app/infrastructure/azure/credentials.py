"""Azure credential factory for keyless service authentication.

Pillar: Stable Core
Phase: KV
Purpose: Shared Azure credential factory for Cosmos DB and Azure AI Foundry.
Documented in: docs/deployment/runbook.md
"""

from functools import lru_cache

from azure.core.credentials import TokenCredential
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

from app.config import settings

_LOCAL_ENVS = {"dev", "development", "local", "test"}


@lru_cache(maxsize=1)
def get_azure_credential() -> TokenCredential:
    """Return the Azure credential for the current runtime environment."""
    app_env = settings.app_env.strip().lower()
    azure_client_id = settings.azure_client_id
    if app_env in _LOCAL_ENVS:
        return DefaultAzureCredential(exclude_environment_credential=True)
    if azure_client_id:
        return ManagedIdentityCredential(client_id=azure_client_id)
    return ManagedIdentityCredential()
