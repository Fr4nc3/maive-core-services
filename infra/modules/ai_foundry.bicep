// Azure AI Foundry (Azure OpenAI) account + chat & embedding deployments.
param location string
param resourceToken string
param tags object

@description('Chat model name to deploy.')
param chatModelName string = 'gpt-4o-mini'
@description('Chat model version to deploy.')
param chatModelVersion string = '2024-07-18'
@description('Embedding model name.')
param embeddingModelName string = 'text-embedding-3-small'
@description('Embedding model version.')
param embeddingModelVersion string = '1'

resource account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'aif-maive-${resourceToken}'
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: 'aif-maive-${resourceToken}'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
}

resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: account
  name: 'chat'
  sku: {
    name: 'GlobalStandard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: chatModelName
      version: chatModelVersion
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: account
  name: 'embedding'
  sku: {
    name: 'Standard'
    capacity: 30
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: embeddingModelVersion
    }
  }
  dependsOn: [
    chatDeployment
  ]
}

output endpoint string = account.properties.endpoint
output accountName string = account.name
output id string = account.id
output chatDeploymentName string = chatDeployment.name
output embeddingDeploymentName string = embeddingDeployment.name
