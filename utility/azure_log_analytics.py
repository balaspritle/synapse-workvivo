from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.identity import ClientSecretCredential
import pandas as pd
from dateutil import parser
import os

def date2str_v2(row):
    processed_date = parser.parse(str(row['timestamp']))
    return processed_date.strftime('%Y-%m-%d')

tenant_id = "8d09e77a-a159-4d16-a7d4-83ffd87a4018"
client_id = "70f438b0-f78d-438d-a5f4-f611578251bf"
client_secret = "z~S8Q~yvySoQBmFLF3KrdtlW1pcCnq26I_sdTa70"
workspace_id = "2678d7bd-7e71-4e15-9732-3c98e3c8b456"
kb_id = os.getenv("AZURE_BOT_URL").split("projectName=")[-1].split('&')[0]

query = """
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.COGNITIVESERVICES"
| where OperationName=="CustomQuestionAnswering QueryKnowledgebases"
| where Category=="Trace"
| extend answer_ = tostring(parse_json(properties_s).answer)
| extend user_id = tostring(parse_json(properties_s).userId)
| extend question_ = tostring(parse_json(properties_s).question)
| extend score_ = tostring(parse_json(properties_s).score)
| extend kbId_ = tostring(parse_json(properties_s).kbId)
| project TimeGenerated, user_id, question_, answer_, score_, kbId_
""" + f'| where kbId_=="{kb_id}"'

print("Azure Log Query", query)

def query_log_analytics(timespan):
    """
    Query Azure Log Analytics using Service Principal authentication
    
    Args:
        tenant_id (str): Azure AD tenant ID
        client_id (str): Service Principal client ID
        client_secret (str): Service Principal secret
        workspace_id (str): The Log Analytics workspace ID
        query (str): The KQL query to execute
        timespan (timedelta, optional): Time range for the query. Defaults to last 24 hours
    
    Returns:
        pd.DataFrame: Query results as a DataFrame
    """
    # Create credential object using Service Principal
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )
    
    # Create Log Analytics client
    client = LogsQueryClient(credential)
    column_names = ['timestamp', 'user_id', 'question', 'answer', 'score', 'KbId']
    
    try:
        # Execute the query
        response = client.query_workspace(
            workspace_id=workspace_id,
            query=query,
            timespan=timespan
        )
        
        # Check if the query was successful
        if response.status == LogsQueryStatus.SUCCESS:
            # Convert tables to DataFrame
            if response.tables[0].rows:
                df = pd.DataFrame(
                    response.tables[0].rows,
                    columns=column_names
                )
                df['Date'] = df.apply(date2str_v2, axis=1)
                return df
            else:
                print("Query returned no data")
                return pd.DataFrame(columns=column_names)
        else:
            print(f"Query failed with status: {response.status}")
            return pd.DataFrame(columns=column_names)
            
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        return pd.DataFrame(columns=column_names)