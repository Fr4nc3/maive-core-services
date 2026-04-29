// App Service Plan (B1) + App Service for the React frontend (Linux container).
// Acts as a thin proxy/static host; nginx inside the container reverse-proxies /api/*.
param location string
param resourceToken string
param tags object
param backendUrl string

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'plan-maive-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource site 'Microsoft.Web/sites@2023-12-01' = {
  name: 'app-maive-${resourceToken}'
  location: location
  tags: union(tags, {
    'azd-service-name': 'frontend'
  })
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      alwaysOn: true
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      linuxFxVersion: 'DOCKER|nginx:alpine'
      appSettings: [
        { name: 'WEBSITES_PORT', value: '80' }
        { name: 'BACKEND_URL', value: 'https://${backendUrl}' }
        { name: 'DOCKER_REGISTRY_SERVER_URL', value: 'https://mcr.microsoft.com' }
      ]
    }
  }
}

output defaultHostname string = site.properties.defaultHostName
output siteName string = site.name
