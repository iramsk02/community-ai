# Authentication Setup Guide

This guide explains how to configure and obtain all required authentication keys for Slack, Jira, GitHub, and Google Auth for your application.

---

## Slack Auth Keys

1. **Create a Slack App**  
   Visit [Slack API](https://api.slack.com/tutorials/tracks/getting-a-token) and create a developer account. Follow the steps to create a new Slack app.

2. **Generate Token**  
   After app creation, generate a token using the Slack UI or via OAuth scopes.

3. **Invite Bot to Channel**  
   Once the app is authorized, invite the bot to the relevant channels in the Mifos Slack workspace.

4. **Accessing Messages**  
   Once the bot is invited, it will be able to read legacy messages and respond to queries regarding the channels.

---

## Jira Auth Keys

1. **Generate a Jira API Token**  
   Follow [this guide](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account//) to generate your Jira API token.

2. **Set the Following Environment Variables**:
   ```env
   JIRA_USERNAME=your-email@example.com
   JIRA_INSTANCE_URL=https://mifosforge.jira.com
   JIRA_CLOUD=TRUE
   ```

> **Note**:
> The Jira agent is built using [atlassian-python-api](https://atlassian-python-api.readthedocs.io/jira.html). Based on current testing, it might struggle with complex issue queries due to JIRA's native limitations.

---

## GitHub Bot Auth Keys

1. **Register a GitHub App**
   Visit [Register a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app).

2. **Set Required Permissions**:

   * `Commit statuses`: Read-only

   * `Contents`: Read & Write

   * `Issues`: Read & Write

   * `Metadata`: Read-only

   * `Pull requests`: Read & Write

   > Refer to [GitHub permissions guide](https://docs.github.com/en/rest/authentication/permissions-required-for-github-apps?apiVersion=2022-11-28) for details.

3. **Install the App on Repositories**
   Use [GitHub App Installations](https://github.com/settings/installations) to give your app access to the desired repositories.

---

## Frontend & Backend URLs

Set the following URLs for local development:

```env
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
```

---

## Google Auth & NextAuth

1. **Create OAuth Client**
   Go to [Google Cloud Console](https://console.cloud.google.com/) and create a new project with an OAuth client.

2. **Generate NEXTAUTH\_SECRET**
   Run the following command to create a secure secret:

   ```bash
   openssl rand -base64 32
   ```

3. **Set Environment Variables**:

   ```env
   NEXTAUTH_SECRET=your-generated-secret
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ```

---

## Final Checklist

* [ ] Slack App token generated and bot invited to Mifos channels
* [ ] Jira token created and `JIRA_` variables set
* [ ] GitHub App registered and installed on repositories
* [ ] Google OAuth keys created and configured
* [ ] `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, and `NEXT_PUBLIC_FASTAPI_URL` set properly

---

> This setup enables secure integration with Slack, Jira, GitHub, and Google authentication across both frontend and backend services.

