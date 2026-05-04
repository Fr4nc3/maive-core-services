// Container Apps Environment + Backend Container App + ACR.
// Backend uses a system-assigned managed identity for Cosmos / AI Foundry / Key Vault access.
param location string
param resourceToken string
param tags object
param logAnalyticsWorkspaceId string
param appInsightsConnectionString string

param cosmosEndpoint string
param cosmosDatabase string
param keyVaultName string
param aiFoundryEndpoint string
param aiFoundryChatDeployment string
param aiFoundryEmbeddingDeployment string

@description('Image tag to deploy. azd overrides this on each deploy.')
param backendImageTag string = 'latest'

resource registry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: 'crmaive${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' existing = {
  name: last(split(logAnalyticsWorkspaceId, '/'))
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'cae-maive-${resourceToken}'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}

var backendImage = '${registry.properties.loginServer}/maive-backend:${backendImageTag}'

// Role: AcrPull on the registry (for the Container App's identity).
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'

resource backend 'Microsoft.App/containerApps@2024-03-01' = {
  name: 'ca-maive-backend-${resourceToken}'
  location: location
  tags: union(tags, {
    'azd-service-name': 'backend'
  })
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
        allowInsecure: false
      }
      registries: [
        {
          server: registry.properties.loginServer
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: backendImage
          resources: {
            cpu: json('0.5')
            memory: '1.0Gi'
          }
          env: [
            { name: 'APP_ENV', value: 'production' }
            { name: 'LLM_PROVIDER', value: 'azure' }
            { name: 'COSMOS_ENDPOINT', value: cosmosEndpoint }
            { name: 'COSMOS_DATABASE', value: cosmosDatabase }
            { name: 'AZURE_OPENAI_ENDPOINT', value: aiFoundryEndpoint }
            { name: 'AZURE_OPENAI_CHAT_DEPLOYMENT', value: aiFoundryChatDeployment }
            { name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT', value: aiFoundryEmbeddingDeployment }
            { name: 'AZURE_OPENAI_API_VERSION', value: '2024-12-01-preview' }
            { name: 'KEY_VAULT_NAME', value: keyVaultName }
            { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/api/health'
                port: 8000
              }
              initialDelaySeconds: 20
              periodSeconds: 30
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

resource acrPullAssign 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, backend.id, acrPullRoleId)
  scope: registry
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalType: 'ServicePrincipal'
  }
}

// Cosmos DB Built-in Data Contributor (data plane).
var cosmosDataContributorRoleId = '00000000-0000-0000-0000-000000000002'
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2024-08-15' existing = {
  name: 'cosmos-maive-${resourceToken}'
}
resource cosmosRoleAssign 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-08-15' = {
  parent: cosmosAccount
  name: guid(cosmosAccount.id, backend.id, cosmosDataContributorRoleId)
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: '${cosmosAccount.id}/sqlRoleDefinitions/${cosmosDataContributorRoleId}'
    scope: cosmosAccount.id
  }
}

// Key Vault Secrets User on the vault.
var kvSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
resource kv 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}
resource kvAssign 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(kv.id, backend.id, kvSecretsUserRoleId)
  scope: kv
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', kvSecretsUserRoleId)
    principalType: 'ServicePrincipal'
  }
}

// Cognitive Services OpenAI User on the AI Foundry account.
var aifUserRoleId = '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
resource aifAccount 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: 'aif-maive-${resourceToken}'
}
resource aifAssign 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aifAccount.id, backend.id, aifUserRoleId)
  scope: aifAccount
  properties: {
    principalId: backend.identity.principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', aifUserRoleId)
    principalType: 'ServicePrincipal'
  }
}

output fqdn string = backend.properties.configuration.ingress.fqdn
output registryLoginServer string = registry.properties.loginServer
output registryName string = registry.name
output backendName string = backend.name
output backendPrincipalId string = backend.identity.principalId
output backendIdentityPrincipalId string = backend.identity.principalId
