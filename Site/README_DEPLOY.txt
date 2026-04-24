Minecraft Coach — deployment notes

1. Files for the public website
Upload these files from the Site/ folder into the public website root for https://minecraftcoach.pl :
- index.html
- styles.css
- script.js
- site-config.js

2. How site-config.js works
- If the website and backend API are served from the same domain, leave:
  apiBaseUrl: ""
- If the website is static but the API runs on another domain or subdomain, set for example:
  apiBaseUrl: "https://api.minecraftcoach.pl"

3. What the static website can do
- show the current desktop app download button
- show available learning modules
- allow login to a specific session by program ID and parent password

4. Important limitation
- The static files alone are not enough for session monitoring.
- Monitoring, module ZIP downloads, and app downloads require the backend API.

5. Backend files
Backend is in:
- server/app/main.py
- server/app/storage.py
- server/requirements.txt

6. Current API endpoints used by the site
- GET /downloads/catalog
- GET /downloads/app/latest
- GET /downloads/modules/{slug}.zip
- POST /auth/login
- GET /dashboard

7. Updating the desktop app on the server
- replace dist/MinecraftCoach.exe on the backend host
- update folders inside modules/ when you add or change modules

8. Hosting note
- If minecraftcoach.pl is only a static/shared hosting folder, the website files will open, but the Python FastAPI backend may need a separate server/VPS.
- If you place the backend elsewhere, point site-config.js to that API address.
