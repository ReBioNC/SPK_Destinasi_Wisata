# TravelFit Jawa — native web design

Direction approved: cream–teal, Java destinations, transparent recommendation.
UI-UX Pro Max searches (30 Sep 2026): `travel recommendation editorial warm`
returned Swiss/minimal editorial guidance; narrower tourism retry returned
Aurora/Thai typography, not appropriate for this Indonesian decision tool.
No verified full tourism design-system match; do not persist those palettes.
Use approved brand palette and clearly labeled general editorial guidance.
Verified UX result: **Focusable Error Summary**, web forms, links to invalid
fields plus inline errors. Stack search `responsive form labels` had no match;
retry `label` returned accessible labels and wrapping collections. Only these
HTML principles apply; Tailwind/React/native mobile packages are not adopted.

Tokens: warm paper #F7F5ED, card #FFFFFF, ink #183B36, teal #08685C,
soft teal #E2EEE8, mustard #EDD79C; body muted #52635E, border #B5C4BC.
Heading Georgia (editorial travel field-guide), body Segoe UI/system sans,
numeric data tabular system monospace. No remote font dependency.

Signature: a Java field-guide panel combining province navigation and source
counts; six-criterion comparison bars are actual relative ideal gaps, not
decorative “accuracy”. One large italic display word; quiet functional form.

Layout: headline + destination field guide → preferences (route, interests,
priorities) → ranked result cards with estimated cost and provenance → Java map.
Form uses native controls, progressive city search, optional advanced sliders.
Never bury Tahura imputations or Marina conflicts inside a closed details block.

Quality floor: 375/768/1440px reflow, visible focus, 44px controls, reduced motion,
form error summary and inline messages, loading/live region and retryable network
failure. No toast-only errors, simulated source badge, emoji navigation, giant
inline duplicate assets, scroll parallax or runtime Tailwind compiler.

Visual critique: avoid generic decorative travel photos; the Java geography
and provenance are the subject's own visual language. Main headline is concise,
body copy plain Indonesian; methodology has structured sections instead of a
wall of text. Light theme only; dark mode is not promised.

## Task 6 verification (30 Sep 2026)

- Full Django suite: 165 tests, OK (46.884s). Includes ordinary POST/redirect,
  AJAX success/400, input preservation and visible imputation/source notes.
- agent-browser CLI unavailable; used the existing in-app browser, no package
  installation. Local dev server bound to 127.0.0.1:8000.
- Inspected actual 1440px desktop hero, form/error and result cards; 375px form
  has one column, 768px two columns; document width equals viewport at all three.
- AJAX invalid budget focuses `form-errors`, announces error, enables retry.
  Valid Serang→Banten submission displays two results and Tahura imputation.
- Hemat preset changes C1 slider to 41; ArrowRight changes to 42 and returned
  result states normalized custom weights. Budget blur displays 20.000.000.
- Keyboard Tab from budget reaches city search with visible outline. Native city
  select remains usable without the search enhancement. Browser error log empty
  after successful submission. No remote compiler/font resource dependency.
- Reduced-motion behavior is explicitly implemented in CSS and scroll handling;
  browser API does not expose media emulation, so OS motion preference was not
  changed and simulated motion settings are not claimed as a manual test.

## Task 7 map verification

Inherited SVG paths: six Java provinces only, copied from the previous map.
The old asset lacks geographic projection parameters. Display uses a documented
affine approximation anchored at Monas; this is not a GIS-certified overlay.
Source lat/lon and SPK distances are unaffected. Frame 220/287/242/97 never fits
outlier Marina. Dataset retains 443 rows, 442 dots; lists contain all 443.
Unit test ray casting places Monas inside inherited Jakarta outline; this does
not audit the other coordinates or fix misleading Kaggle province labels.

Browser: keyboard Enter on all six province links prefilled each correct region;
back navigation works. Zoom/pan/reset bounded at 1–4×; mobile375 drag changed
viewBox within Java and reset returned exactly original. No horizontal overflow.
Search Marina retained both Marina entries, ID9 explicitly outside-frame/review.
Successful browser error log empty. SVG DOM geometry methods unavailable through
the read-only browser wrapper; polygon containment tested in Python instead.
