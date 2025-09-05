# Authentication Setup Guide

This guide explains how to configure and obtain all required authentication keys for **Slack**, **Jira**, **GitHub**, and **Firebase** for your application.

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
> The Jira agent is built using [atlassian-python-api](https://atlassian-python-api.readthedocs.io/jira.html).  
> Based on current testing, it might struggle with complex issue queries due to JIRA's native limitations.

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
```

---

## Firebase Auth

1. Create Firebase Project
   1. Go to [Firebase Console](https://console.firebase.google.com/).  
   2. Click **Add Project** → give it a name (e.g., `my-mifos-app`).  

2. Add Web App
   1. In Firebase project → click **Web → {</>}**.  
   2. Register a new Web App (name it e.g. `mifos-client`).  
   3. Copy the configuration object (API key, auth domain, project ID, etc.).  
   4. Add these to `.env`:

   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-firebase-auth-domain
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-firebase-storage-bucket
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-firebase-messaging-sender-id
   NEXT_PUBLIC_FIREBASE_APP_ID=your-firebase-app-id
   NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=your-firebase-measurement-id
   ```

3. Enable Authentication Providers
   1. Go to **Firebase Console → Authentication → Sign-in method**.  
   2. Enable:
      - **Email/Password**
      - **Google**

4. Setup Firestore Database
   1. Firebase Console → **Firestore Database → Create Database**.  
   2. Choose **Production mode**.  
   3. Select a region. (e.g., `asia-south1`).

## Final Checklist

- [ ] Slack App token generated and bot invited to Mifos channels  
- [ ] Jira token created and `JIRA_` variables set  
- [ ] GitHub App registered and installed on repositories  
- [ ] Firebase Auth configured with required environment variables  
- [ ] `NEXT_PUBLIC_FASTAPI_URL` set properly  

---

> This setup enables **secure integration** with Slack, Jira, GitHub, and Firebase authentication across both frontend and backend services.
