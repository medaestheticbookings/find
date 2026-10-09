# -*- coding: utf-8 -*-
"""Copy the clinic-owners landing page into /pro/ on this site.

The landing page is still authored in aesthetics-pipeline/deploy/ — that stays
the one place to edit it. This copies the built files in and rewrites the
absolute URLs, because the page used to sit at the root of the domain and now
sits one folder down.

    python tools/sync_pro.py [path-to-aesthetics-pipeline/deploy]
"""
import io, os, shutil, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\marco\aesthetics-pipeline\deploy'
DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'pro')

ROOT = 'https://medaestheticbookings.com/'
NEW = 'https://medaestheticbookings.com/pro/'

if not os.path.isdir(SRC):
    sys.exit('source not found: ' + SRC)

if os.path.isdir(DST):
    shutil.rmtree(DST)
os.makedirs(DST)

copied, rewritten = [], 0
for name in sorted(os.listdir(SRC)):
    s = os.path.join(SRC, name)
    # CNAME belongs to whichever repo owns the domain; this one is not it.
    # deploy/ is its own git repo, so its metadata must not come along.
    if name in ('CNAME', '.git', '.gitignore'):
        continue
    d = os.path.join(DST, name)
    if os.path.isdir(s):
        shutil.copytree(s, d)
        copied.append(name + '/')
        continue
    if name.endswith(('.html', '.xml', '.txt')):
        t = io.open(s, encoding='utf-8').read()
        before = t
        # the root URL now belongs to the patient finder
        t = t.replace(ROOT + 'sales.html', NEW + 'sales.html')
        t = t.replace(ROOT + 'privacy.html', NEW + 'privacy.html')
        t = t.replace(ROOT + 'share-card.png', NEW + 'share-card.png')
        t = t.replace('"' + ROOT + '"', '"' + NEW + '"')
        t = t.replace("'" + ROOT + "'", "'" + NEW + "'")
        t = t.replace('content="' + ROOT + '"', 'content="' + NEW + '"')
        if t != before:
            rewritten += 1
        io.open(d, 'w', encoding='utf-8', newline='').write(t)
    else:
        shutil.copy2(s, d)
    copied.append(name)

print('copied %d items into pro/ (%d had URLs rewritten)' % (len(copied), rewritten))
for c in copied:
    print('  ', c)
