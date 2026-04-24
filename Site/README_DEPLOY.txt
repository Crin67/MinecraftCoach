Minecraft Coach - deployment notes

1. Files for the public website
Upload the full contents of the Site/ folder into the public website root:
- index.html
- styles.css
- script.js
- site-config.js
- assets/ (new folder with design images)

2. How site-config.js works
- If the website and backend API are served from the same domain, keep:
  apiBaseUrl: ""
- If the website is static but the API runs on another domain or subdomain, set for example:
  apiBaseUrl: "https://api.minecraftcoach.pl"

3. Asset handling
- The new landing page uses local images from Site/assets/.
- If the backend serves the website through FastAPI, /assets/* is now exposed by server/app/main.py.

4. What the static website can do
- show the current desktop app download button
- show available learning modules
- allow login to a specific session by program ID and parent password

5. Important limitation
- Static files alone are not enough for session monitoring.
- Monitoring, module ZIP downloads, and app downloads require the backend API.

6. Backend files
Backend is in:
- server/app/main.py
- server/app/storage.py
- server/requirements.txt

7. Current API endpoints used by the site
- GET /downloads/catalog
- GET /downloads/app/latest
- GET /downloads/modules/{slug}.zip
- POST /auth/login
- GET /dashboard

8. Updating the desktop app on the server
- replace dist/MinecraftCoach.exe on the backend host
- update folders inside modules/ when you add or change modules

9. Netlify preview / online deploy
- The repository can now be deployed as a static site from Site/ using netlify.toml.
- Redirect rules proxy API calls to the current production domain.
- If you later move the API to another host or custom domain, update the redirect targets accordingly.
