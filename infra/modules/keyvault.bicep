// Key Vault with RBAC authorization (no access policies).
param location string
param resourceToken string
param tags object
param principalId string = ''

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'kv-maive-${resourceToken}'
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enablePurgeProtection: true
    publicNetworkAccess: 'Enabled'
  }
}

// Grant Key Vault Administrator to the deployer principal (if provided).
var kvAdminRoleId = '00482a5a-887f-4fb3-b363-3b7fe8e74483'
resource kvAdminAssign 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(principalId)) {
  name: guid(kv.id, principalId, kvAdminRoleId)
  scope: kv
  properties: {
    principalId: principalId
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', kvAdminRoleId)
    principalType: 'User'
  }
}

output name string = kv.name
output id string = kv.id
output uri string = kv.properties.vaultUri
