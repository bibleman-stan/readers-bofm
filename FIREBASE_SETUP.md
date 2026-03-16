# Firebase Setup for BOMReader Annotations

## 1. Create a Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Add project" → name it (e.g. "bomreader")
3. Disable Google Analytics (not needed) → Create Project

## 2. Enable Authentication

1. In the Firebase console, go to **Authentication** → **Sign-in method**
2. Enable **Google** as a sign-in provider
3. Set a support email → Save

## 3. Create Firestore Database

1. Go to **Firestore Database** → **Create database**
2. Choose **production mode** (we'll deploy custom rules)
3. Pick a region close to your users (e.g. `us-central1`)

## 4. Deploy Security Rules

Copy the contents of `firestore.rules` into the Firebase console:
1. Go to **Firestore Database** → **Rules**
2. Replace the default rules with the contents of `firestore.rules`
3. Click **Publish**

## 5. Create Firestore Indexes

The annotation queries need a composite index. Create it:
1. Go to **Firestore Database** → **Indexes**
2. Add a composite index:
   - Collection: `annotations`
   - Fields: `userId` (Ascending), `verseId` (Ascending)
3. Add another composite index:
   - Collection: `annotations`
   - Fields: `userId` (Ascending), `updatedAt` (Descending)

## 6. Add Your Web App

1. In Project Settings (gear icon), click **Add app** → **Web** (</> icon)
2. Register the app (e.g. "bomreader-web")
3. Copy the `firebaseConfig` object

## 7. Configure annotations.js

Open `annotations.js` and replace the empty `firebaseConfig` object (near the top) with your config:

```js
var firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT.appspot.com",
  messagingSenderId: "YOUR_SENDER_ID",
  appId: "YOUR_APP_ID"
};
```

## 8. Add Authorized Domain

1. In **Authentication** → **Settings** → **Authorized domains**
2. Add `bomreader.com` (and `localhost` for testing)

## 9. Test

1. Open bomreader.com locally or deploy
2. Click the ✎ button in the controls row
3. Sign in with Google
4. Tap any verse number to add a note
5. Click ✎ again to open the annotation dashboard

## Cost Notes

Firebase free tier (Spark plan) includes:
- 50K reads/day, 20K writes/day, 20K deletes/day
- 1 GiB storage
- This is more than sufficient for personal/small-group use
