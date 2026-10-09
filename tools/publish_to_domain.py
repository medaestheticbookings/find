# -*- coding: utf-8 -*-
"""Publish the patient finder into the landing page's repo, under a sub-path.

medaestheticbookings.com belongs to the aesthetics-pipeline repo, which serves
the clinic-owners landing page. Only one repo can hold a custom domain, so the
patient site rides along inside it at /<path>/ rather than taking the domain.

    python tools/publish_to_domain.py [dest-deploy-dir] [path]

Defaults to C:\\Users\\marco\\aesthetics-pipeline\\deploy and 'vres'.
Rebuilds the blog and FAQ against the public URL first, so canonicals,
og:url and the sitemap all point at the address people will actually visit.
"""
import io, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST_ROOT = sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\marco\aesthetics-pipeline\deploy'
SUBPATH = (sys.argv[2] if len(sys.argv) > 2 else 'vres').strip('/')

PUBLIC = 'https://medaestheticbookings.com/%s/' % SUBPATH
OLD = 'https://medaestheticbookings.github.io/find/'

# files that make up the site; everything else in the repo is tooling
INCLUDE = ['index.html', 'privacy.html', 'robots.txt', 'sitemap.xml', 'img', 'blog', 'faq']
SKIP = {'CNAME', 'pro', 'tools', '.git', '.gitignore', '__pycache__'}

if not os.path.isdir(DEST_ROOT):
    sys.exit('destination not found: ' + DEST_ROOT)

# 1. rebuild the generated pages against the public address
subprocess.check_call([sys.executable, os.path.join(HERE, 'tools', 'make_blog.py'), HERE, PUBLIC])

dest = os.path.join(DEST_ROOT, SUBPATH)
if os.path.isdir(dest):
    shutil.rmtree(dest)
os.makedirs(dest)

rewritten = 0
for name in INCLUDE:
    src = os.path.join(HERE, name)
    if not os.path.exists(src) or name in SKIP:
        continue
    dst = os.path.join(dest, name)
    if os.path.isdir(src):
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    else:
        shutil.copy2(src, dst)

# 2. the hand-written page still carries the old absolute URLs
for root, _dirs, files in os.walk(dest):
    for f in files:
        if not f.endswith(('.html', '.xml', '.txt')):
            continue
        p = os.path.join(root, f)
        t = io.open(p, encoding='utf-8').read()
        if OLD in t:
            io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(OLD, PUBLIC))
            rewritten += 1

print('published to %s' % dest)
print('public address: %s' % PUBLIC)
print('%d files had their absolute URLs rewritten' % rewritten)

# 3. leave nothing pointing at the old host
stale = []
for root, _dirs, files in os.walk(dest):
    for f in files:
        if f.endswith(('.html', '.xml', '.txt')) and OLD in io.open(os.path.join(root, f), encoding='utf-8').read():
            stale.append(os.path.join(root, f))
print('stale github.io references left:', len(stale))
for s_ in stale:
    print('  ', s_)

# restore the working copy to its own address so the repo stays consistent
subprocess.check_call([sys.executable, os.path.join(HERE, 'tools', 'make_blog.py'), HERE, OLD])
print('local build restored to', OLD)
