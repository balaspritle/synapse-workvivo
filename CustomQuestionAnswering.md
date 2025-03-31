## For Application Insights

To be executed in Cloud Shell inside azure.

>> az ad sp create-for-rbac --name "LogAnalyticsReader" --role "Log Analytics Reader" --scopes /subscriptions/3d06e7d1-0ef1-45d9-ab16-6fdd37a8ac1f/resourceGroups/zevigo-synapse-cqna/providers/Microsoft.OperationalInsights/workspaces/zevigo-synapse-cqna-log-analytics

{
  "appId": "70f438b0-f78d-438d-a5f4-f611578251bf",
  "displayName": "LogAnalyticsReader",
  "password": "z~S8Q~yvySoQBmFLF3KrdtlW1pcCnq26I_sdTa70",
  "tenant": "8d09e77a-a159-4d16-a7d4-83ffd87a4018"
}

>> az role assignment list --assignee "70f438b0-f78d-438d-a5f4-f611578251bf" --output table
>> az role assignment create \
    --assignee "70f438b0-f78d-438d-a5f4-f611578251bf" \
    --role "Log Analytics Reader" \
    --scope "/subscriptions/3d06e7d1-0ef1-45d9-ab16-6fdd37a8ac1f/resourceGroups/zevigo-synapse-cqna/providers/Microsoft.OperationalInsights/workspaces/zevigo-synapse-cqna-log-analytics"

>> az role assignment create \
    --assignee "70f438b0-f78d-438d-a5f4-f611578251bf" \
    --role "Reader" \
    --scope "/subscriptions/3d06e7d1-0ef1-45d9-ab16-6fdd37a8ac1f/resourceGroups/zevigo-synapse-cqna/providers/Microsoft.CognitiveServices/accounts/ihis-custom-question-answering"