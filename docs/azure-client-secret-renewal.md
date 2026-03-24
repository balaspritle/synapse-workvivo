# Azure Client Secret Renewal for Log Analytics

When the Azure client secret expires, the weekly analytics report (`consolidated_analytics`) fails with:

```
AADSTS7000222: The provided client secret keys for app '70f438b0-f78d-438d-a5f4-f611578251bf' are expired.
```

This blocks `query_log_analytics()` in `utility/azure_log_analytics.py` from authenticating, resulting in empty DataFrames and cascading errors in the report.

## App Registration Details

| Field | Value |
|-------|-------|
| App Name | LogAnalyticsReader |
| Application (client) ID | 70f438b0-f78d-438d-a5f4-f611578251bf |
| Tenant ID | 8d09e77a-a159-4d16-a7d4-83ffd87a4018 |
| Role | Log Analytics Reader |
| Scope | Subscription `3d06e7d1-0ef1-45d9-ab16-6fdd37a8ac1f` / Resource Group `zevigo-synapse-cqna` / Workspace `zevigo-synapse-cqna-log-analytics` |

## Steps to Generate a New Client Secret

### 1. Open App Registrations

- Go to [Azure Portal](https://portal.azure.com)
- Search for **Microsoft Entra ID** in the top search bar (formerly Azure Active Directory)
- In the left sidebar, click **App registrations**

### 2. Find the App

- Click **All applications** tab
- Find **LogAnalyticsReader** (Client ID: `70f438b0-f78d-438d-a5f4-f611578251bf`)
- Click on it

### 3. Generate New Secret

- In the left sidebar, click **Certificates & secrets**
- Go to the **Client secrets** tab
- Click **+ New client secret**
- Enter a description (e.g., `rbac-v3`)
- Choose an expiry period (recommended: 12 or 24 months)
- Click **Add**

### 4. Copy the Secret Value

> **IMPORTANT:** The secret **Value** is only shown once immediately after creation. If you navigate away without copying it, you'll need to create a new one.

- Copy the **Value** column (NOT the "Secret ID")
- The value looks like: `z~S8Q~yvySoQBmFLF3KrdtlW1pcCnq26I_sdTa70`

### 5. Update the Environment Variable

Update `CLIENT_SECRET` in the `.env` file at the project root:

```
CLIENT_SECRET=<paste-new-secret-value-here>
```

### 6. Restart the Application

If running locally:
```bash
# Stop and restart the app
python3 app.py
```

If running on AWS App Runner:
```bash
# Redeploy
./deploy.sh
```

### 7. Verify

Run the app and check that `consolidated_analytics` no longer shows authentication errors:

```bash
python3 app.py
```

You should see actual data in the `df from log analytics` output instead of an empty DataFrame.

### 8. Clean Up (Optional)

- Go back to **Certificates & secrets** in Azure Portal
- Delete the old expired secret using the trash icon

## Setting a Reminder

Set a calendar reminder ~2 weeks before the new secret's expiry date to avoid downtime.

---

## Data Retention Settings

Azure Log Analytics has a configurable data retention period. Data older than the retention period is automatically purged and **cannot be recovered**. As of March 2026, retention is set to **730 days**.

### How to Change Data Retention

1. Go to [Azure Portal](https://portal.azure.com)
2. Search for **Log Analytics workspaces** in the top search bar
3. Click **zevigo-synapse-cqna-log-analytics**
4. In the left sidebar, click **Usage and estimated costs**
5. At the top of the page, click the **Data Retention** button (in the top toolbar, not the sidebar)
6. A panel will open on the right with a slider — set the number of days (max 730)
7. Click **OK**

> **Note:** Retention beyond 31 days incurs additional cost per GB/month on the pay-as-you-go plan.

**Direct link:** [Data Retention Settings](https://portal.azure.com/#@ZevigoSolutions728.onmicrosoft.com/resource/subscriptions/3d06e7d1-0ef1-45d9-ab16-6fdd37a8ac1f/resourceGroups/zevigo-synapse-cqna/providers/Microsoft.OperationalInsights/workspaces/zevigo-synapse-cqna-log-analytics/usageAndCosts)

---

## Quick Links

| Resource | Link |
|----------|------|
| Certificates & Secrets | [LogAnalyticsReader App](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationMenuBlade/~/Credentials/appId/70f438b0-f78d-438d-a5f4-f611578251bf/isMSAApp~/false) |
| Data Retention | [Usage and estimated costs](https://portal.azure.com/#@ZevigoSolutions728.onmicrosoft.com/resource/subscriptions/3d06e7d1-0ef1-45d9-ab16-6fdd37a8ac1f/resourceGroups/zevigo-synapse-cqna/providers/Microsoft.OperationalInsights/workspaces/zevigo-synapse-cqna-log-analytics/usageAndCosts) |
| Log Analytics Workspace | [zevigo-synapse-cqna-log-analytics](https://portal.azure.com/#@ZevigoSolutions728.onmicrosoft.com/resource/subscriptions/3d06e7d1-0ef1-45d9-ab16-6fdd37a8ac1f/resourceGroups/zevigo-synapse-cqna/providers/Microsoft.OperationalInsights/workspaces/zevigo-synapse-cqna-log-analytics/overview) |