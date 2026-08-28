# Huella en el Río

Parte de **Huellas** — el mismo motor de documentación también existe para
senderos de montaña en `../montana/`. El enlace "← Huellas" en la esquina del
sitio regresa al landing con ambos programas (`../index.html`).

A self-hosted website that plots your geotagged trash-report photos on a real
map, alongside a marked trail with named landmarks — like a Wikiloc route
page. No app, no login — just a link anyone can open.

## 0. Mark the trail (do this once)

**Option A — import a real GPS track (recommended).** Someone has likely
already walked and recorded this exact river. Search Wikiloc for your
river and download the GPX:

1. Go to [wikiloc.com](https://www.wikiloc.com) and search for your trail
   (for Río Ramos in Allende, try "Río Ramos Charco de las Víboras" — a
   couple of matching routes are linked below).
2. Open a route that covers the stretch you want. Look for the download
   button (usually near the map) and save the **GPX** file. You may need a
   free Wikiloc account to download.
3. Save the .gpx file into this folder.
4. Run:
   ```
   python3 gpx_to_trail.py your-file.gpx
   ```
5. This writes `trail.js` for you — the real trail line, and any named
   landmarks the route already had (like "Charco de las Víboras"), done.

Two Río Ramos routes worth checking:
- [Recorrido río Ramos](https://www.wikiloc.com/hiking-trails/recorrido-rio-ramos-68166549) — La Peñita, Paso Canavati, Charco de las Víboras, up to Media Luna
- [Río Ramos, Charco de las víboras-Media Luna-Cozumelito](https://es.wikiloc.com/rutas-senderismo/rio-ramos-charco-de-las-viboras-media-luna-cozumelito-76935638)

If the GPX you find doesn't have named landmarks, or you want to add more,
open `trail-builder.html` afterward — it will show your imported line and
let you click landmark labels onto it.

**Option B — mark it by hand.** No GPX available, or you'd rather do it
yourself? Open `trail-builder.html` by double-clicking it — it opens in
your browser, no install needed, centered on Allende already.

1. Click "Satellite" in the panel to see the river clearly.
2. Zoom and pan to the stretch you want.
3. Click along the river, in order, naming each landmark as you go.
4. Click **Download trail.js** when done, and move it into this folder,
   replacing the old one.

Either way, open `index.html` afterward — you'll see the trail drawn with
its length shown at the top, and clickable landmark pins.

You only need to do this once, unless you want to add more landmarks
later — reopen `trail-builder.html` any time.

## 1. Take the photos

Use your phone's regular camera app, with **Location Services turned on**
for the Camera app specifically (Settings → Privacy → Location Services →
Camera → While Using). That's it — no separate GPS logger needed. Every
photo you take will carry its coordinates automatically.

Tips for the walk:
- One photo per distinct trash spot (not five of the same pile).
- Wide enough shot that the surroundings are recognizable — this doubles as
  proof of *where*, not just *what*.
- If you want a caption, create a plain text file with the exact same name
  as the photo. Example: `images/IMG_0231.jpg` → `images/IMG_0231.txt`
  containing `Broken glass near the rope swing`. This is optional — you can
  also just add captions later by opening `pins.js` in any text editor.

### Marking a spot as cleaned up

If someone cleans up a spot and photographs the result, it shows on the
map in green instead of amber, with a "✓ Cleaned up" badge. To mark one:
make the caption file's **first line** exactly `CLEANED`, then write the
caption underneath it. Example, `images/IMG_0250.txt`:
```
CLEANED
Removed by a group of 3 volunteers on Saturday
```
The word `CLEANED` itself won't show up in the caption — just everything
after it.

When a spot has both a "reported" photo and a nearby "cleaned" photo,
`generate_pins.py` automatically pairs them as real before/after evidence —
open `lo-que-no-ves.html` to see them as drag-to-compare sliders. No extra
steps needed; it just fills in as you document and clean up spots.

### If someone else is sending you photos

Works exactly the same — the script doesn't care who took a photo, only
that it has GPS data. Just make sure they send you the **actual file**,
not a compressed chat version:

- ✅ Email attachment, AirDrop, or a shared Drive/Dropbox file — all keep
  the GPS data intact
- ✅ WhatsApp, but sent as a **Document**, not as a "Photo"
- ❌ WhatsApp or similar apps sending it as a regular photo often strip
  the GPS data out during compression
- ❌ A screenshot of a photo has no GPS data at all — it's a new image

If a photo comes in with no GPS data, the script will skip it and tell you
which one, so you'll know right away if you need to ask for a resend.

## 2. Add the photos to the project

Copy your photos into the `images/` folder here.

## 3. Generate the map data

```
pip install Pillow --break-system-packages
python3 generate_pins.py
```

This reads the GPS data straight out of each photo and writes `pins.js`.
Run it again any time you add new photos — it rewrites the whole file, so
if you hand-edited a caption directly in `pins.js` instead of using a
`.txt` file, re-running will overwrite that edit.

If a photo gets skipped, it means Location Services was off when it was
taken — the script will tell you which ones.

### Documenting more than one place

By default all your photos go straight into `images/` and count as one
location. If your program covers several rivers or trails — for example
"Huella en el Río" documenting both Río Ramos and Río Santa Catarina — create
one subfolder per place instead:

```
images/
  rio-ramos/
    location.json   (optional)
    IMG_001.jpg
  rio-santa-catarina/
    IMG_010.jpg
```

Each subfolder becomes its own location automatically, and a location
switcher appears above the map once you have more than one. Add an optional
`location.json` inside a subfolder to control its display name and where the
map centers on it:

```json
{
  "name": "Río Ramos",
  "description": "Cuenca en Santiago y Allende, Nuevo León",
  "lat": 25.32,
  "lng": -100.08,
  "zoom": 12
}
```

Without a `location.json`, the folder name is used to guess a name (accents
and special characters won't come through, so it's worth adding one for
anything like "Río" or "Cañón"). Re-run `python3 generate_pins.py` any time
you add a new location — it picks up new subfolders automatically.

Note: the trail line and landmarks from `trail-builder.html` /
`gpx_to_trail.py` are still tied to a single trail today. If you need a
marked trail for more than one location, ask about extending those tools too.

## 4. Preview it

Just double-click `index.html` to open it in your browser. No server
needed. You should see your pins on the map — click one to see the photo.

## 5. Customize the text

Open `config.js` in any text editor. You can change:
- the site title and tagline
- the map's starting position (`mapCenter` — update this to your river's
  actual coordinates, or it'll default to a placeholder)
- the "what's happening" paragraph
- the list of asks for the government

No coding needed — just edit the text between the quotes.

## 6. Put it online (free, no download for visitors)

Since this site is part of **Huellas**, deploy the whole `huellas` folder
together (not just this `rio` folder on its own) — that's what makes the
"← Huellas" link and the `montana` branch resolve correctly as
`tusitio.com/rio/` and `tusitio.com/montana/`, with the landing page at
`tusitio.com/`.

Two easy free options:

**Netlify (simplest):**
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag the whole `huellas` folder onto the page (the one containing
   `index.html`, `rio/`, and `montana/`)
3. You get a live URL immediately — share that link with anyone

**GitHub Pages (if you already use GitHub):**
1. Create a new repository, upload the whole `huellas` folder's contents
2. Go to Settings → Pages → set source to the main branch
3. Your site will be live at `https://yourusername.github.io/repo-name`

Either way, nobody visiting the link needs to install anything.

## Notes on the pitch

A few things that tend to land well with a local government audience:
- **Lead with the count and date range** — "47 spots documented over 6
  weeks" is more persuasive than a single dramatic photo.
- **Repeat offenders matter** — if the same spot gets photographed twice
  because it wasn't cleaned, that's strong evidence for the "needs a
  scheduled crew" ask, not just "needs a one-time cleanup."
- **Cleaned-up spots make the case too** — showing spots that were fixed
  once volunteers or you stepped in demonstrates the problem is solvable
  with support, not just a complaint.
- **Keep the ask concrete and small** — bins, signage, and a scheduled
  cleanup are much easier for an office to say yes to than a vague request
  to "do something about litter."
- Consider printing a couple of the strongest photos alongside a QR code
  linking to the live site for an in-person meeting — the site does the
  rest of the work.

If you want, once you have real photos in hand, I can help you turn this
into a one-page PDF handout too, using the same data.
