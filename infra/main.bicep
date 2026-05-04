// Documented in: docs/deployment/runbook.md, docs/decisions.md (DEC-018)
// MAIVE Core Services — root Bicep template (azd entry point).
//
// Provisions:
//  - Log Analytics + Application Insights
//  - Azure Container Registry
//  - Container Apps Environment + Backend Container App
//  - App Service Plan (B1) + Frontend App Service
//  - Cosmos DB serverless (NoSQL API)
//  - Key Vault
//  - Azure AI Foundry / OpenAI account + chat & embedding deployments
//  - Managed Identity + RBAC

targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (e.g. dev, staging, prod). Used as resource suffix.')
param environmentName string

@minLength(1)
@description('Azure region for all resources.')
param location string

@description('Object ID of the principal (user or SP) that should receive Key Vault Administrator on the new vault. Defaults to deployer.')
param principalId string = ''

// Resource token used to make resource names globally unique but stable across deployments.
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = {
  'azd-env-name': environmentName
  project: 'maive-core-services'
}

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-maive-${environmentName}'
  location: location
  tags: tags
}

module monitoring 'modules/monitoring.bicep' = {
  scope: rg
  name: 'monitoring'
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
  }
}

module keyvault 'modules/keyvault.bicep' = {
  scope: rg
  name: 'keyvault'
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
    principalId: principalId
  }
}

module cosmos 'modules/cosmos.bicep' = {
  scope: rg
  name: 'cosmos'
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
  }
}

module aiFoundry 'modules/ai_foundry.bicep' = {
  scope: rg
  name: 'aifoundry'
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
  }
}

module containerApp 'modules/containerapp.bicep' = {
  scope: rg
  name: 'containerapp'
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
    cosmosEndpoint: cosmos.outputs.endpoint
    cosmosDatabase: cosmos.outputs.databaseName
    keyVaultName: keyvault.outputs.name
    aiFoundryEndpoint: aiFoundry.outputs.endpoint
    aiFoundryChatDeployment: aiFoundry.outputs.chatDeploymentName
    aiFoundryEmbeddingDeployment: aiFoundry.outputs.embeddingDeploymentName
  }
}

module appService 'modules/appservice.bicep' = {
  scope: rg
  name: 'appservice'
  params: {
    location: location
    resourceToken: resourceToken
    tags: tags
    backendUrl: containerApp.outputs.fqdn
  }
}

// azd-required outputs
output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerApp.outputs.registryLoginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerApp.outputs.registryName
output BACKEND_URI string = 'https://${containerApp.outputs.fqdn}'
output FRONTEND_URI string = 'https://${appService.outputs.defaultHostname}'
output COSMOS_ENDPOINT string = cosmos.outputs.endpoint
output COSMOS_ACCOUNT_NAME string = cosmos.outputs.accountName
output COSMOS_DATABASE string = cosmos.outputs.databaseName
output KEY_VAULT_NAME string = keyvault.outputs.name
output AI_FOUNDRY_ENDPOINT string = aiFoundry.outputs.endpoint
output AI_FOUNDRY_ACCOUNT_NAME string = aiFoundry.outputs.accountName
output AI_FOUNDRY_RESOURCE_ID string = aiFoundry.outputs.id
output BACKEND_PRINCIPAL_ID string = containerApp.outputs.backendPrincipalId
