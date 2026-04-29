// Cosmos DB (NoSQL API), serverless. Database name: `maive`.
// Containers are created on first use by the backend; this template only
// provisions the account + database to keep deploys idempotent.
param location string
param resourceToken string
param tags object

var databaseName = 'maive'

resource account 'Microsoft.DocumentDB/databaseAccounts@2024-08-15' = {
  name: 'cosmos-maive-${resourceToken}'
  location: location
  tags: tags
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
    capabilities: [
      { name: 'EnableServerless' }
      { name: 'EnableNoSQLVectorSearch' }
    ]
    disableLocalAuth: false
    publicNetworkAccess: 'Enabled'
  }
}

resource db 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-08-15' = {
  parent: account
  name: databaseName
  properties: {
    resource: {
      id: databaseName
    }
  }
}

// bot_audit container is provisioned explicitly because the partition
// key (/session_id) is part of the RAI audit contract (DEC-013/019).
// All other containers are created on first use by the backend.
resource botAuditContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-08-15' = {
  parent: db
  name: 'bot_audit'
  properties: {
    resource: {
      id: 'bot_audit'
      partitionKey: {
        paths: [ '/session_id' ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [ { path: '/*' } ]
        excludedPaths: [ { path: '/"_etag"/?' } ]
      }
    }
  }
}

output endpoint string = account.properties.documentEndpoint
output accountName string = account.name
output databaseName string = databaseName
output id string = account.id
