# Translation Manager - Setup Instructions

A new "Translations" page has been added to wergonic-admin. It lets you upload `en.json`, auto-translate missing keys to German/Spanish/Swedish/Dutch, and download the translated files.

Code is already pushed to `main` on both repos. CI/CD will build new Docker images automatically.

---

## Step 1: Wait for CI/CD to finish

Check that both GitHub Actions completed successfully:
- https://github.com/wergonic/wergonic-django-backend/actions
- https://github.com/wergonic/wergonic-web-apps/actions

Both should show green checkmarks on the latest `main` push. If tests fail, let me know.

---

## Step 2: Deploy the new Docker images

Once CI/CD passes, the new Docker images are in the DigitalOcean Container Registry:
- `registry.digitalocean.com/wergonic/django-app-prod:latest`
- `registry.digitalocean.com/wergonic/wergonic-admin-production:latest`

**If using DigitalOcean App Platform:** It may auto-deploy. Check if the latest deployment shows the new image.

**If deploying manually on a droplet:** SSH into the server and pull the new images:

```bash
# Log into DO registry
doctl registry login

# Pull new images
docker pull registry.digitalocean.com/wergonic/django-app-prod:latest
docker pull registry.digitalocean.com/wergonic/wergonic-admin-production:latest

# Restart containers (adjust paths/names to match your setup)
docker compose down
docker compose up -d
```

---

## Step 3: Run database migration

The new feature needs a database table. SSH into wherever Django runs and execute:

```bash
# Option A: If you can exec into the running Django container
docker exec -it django-container python manage.py migrate

# Option B: If container name is different, find it first
docker ps | grep django
docker exec -it <container-name-or-id> python manage.py migrate
```

You should see output like:
```
Running migrations:
  Applying translations.0001_initial... OK
```

---

## Step 4: Seed existing translations (one-time only)

The database needs to be populated with all current translations. You need to get the translation JSON files into the Django container.

### 4a. Copy the translation files to the server

From your local machine (where you have all 3 repos), run:

```bash
# Create a temp folder with all translation files organized by namespace
mkdir -p /tmp/translations/web-ui
mkdir -p /tmp/translations/client-panel
mkdir -p /tmp/translations/flutter

# Copy web-ui translations
cp wergonic-web-apps/packages/ui/src/assets/locals/*.json /tmp/translations/web-ui/

# Copy client-panel translations
cp wergonic-web-apps/apps/client-panel/src/assets/locals/*.json /tmp/translations/client-panel/

# Copy flutter translations
cp wergonic-flutter/assets/translations/*.json /tmp/translations/flutter/

# Upload to server
scp -r /tmp/translations/ user@your-server-ip:/tmp/translations/
```

Replace `user@your-server-ip` with your actual SSH credentials.

### 4b. Run the seed commands inside the Django container

```bash
# SSH into the server
ssh user@your-server-ip

# Copy files into the Django container
docker cp /tmp/translations/ django-container:/tmp/translations/

# Run seed commands
docker exec -it django-container python manage.py seed_translations \
  --dir /tmp/translations/web-ui \
  --namespace web-ui \
  --nl-filename nl-NL.json

docker exec -it django-container python manage.py seed_translations \
  --dir /tmp/translations/client-panel \
  --namespace client-panel \
  --nl-filename nl-NL.json

docker exec -it django-container python manage.py seed_translations \
  --dir /tmp/translations/flutter \
  --namespace flutter \
  --nl-filename nl.json

# Clean up
docker exec django-container rm -rf /tmp/translations/
rm -rf /tmp/translations/
```

Each command should output something like:
```
Loaded /tmp/translations/web-ui/en.json: 142 keys
Loaded /tmp/translations/web-ui/de.json: 140 keys
Loaded /tmp/translations/web-ui/es.json: 138 keys
Loaded /tmp/translations/web-ui/sv.json: 136 keys
Loaded /tmp/translations/web-ui/nl-NL.json: 135 keys
[web-ui] Done: 142 created, 0 updated
```

---

## Step 5: Verify it works

1. Go to wergonic-admin in your browser
2. You should see "Translations" in the sidebar
3. Click it
4. Select a namespace (e.g. "Web UI (shared)")
5. You should see translation stats with progress bars
6. Try uploading an en.json file and clicking "Translate Missing Keys"

---

## How it works (for future reference)

- Dev adds new English strings in en.json as usual
- Dev goes to wergonic-admin > Translations
- Uploads the updated en.json
- Clicks "Translate Missing" — auto-translates new keys using Google Translate (free)
- Downloads the translated files (de.json, es.json, sv.json, nl.json)
- Puts them in the correct repo folder and commits

---

## Troubleshooting

**"Translations" not showing in sidebar:**
The frontend wasn't redeployed. Check that the wergonic-admin Docker image was updated.

**Stats show 0 keys:**
The seed command wasn't run. Go back to Step 4.

**Translation API errors:**
The `deep-translator` package might not be installed. Check with:
```bash
docker exec -it django-container pip list | grep deep-translator
```
If missing, install it:
```bash
docker exec -it django-container pip install deep-translator==1.11.4
```
Note: This is temporary — it should be in the Docker image. If it's missing, the image wasn't rebuilt from the latest code.

**Migration errors:**
```bash
docker exec -it django-container python manage.py showmigrations translations
```
Should show `[X] 0001_initial`. If not, run migrate again.

**Container name is different:**
Find it with `docker ps` and look for the Django container. Replace `django-container` with the actual name/ID in all commands above.
