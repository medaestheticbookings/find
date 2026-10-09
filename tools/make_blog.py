# -*- coding: utf-8 -*-
"""Builds blog/index.html and the article pages off one shared shell."""
import io, os, json, sys

OUT = sys.argv[1]            # repo root
BASE = 'https://medaestheticbookings.github.io/find/'
BLOG = BASE + 'blog/'
FAQ = BASE + 'faq/'

SHELL_CSS = u"""
  :root{
    --cream:#FAF7F2; --cream-alt:#F3EDE3; --card:#FFFFFF;
    --teal:#0F4A5E; --teal-deep:#0A3746; --teal-soft:#3B6D7E;
    --brass:#A8763E; --brass-lift:#C08F4F;
    --brass-ink:#8A5E2C; --brass-btn:#8F6330; --brass-btn-dark:#7A5226;
    --ink:#12303B; --ink-soft:#5A6B72; --line:#E2DACE;
    --radius:16px;
    --shadow-sm:0 1px 2px rgba(15,74,94,.05), 0 1px 1px rgba(15,74,94,.04);
    --shadow-md:0 10px 28px rgba(15,74,94,.09), 0 2px 6px rgba(15,74,94,.05);
    --shadow-lg:0 22px 52px rgba(15,74,94,.14), 0 4px 12px rgba(15,74,94,.06);
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  html{scroll-behavior:smooth;-webkit-text-size-adjust:100%;}
  body{background:var(--cream);color:var(--ink);font-family:'Inter',sans-serif;
    line-height:1.68;-webkit-font-smoothing:antialiased;overflow-x:hidden;}
  h1,h2,h3{font-weight:800;letter-spacing:-0.035em;text-wrap:balance;color:var(--ink);}
  img{max-width:100%;display:block;}
  a{color:inherit;text-decoration:none;}
  :focus-visible{outline:2px solid var(--brass);outline-offset:3px;}
  .wrap{width:100%;max-width:1120px;margin:0 auto;padding:0 20px;}
  .narrow{max-width:760px;}
  nav{position:sticky;top:0;z-index:60;background:rgba(250,247,242,.94);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--line);}
  nav .wrap{display:flex;align-items:center;justify-content:space-between;height:66px;gap:10px;}
  nav .logo{height:28px;width:auto;}
  @media (max-width:520px){nav .logo{height:22px;}}
  .nav-right{display:flex;align-items:center;gap:10px;}
  .nav-ig{display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;
    border-radius:50%;color:var(--teal);border:1px solid var(--line);background:var(--card);}
  .nav-ig:hover{color:var(--brass-ink);border-color:var(--brass-ink);}
  .nav-cta{font-size:13.5px;font-weight:700;padding:10px 18px;background:var(--brass-btn);
    color:#fff;border-radius:999px;white-space:nowrap;}
  .nav-cta:hover{background:var(--brass-btn-dark);}
  .crumb{font-size:13px;color:var(--ink-soft);padding:26px 0 0;}
  .crumb a{color:var(--teal);font-weight:600;}
  footer{background:var(--teal-deep);color:rgba(250,247,242,.72);padding:44px 0 34px;
    font-size:14px;text-align:center;margin-top:70px;}
  footer a{color:var(--cream);text-decoration:underline;text-underline-offset:3px;}
  footer .flogo{height:24px;width:auto;margin:0 auto 16px;filter:brightness(0) invert(1);opacity:.9;}
  footer .fine{font-size:12.5px;color:rgba(250,247,242,.82);margin-top:12px;line-height:1.6;}
  .cta-band{background:var(--teal);color:var(--cream);border-radius:var(--radius);
    padding:34px 32px;margin:48px 0 0;text-align:center;}
  .cta-band h3{color:var(--cream);font-size:22px;margin-bottom:10px;}
  .cta-band p{color:rgba(250,247,242,.8);font-size:15.5px;margin-bottom:20px;}
  .btn{display:inline-flex;align-items:center;justify-content:center;background:var(--brass-btn);
    color:#fff;font-weight:800;font-size:16px;padding:16px 32px;border-radius:12px;
    box-shadow:var(--shadow-md);}
  .btn:hover{background:var(--brass-btn-dark);}
"""

LOGO_IG = (u'<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" '
           u'd="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 '
           u'4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 '
           u'0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 '
           u'0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 '
           u'4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 '
           u'3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 '
           u'3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 '
           u'0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 '
           u'5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 '
           u'1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>')


def nav(prefix):
    return (u'<nav><div class="wrap">\n'
            u'  <a href="' + prefix + u'index.html"><img src="' + prefix + u'img/logo.png" alt="Med Aesthetic Bookings" class="logo"></a>\n'
            u'  <div class="nav-right">\n'
            u'    <a href="https://www.instagram.com/medaestheticbookings/" target="_blank" rel="noopener" class="nav-ig" aria-label="Instagram">' + LOGO_IG + u'</a>\n'
            u'    <a href="' + prefix + u'blog/" class="nav-blog">Blog</a>\n'
            u'    <a href="' + prefix + u'faq/" class="nav-blog">Συχνές ερωτήσεις</a>\n'
            u'    <a href="' + prefix + u'index.html#form" class="nav-cta">Βρες κλινική</a>\n'
            u'  </div>\n</div></nav>')


def footer(prefix):
    return (u'<footer><div class="wrap">\n'
            u'  <img src="' + prefix + u'img/logo.png" alt="Med Aesthetic Bookings" class="flogo">\n'
            u'  <div><a href="mailto:medaestheticbooking@outlook.com">medaestheticbooking@outlook.com</a></div>\n'
            u'  <div style="margin-top:10px"><a href="https://www.instagram.com/medaestheticbookings/" target="_blank" rel="noopener">@medaestheticbookings</a>'
            u' · <a href="' + prefix + u'privacy.html">Δήλωση απορρήτου</a>'
            u' · <a href="' + prefix + u'blog/">Blog</a>'
            u' · <a href="' + prefix + u'faq/">Συχνές ερωτήσεις</a></div>\n'
            u'  <div class="fine">Η Med Aesthetic Bookings είναι υπηρεσία παραπομπής. Δεν είμαστε κλινική και δεν παρέχουμε ιατρικές συμβουλές. Κάθε θεραπεία εκτελείται από την αδειοδοτημένη κλινική που επιλέγεις.</div>\n'
            u'  <div class="fine">© 2026 Med Aesthetic Bookings</div>\n'
            u'</div></footer>')


CTA = (u'<div class="cta-band">\n'
       u'  <h3>Θέλεις να το κάνεις;</h3>\n'
       u'  <p>Πες μας ποια θεραπεία σε ενδιαφέρει και σε ποια περιοχή είσαι. Σου στέλνουμε τις καλύτερες κλινικές κοντά σου μέσα σε 24 ώρες. Δωρεάν.</p>\n'
       u'  <a href="../index.html#form" class="btn">Βρες μου κλινική</a>\n'
       u'</div>')

POSTS = [
    {
        'slug': 'apotrichosi-laser-poses-synedries',
        'img': 'laser.jpg',
        'date': '2026-10-09',
        'cat': u'Αποτρίχωση',
        'title': u'Αποτρίχωση με laser: πόσες συνεδρίες χρειάζεσαι πραγματικά;',
        'desc': u'Πόσες συνεδρίες θέλει η αποτρίχωση με laser, από τι εξαρτάται ο αριθμός τους και πώς να καταλάβεις αν μια κλινική σου λέει την αλήθεια.',
        'body': [
            ('p', u'Η πιο συχνή ερώτηση που λαμβάνουμε είναι ακριβώς αυτή, και η ειλικρινής απάντηση είναι: εξαρτάται. Οποιοσδήποτε σου δώσει έναν ακριβή αριθμό πριν δει το δέρμα και την τρίχα σου, σου πουλάει κάτι. Υπάρχουν όμως πραγματικά εύρη και πραγματικοί παράγοντες, και αξίζει να τους ξέρεις πριν μπεις σε πακέτο.'),
            ('h2', u'Το ρεαλιστικό εύρος'),
            ('p', u'Για τις περισσότερες περιοχές του σώματος, οι κλινικές με τις οποίες συνεργαζόμαστε συζητούν για <strong>6 έως 10 συνεδρίες</strong> για το βασικό αποτέλεσμα, με διαστήματα τεσσάρων έως οκτώ εβδομάδων. Μετά από αυτό, οι περισσότεροι άνθρωποι χρειάζονται μία συνεδρία συντήρησης μία ή δύο φορές τον χρόνο.'),
            ('h2', u'Από τι εξαρτάται'),
            ('ul', [
                u'<strong>Η αντίθεση τρίχας και δέρματος.</strong> Σκούρα τρίχα σε ανοιχτό δέρμα ανταποκρίνεται πιο γρήγορα. Ξανθή, γκρι ή πολύ λεπτή τρίχα ανταποκρίνεται λιγότερο ή καθόλου.',
                u'<strong>Η περιοχή.</strong> Οι μασχάλες και το μπικίνι συνήθως ανταποκρίνονται πιο γρήγορα από τα πόδια ή την πλάτη.',
                u'<strong>Οι ορμόνες.</strong> Περιπτώσεις όπως ο ΠΚΩ μπορεί να χρειάζονται περισσότερες συνεδρίες και συχνότερη συντήρηση.',
                u'<strong>Το μηχάνημα.</strong> Ένα σωστά συντηρημένο διοδικό laser ή Alexandrite δεν είναι το ίδιο με μια συσκευή IPL κομμωτηρίου.',
            ]),
            ('h2', u'Το κόκκινο πανί: τα πακέτα'),
            ('p', u'Πολλές κλινικές πουλάνε πακέτα των οκτώ ή δέκα συνεδριών με έκπτωση. Δεν είναι απαραίτητα κακό — αλλά ρώτα δύο πράγματα πριν πληρώσεις: αν οι συνεδρίες έχουν ημερομηνία λήξης και αν επιστρέφονται χρήματα αν πετύχεις το αποτέλεσμα σε λιγότερες.'),
            ('h2', u'Τι να ρωτήσεις στην πρώτη επίσκεψη'),
            ('p', u'Ποιο μηχάνημα χρησιμοποιείτε και γιατί το επιλέξατε για το δικό μου τύπο δέρματος; Κάνετε δοκιμαστική βολή; Ποιος χειρίζεται το μηχάνημα και τι εκπαίδευση έχει; Μια σοβαρή κλινική απαντάει σε αυτά χωρίς να δυσκολεύεται.'),
        ],
    },
    {
        'slug': 'prx-t33-i-biorepeel',
        'img': 'skin.jpg',
        'date': '2026-10-09',
        'cat': u'Πρόσωπο',
        'title': u'PRX-T33 ή BioRePeel; Ποιο ταιριάζει στο δέρμα σου',
        'desc': u'Δύο θεραπείες χωρίς downtime που μπερδεύονται συχνά. Τι κάνει η καθεμία και ποια να ζητήσεις.',
        'body': [
            ('p', u'Και οι δύο διαφημίζονται ως «πείλινγκ χωρίς ξεφλούδισμα» και γι’ αυτό μπερδεύονται. Κάνουν όμως διαφορετική δουλειά.'),
            ('h2', u'PRX-T33 — για σφριγηλότητα και λάμψη'),
            ('p', u'Δουλεύει στην αναδόμηση του κολλαγόνου χωρίς να τραυματίζει την επιδερμίδα. Διάλεξέ το αν το θέμα σου είναι χαλαρή υφή, θαμπάδα, λεπτές γραμμές, ουλές ακμής ή ραγάδες. Είναι ασφαλές και το καλοκαίρι.'),
            ('h2', u'BioRePeel — για πόρους και ακμή'),
            ('p', u'Πιο κοντά σε κλασικό πείλινγκ ως προς τον σκοπό: καθαρίζει πόρους, λειαίνει την υφή και βοηθάει σε λιπαρό δέρμα και ενεργή ακμή. Διάλεξέ το αν το δέρμα σου βουλώνει ή γυαλίζει.'),
            ('h2', u'Μπορείς να κάνεις και τα δύο;'),
            ('p', u'Ναί, σε κύκλους και σε σωστή σειρά — αλλά αυτό το κρίνει η κλινική αφού δει το δέρμα σου. Αν κάποιος σου πουλήσει και τα δύο πριν σε εξετάσει, αλλάξε κλινική.'),
        ],
    },
    {
        'slug': 'leukansi-dontion-peiraias',
        'img': 'teeth2.jpg',
        'date': '2026-10-09',
        'cat': u'Πειραιάς',
        'title': u'Λεύκανση δοντιών στον Πειραιά: τι περιλαμβάνει μια σωστή συνεδρία',
        'desc': u'Τι πρέπει να περιλαμβάνει η επαγγελματική λεύκανση σε οδοντιατρείο στον Πειραιά, και πού κρύβονται οι εκπλήξεις στο κόστος.',
        'body': [
            ('p', u'Η λεύκανση είναι από τις πιο διαφημιζόμενες υπηρεσίες στον Πειραιά, και από τις πιο άνισες σε ποιότητα. Το ίδιο όνομα θεραπείας μπορεί να σημαίνει δύο πολύ διαφορετικά πράγματα.'),
            ('h2', u'Τι περιλαμβάνει μια σωστή συνεδρία'),
            ('ul', [
                u'<strong>Έλεγχο πριν.</strong> Τερηδόνα, ουλίτιδα ή εκτεθειμένες ρίζες πρέπει να αντιμετωπιστούν πρώτα. Λεύκανση πάνω σε πρόβλημα πονάει και δεν κρατάει.',
                u'<strong>Καθαρισμό.</strong> Πέτρα και χρώσεις φεύγουν πριν, αλλιώς λευκαίνεις την πλάκα.',
                u'<strong>Προστασία ούλων.</strong> Αυτό είναι που κάνει τη διαφορά στην ευαισθησία.',
                u'<strong>Οδηγίες και κιτ συντήρησης.</strong> Χωρίς αυτά, χάνεις μέρος του αποτελέσματος μέσα σε μήνες.',
            ]),
            ('h2', u'Πού κρύβεται το κόστος'),
            ('p', u'Η διαφημιζόμενη τιμή συχνά δεν περιλαμβάνει τον καθαρισμό ή το κιτ. Ρώτα ευθέως τι ακριβώς περιλαμβάνει το ποσό και αν ο έλεγχος χρεώνεται χωριστά. Δεν δημοσιεύουμε τιμές εδώ επειδή διαφέρουν πραγματικά ανά οδοντιατρείο — σου στέλνουμε τις τρέχουσες τιμές των κλινικών της περιοχής σου όταν μας το ζητήσεις.'),
            ('h2', u'Μία συνεδρία ή περισσότερες;'),
            ('p', u'Για τους περισσότερους, μία. Αν τα δόντια σου έχουν βαθιές χρώσεις από χρόνια καφέ ή κάπνισμα, ο οδοντίατρος μπορεί να προτείνει μια δεύτερη ή συνδυασμό με λεύκανση στο σπίτι. Αυτό πρέπει να σου λέγεται πριν, όχι αφού πληρώσεις.'),
        ],
    },
    {
        'slug': 'kostos-apotrichosi-laser-athina',
        'img': 'laser-cost.jpg',
        'date': '2026-10-09',
        'cat': u'Αθήνα',
        'title': u'Πόσο κοστίζει η αποτρίχωση με laser στην Αθήνα;',
        'desc': u'Τι καθορίζει πραγματικά την τιμή της αποτρίχωσης laser στην Αθήνα, γιατί οι διαφημίσεις των 10 ευρώ είναι παραπλανητικές, και πώς να συγκρίνεις σωστά.',
        'body': [
            ('p', u'Θα δεις διαφημίσεις «από 10 ευρώ» και πακέτα ολικής σώματος που φαίνονται πολύ φθηνά. Και τα δύο μπορεί να είναι αληθινά και ταυτόχρονα άχρηστα για να αποφασίσεις.'),
            ('h2', u'Γιατί δεν δίνουμε έναν αριθμό'),
            ('p', u'Επειδή η τιμή ανά συνεδρία δεν είναι το κόστος. Το κόστος είναι <strong>τιμή ανά συνεδρία × συνεδρίες που θα χρειαστείς</strong>, και ο δεύτερος αριθμός εξαρτάται από το δέρμα σου, την τρίχα σου και το μηχάνημα. Ένα φθηνό μηχάνημα που θέλει δεκαπέντε συνεδρίες είναι ακριβότερο από ένα σωστό που θέλει επτά.'),
            ('h2', u'Τι μετακινεί την τιμή'),
            ('ul', [
                u'<strong>Η περιοχή του σώματος.</strong> Άνω χείλος και μασχάλες είναι από τις φθηνότερες, πλάτη και πόδια από τις ακριβότερες.',
                u'<strong>Πακέτο ή μεμονωμένη.</strong> Τα πακέτα κατεβάζουν την τιμή ανά συνεδρία, αλλά σε δεσμεύουν.',
                u'<strong>Η γειτονιά.</strong> Κολωνάκι και Γλυφάδα τιμολογούν διαφορετικά από τον Πειραιά ή τα δυτικά προάστια, για την ίδια δουλειά.',
                u'<strong>Το μηχάνημα.</strong> Η συντήρηση και η ανανέωση κοστίζουν, και αυτό περνάει στην τιμή — δικαιολογημένα.',
            ]),
            ('h2', u'Πώς να συγκρίνεις σωστά'),
            ('p', u'Ζήτα από κάθε κλινική <strong>συνολικό κόστος για το αποτέλεσμα</strong>, όχι τιμή ανά συνεδρία: πόσες συνεδρίες εκτιμούν για εσένα, τι κοστίζουν συνολικά, και τι γίνεται αν χρειαστούν παραπάνω. Αν δεν μπορούν να το απαντήσουν πριν σε δουν, είναι εντάξει — αλλά τότε δεν μπορούν και να σου διαφημίσουν τιμή.'),
            ('h2', u'Σου το μαζεύουμε εμείς'),
            ('p', u'Αντί να πάρεις οκτώ τηλέφωνα, πες μας τι ψάχνεις και σε ποια περιοχή. Σου στέλνουμε τις τρέχουσες τιμές από ελεγμένες κλινικές κοντά σου, με το τι περιλαμβάνουν. Δωρεάν.'),
        ],
    },
    {
        'slug': 'mesotherapia-mallion-trichoptosi',
        'img': 'hair.jpg',
        'date': '2026-10-09',
        'cat': u'Τριχόπτωση',
        'title': u'Μεσοθεραπεία μαλλιών και PRP: πότε βοηθάνε στην τριχόπτωση',
        'desc': u'Τι κάνει η μεσοθεραπεία τριχωτού και το PRP, σε ποιον ταιριάζουν, και γιατί η διάγνωση είναι πιο σημαντική από τη θεραπεία.',
        'body': [
            ('p', u'Η τριχόπτωση είναι από τα λίγα αισθητικά θέματα όπου το «ξεκίνα μια θεραπεία και βλέπουμε» χάνει χρόνο που δεν παίρνεις πίσω. Η τρίχα που έχει φύγει οριστικά δεν επιστρέφει με ενέσεις.'),
            ('h2', u'Πρώτα η διάγνωση'),
            ('p', u'Ανδρογενετική αλωπεκία, τηλογενές defluvium μετά από στρες ή ασθένεια, έλλειψη σιδήρου, θυρεοειδής, αυτοάνοσο — αυτά αντιμετωπίζονται αλλιώς το καθένα. Μια σοβαρή κλινική θα ζητήσει ιστορικό και πιθανότατα αιματολογικές πριν σου πουλήσει κύκλο συνεδριών.'),
            ('h2', u'Τι κάνει η μεσοθεραπεία'),
            ('p', u'Μικροενέσεις βιταμινών, αμινοξέων και αυξητικών παραγόντων στο τριχωτό, ώστε ο θύλακος να τραφεί καλύτερα. Δουλεύει καλύτερα σε τρίχα που <strong>λεπταίνει</strong>, όχι σε περιοχή που έχει ήδη αδειάσει εντελώς.'),
            ('h2', u'Τι κάνει το PRP'),
            ('p', u'Παίρνουν αίμα σου, το φυγοκεντρούν και ενίουν το πλάσμα πλούσιο σε αιμοπετάλια πίσω στο τριχωτό. Ίδια λογική, διαφορετικό υλικό — δικό σου. Συχνά γίνονται συνδυαστικά, σε κύκλους, με επανεκτίμηση στην πορεία.'),
            ('h2', u'Ρεαλιστικές προσδοκίες'),
            ('p', u'Στόχος είναι να <strong>σταματήσει η πτώση</strong> και να πυκνώσει η υπάρχουσα τρίχα. Όποιος σου υπόσχεται νέα μαλλιά σε άδεια περιοχή, υπερβάλλει. Αν η πτώση είναι προχωρημένη, η ειλικρινής συζήτηση είναι για μεταμόσχευση, όχι για ενέσεις.'),
        ],
    },
    {
        'slug': 'salmon-dna-microneedling',
        'img': 'microneedling.jpg',
        'date': '2026-10-09',
        'cat': u'Αναζωογόνηση',
        'title': u'Salmon DNA και microneedling: τι είναι και γιατί γίνονται μαζί',
        'desc': u'Τι είναι τα πολυνουκλεοτίδια («salmon DNA»), τι κάνει το microneedling, και γιατί ο συνδυασμός τους δουλεύει καλύτερα από το καθένα χωριστά.',
        'body': [
            ('p', u'Θα το δεις διαφημισμένο ως «salmon DNA» και ακούγεται σαν μάρκετινγκ. Δεν είναι. Πρόκειται για <strong>πολυνουκλεοτίδια</strong> — καθαρισμένα θραύσματα DNA από σολομό, τα οποία είναι βιολογικά πολύ κοντά στο ανθρώπινο DNA και γι’ αυτό τα αναγνωρίζει το δέρμα μας.'),
            ('h2', u'Τι κάνουν τα πολυνουκλεοτίδια'),
            ('p', u'Δεν γεμίζουν και δεν παγώνουν τίποτα. Δίνουν στους ινοβλάστες — τα κύτταρα που φτιάχνουν κολλαγόνο — το υλικό και το ερέθισμα να δουλέψουν. Το αποτέλεσμα είναι σταδιακό: καλύτερη ενυδάτωση, πυκνότερο δέρμα, λιγότερη λεπτή γραμμή. Όχι άμεση αλλαγή σχήματος.'),
            ('h2', u'Τι κάνει το microneedling'),
            ('p', u'Μικροσκοπικές βελόνες δημιουργούν ελεγχόμενους μικροτραυματισμούς. Το δέρμα απαντά με επούλωση, δηλαδή νέο κολλαγόνο. Βοηθά σε ουλές ακμής, πόρους και υφή.'),
            ('h2', u'Γιατί μαζί'),
            ('p', u'Το microneedling ανοίγει διαύλους και ξεκινά τη διαδικασία επούλωσης· τα πολυνουκλεοτίδια μπαίνουν ακριβώς τότε και τροφοδοτούν αυτή τη διαδικασία. Το ένα δημιουργεί τη ζήτηση, το άλλο δίνει την προσφορά. Γι’ αυτό πολλές κλινικές τα συνδυάζουν στην ίδια συνεδρία.'),
            ('h2', u'Τι να περιμένεις ρεαλιστικά'),
            ('ul', [
                u'<strong>Κύκλος, όχι μία φορά.</strong> Συνήθως τρεις έως τέσσερις συνεδρίες, ανά τρεις έως τέσσερις εβδομάδες.',
                u'<strong>Λίγο downtime.</strong> Ερυθρότητα για μία με δύο μέρες μετά το microneedling.',
                u'<strong>Αποτέλεσμα που χτίζεται.</strong> Το καλύτερο σημείο είναι συνήθως ένα με δύο μήνες μετά τον κύκλο.',
                u'<strong>Αντηλιακό, υποχρεωτικά.</strong> Δέρμα σε επούλωση και ελληνικός ήλιος δεν πάνε μαζί.',
            ]),
            ('h2', u'Σε ποιον δεν ταιριάζει'),
            ('p', u'Σε ενεργή φλεγμονώδη ακμή, ενεργό έρπη, δερματικές λοιμώξεις ή αλλεργία σε ψάρι, πρέπει να το συζητήσεις πριν. Μια σοβαρή κλινική θα το ρωτήσει η ίδια.'),
        ],
    },
    {
        'slug': 'hydrafacial-ti-einai',
        'img': 'hydrafacial.jpg',
        'date': '2026-10-09',
        'cat': u'Πρόσωπο',
        'title': u'HydraFacial: τι είναι και σε ποιον πραγματικά αξίζει',
        'desc': u'Πώς δουλεύει το HydraFacial, σε τι διαφέρει από τον κλασικό καθαρισμό, και πότε δεν αξίζει τα λεφτά του.',
        'body': [
            ('p', u'Το HydraFacial έγινε δημοφιλές επειδή υπόσχεται καθαρό και λαμπερό δέρμα χωρίς κοκκινίλα και χωρίς να χάσεις τη μέρα σου. Σε μεγάλο βαθμό το τηρεί — αρκεί να ξέρεις τι αγοράζεις.'),
            ('h2', u'Πώς δουλεύει'),
            ('p', u'Μια συσκευή με κεφαλή κενού κάνει τρία πράγματα ταυτόχρονα: απολεπίζει, <strong>αναρροφά</strong> το περιεχόμενο των πόρων και ταυτόχρονα εισάγει ορούς. Η διαφορά από τον κλασικό καθαρισμό είναι ότι η εξαγωγή γίνεται με αναρρόφηση αντί για πίεση με τα δάχτυλα.'),
            ('h2', u'Σε ποιον αξίζει'),
            ('ul', [
                u'Σε θαμπό δέρμα που θέλει λάμψη πριν από ένα γεγονός — το αποτέλεσμα είναι άμεσο.',
                u'Σε ευαίσθητο δέρμα που δεν αντέχει τη χειρωνακτική εξαγωγή.',
                u'Σε όποιον δεν μπορεί να έχει κοκκινίλα την επόμενη μέρα.',
            ]),
            ('h2', u'Πότε δεν αξίζει'),
            ('p', u'Αν έχεις <strong>βαθιά μαύρα στίγματα και πολλά μιλιά</strong>, η αναρρόφηση δεν τα βγάζει όλα και ένας σωστός <a href="facial-8-vimaton-ti-perilamvanei.html">καθαρισμός οκτώ βημάτων</a> με χειρωνακτική εξαγωγή θα σε πάει πιο μακριά. Και αν ψάχνεις αλλαγή σε ουλές ή ρυτίδες, το HydraFacial δεν είναι το εργαλείο — εκεί κοιτάς <a href="salmon-dna-microneedling.html">microneedling</a> ή <a href="prx-t33-i-biorepeel.html">PRX-T33</a>.'),
            ('h2', u'Κάθε πότε'),
            ('p', u'Κάθε τέσσερις εβδομάδες αν το κάνεις ως συντήρηση. Μία φορά πριν από γάμο ή φωτογράφιση δίνει λάμψη, αλλά δεν αλλάζει τίποτα μόνιμα.'),
        ],
    },
    {
        'slug': 'high-frequency-wand',
        'img': 'highfreq.jpg',
        'date': '2026-10-09',
        'cat': u'Ακμή',
        'title': u'High frequency wand: τι κάνει αυτή η «μαγική ράβδος» στην ακμή',
        'desc': u'Πώς λειτουργεί η θεραπεία υψηλής συχνότητας, γιατί χρησιμοποιείται μετά τον καθαρισμό, και τι να μην περιμένεις από αυτήν.',
        'body': [
            ('p', u'Η γυάλινη ράβδος που σπινθηρίζει μωβ στο τέλος του καθαρισμού δεν είναι εντυπωσιασμός. Είναι θεραπεία υψηλής συχνότητας, και έχει συγκεκριμένη δουλειά.'),
            ('h2', u'Τι κάνει'),
            ('p', u'Ο γυάλινος ηλεκτρόδιο-σωλήνας περιέχει αδρανές αέριο. Με το ρεύμα υψηλής συχνότητας παράγεται <strong>οζόν</strong> στην επιφάνεια του δέρματος, που έχει αντιβακτηριακή δράση, και ταυτόχρονα βελτιώνεται η τοπική κυκλοφορία.'),
            ('h2', u'Γιατί μπαίνει μετά την εξαγωγή'),
            ('p', u'Αμέσως μετά την εξαγωγή οι πόροι είναι ανοιχτοί και εκτεθειμένοι. Το πέρασμα με high frequency μειώνει το βακτηριακό φορτίο εκείνη ακριβώς τη στιγμή, γι’ αυτό και βοηθά να μην πεταχτούν νέα σπυράκια τις επόμενες μέρες.'),
            ('h2', u'Τι να μην περιμένεις'),
            ('p', u'Δεν θεραπεύει την ακμή. Είναι <strong>βοηθητικό βήμα</strong> μέσα σε μια σωστή διαδικασία, όχι αυτόνομη λύση. Αν κάποιος σου πουλήσει κύκλο συνεδριών μόνο με high frequency για μέτρια ή σοβαρή ακμή, ψάξε αλλού — εκεί χρειάζεται δερματολόγος.'),
            ('h2', u'Πότε αποφεύγεται'),
            ('p', u'Σε εγκυμοσύνη, βηματοδότη, επιληψία, μεταλλικά εμφυτεύματα στην περιοχή ή ροδόχρου νόσο σε έξαρση. Η κλινική οφείλει να σε ρωτήσει πριν.'),
        ],
    },
    {
        'slug': 'diamond-dermabrasion',
        'img': 'dermabrasion.jpg',
        'date': '2026-10-09',
        'cat': u'Πρόσωπο',
        'title': u'Διαμαντένια μικροδερμοαπόξεση: για ποιο δέρμα είναι',
        'desc': u'Τι κάνει η diamond dermabrasion, σε τι διαφέρει από τα peeling και το HydraFacial, και πότε είναι λάθος επιλογή.',
        'body': [
            ('p', u'Η διαμαντένια μικροδερμοαπόξεση είναι μηχανική απολέπιση: μια κεφαλή με διαμαντόσκονη περνά πάνω από το δέρμα και αφαιρεί την επιφανειακή νεκρή στιβάδα, ενώ ταυτόχρονα αναρροφά τα υπολείμματα.'),
            ('h2', u'Τι βελτιώνει'),
            ('ul', [
                u'Τραχιά υφή και θαμπάδα.',
                u'Διεσταλμένους πόρους και επιφανειακά μαύρα στίγματα.',
                u'Επιφανειακές ουλές ακμής — σταδιακά, σε κύκλο συνεδριών.',
                u'Την απορρόφηση των προϊόντων που βάζεις μετά.',
            ]),
            ('h2', u'Σε τι διαφέρει από τα peeling'),
            ('p', u'Η μικροδερμοαπόξεση είναι <strong>μηχανική</strong>, τα peeling είναι <strong>χημικά</strong>. Η πρώτη δουλεύει στην επιφάνεια και είναι προβλέψιμη· ένα <a href="prx-t33-i-biorepeel.html">BioRePeel ή PRX-T33</a> φτάνει βαθύτερα και στοχεύει και σε θέματα τόνου και σφριγηλότητας.'),
            ('h2', u'Πότε είναι λάθος επιλογή'),
            ('p', u'Σε <strong>ενεργή φλεγμονώδη ακμή</strong> η τριβή χειροτερεύει τα πράγματα και διασπείρει τη φλεγμονή. Το ίδιο σε ροδόχρου νόσο, έκζεμα, ή δέρμα που μόλις πήρε ισοτρετινοΐνη. Σε πολύ λεπτό ή ευαίσθητο δέρμα, προτίμησε ενζυμική απολέπιση.'),
            ('h2', u'Μετά τη συνεδρία'),
            ('p', u'Ελαφριά ερυθρότητα για λίγες ώρες και αυξημένη ευαισθησία στον ήλιο για μερικές μέρες. Αντηλιακό δεν είναι προαιρετικό.'),
        ],
    },
    {
        'slug': 'led-light-therapy',
        'img': 'led.jpg',
        'date': '2026-10-09',
        'cat': u'Αναζωογόνηση',
        'title': u'LED light therapy: τι κάνει το κόκκινο και τι το μπλε φως',
        'desc': u'Πώς δουλεύει η θεραπεία με LED στο πρόσωπο, τι κάνει κάθε χρώμα, και γιατί χρειάζεται συνέπεια για να δεις κάτι.',
        'body': [
            ('p', u'Η θεραπεία με LED δεν καίει, δεν τσιμπάει και δεν έχει downtime. Αυτό την κάνει εύκολη — και εύκολα υπερδιαφημισμένη. Δουλεύει, αλλά σε συγκεκριμένα πράγματα και με συγκεκριμένο τρόπο.'),
            ('h2', u'Τι κάνει κάθε χρώμα'),
            ('ul', [
                u'<strong>Κόκκινο (περίπου 630–660 nm).</strong> Φτάνει βαθύτερα, διεγείρει τους ινοβλάστες και την παραγωγή κολλαγόνου. Για λεπτές γραμμές, σφριγηλότητα και επούλωση.',
                u'<strong>Μπλε (περίπου 415 nm).</strong> Στοχεύει το βακτήριο της ακμής στην επιφάνεια. Για ενεργά σπυράκια.',
                u'<strong>Σε συνδυασμό.</strong> Οι περισσότερες κλινικές τρέχουν πρωτόκολλο που εναλλάσσει τα δύο.',
            ]),
            ('h2', u'Γιατί χρειάζεται συνέπεια'),
            ('p', u'Μία συνεδρία LED δεν κάνει σχεδόν τίποτα ορατό. Η βιβλιογραφία μιλά για <strong>σειρές συνεδριών</strong>, συνήθως δύο φορές την εβδομάδα για τέσσερις έως έξι εβδομάδες, και μετά συντήρηση. Αν κάποιος σου το πουλήσει ως εφάπαξ θαύμα, υπερβάλλει.'),
            ('h2', u'Πού ταιριάζει καλύτερα'),
            ('p', u'Ως <strong>προσθήκη</strong> στο τέλος άλλης θεραπείας: μετά από <a href="facial-8-vimaton-ti-perilamvanei.html">καθαρισμό</a> για να καταπραΰνει, ή μετά από <a href="salmon-dna-microneedling.html">microneedling</a> για να υποστηρίξει την επούλωση. Εκεί δίνει την καλύτερη αξία για τα χρήματα.'),
            ('h2', u'Ασφάλεια'),
            ('p', u'Γενικά πολύ ασφαλής. Προσοχή αν παίρνεις φωτοευαισθητοποιά φάρμακα ή έχεις ιστορικό φωτοευαίσθητης πάθησης — πες το στην κλινική.'),
        ],
    },
    {
        'slug': 'massage-prosopou-somatos',
        'img': 'massage.jpg',
        'date': '2026-10-09',
        'cat': u'Μασάζ',
        'title': u'Μασάζ προσώπου και σώματος: τι να ζητήσεις ανάλογα με τι θέλεις',
        'desc': u'Λεμφικό, χαλαρωτικό, βαθύ ιστών ή μασάζ προσώπου — τι κάνει το καθένα και πώς να μη ζητήσεις λάθος πράγμα.',
        'body': [
            ('p', u'«Θέλω ένα μασάζ» είναι σαν να λες «θέλω ένα φαγητό». Το τι θα πάρεις εξαρτάται από το τι ζητάς, και οι περισσότεροι ζητούν λάθος πράγμα για αυτό που χρειάζονται.'),
            ('h2', u'Λεμφικό μασάζ'),
            ('p', u'Πολύ ελαφριές, ρυθμικές κινήσεις που βοηθούν στην αποσυμφόρηση υγρών. Ζήτα το για <strong>πρήξιμο</strong>, βαριά πόδια, ή μετά από κάποιες αισθητικές επεμβάσεις. Αν πονάει, δεν είναι λεμφικό.'),
            ('h2', u'Μασάζ βαθιών ιστών'),
            ('p', u'Δυνατή πίεση σε συγκεκριμένα σημεία. Για σφιγμένους τραπεζοειδείς, αυχένα από γραφείο, κόμπους. Θα νιώσεις ευαισθησία την επόμενη μέρα — αυτό είναι φυσιολογικό.'),
            ('h2', u'Χαλαρωτικό μασάζ'),
            ('p', u'Σταθερή, συνεχής πίεση σε όλο το σώμα. Στόχος είναι το νευρικό σύστημα, όχι ο μυς. Μην το ζητήσεις αν έχεις πραγματικό μυοσκελετικό πρόβλημα — δεν θα το λύσει.'),
            ('h2', u'Μασάζ προσώπου'),
            ('p', u'Δουλεύει την κυκλοφορία και τη λεμφική παροχέτευση στο πρόσωπο. Βοηθά στο πρήξιμο του πρωινού και δίνει στιγμιαία λάμψη, και συχνά μπαίνει μέσα σε έναν <a href="facial-8-vimaton-ti-perilamvanei.html">ολοκληρωμένο καθαρισμό</a>. Δεν αντικαθιστά θεραπεία σφριγηλότητας.'),
            ('h2', u'Πότε να μην κλείσεις'),
            ('p', u'Με πυρετό, ενεργή λοίμωξη, πρόσφατο τραυματισμό, θρόμβωση ή σε εγκυμοσύνη χωρίς έγκριση γιατρού. Ένας σοβαρός θεραπευτής θα ρωτήσει ιστορικό πριν σε ξαπλώσει.'),
        ],
    },
    {
        'slug': 'facial-8-vimaton-ti-perilamvanei',
        'img': 'facial.jpg',
        'date': '2026-10-09',
        'cat': u'Πρόσωπο',
        'title': u'Facial 8 βημάτων: τι ακριβώς περιλαμβάνει, βήμα-βήμα',
        'desc': u'Τα οκτώ στάδια ενός ολοκληρωμένου ιατρικού καθαρισμού προσώπου, γιατί η σειρά έχει σημασία, και κάθε πότε αξίζει να το κάνεις.',
        'body': [
            ('p', u'Ο όρος «καθαρισμός προσώπου» καλύπτει τα πάντα, από είκοσι λεπτά με έναν ατμό μέχρι μια ολοκληρωμένη διαδικασία μιας ώρας. Το facial οκτώ βημάτων είναι το δεύτερο, και η αξία του είναι ακριβώς στη σειρά των σταδίων.'),
            ('h2', u'Τα οκτώ στάδια'),
            ('ul', [
                u'<strong>1. Διάγνωση δέρματος.</strong> Τύπος, ενυδάτωση, ευαισθησίες — καθορίζει τι θα χρησιμοποιηθεί παρακάτω.',
                u'<strong>2. Βαθύς καθαρισμός.</strong> Αφαίρεση μακιγιάζ, σμήγματος και ρύπων.',
                u'<strong>3. Απολέπιση.</strong> Μηχανική ή ενζυμική, ώστε να μαλακώσει η κεράτινη στιβάδα.',
                u'<strong>4. Ατμός ή μαλακτικό.</strong> Ανοίγει τους πόρους πριν την εξαγωγή.',
                u'<strong>5. Εξαγωγή.</strong> Το στάδιο που κάνει τη διαφορά — και το πιο εύκολο να γίνει λάθος.',
                u'<strong>6. Καταπράυνση.</strong> Αντιφλεγμονώδης αγωγή μετά την εξαγωγή.',
                u'<strong>7. Μάσκα.</strong> Επιλεγμένη με βάση το βήμα 1.',
                u'<strong>8. Ενυδάτωση και αντηλιακό.</strong> Κλείνει τη διαδικασία και προστατεύει.',
            ]),
            ('h2', u'Γιατί η σειρά μετράει'),
            ('p', u'Εξαγωγή χωρίς σωστή προετοιμασία τραυματίζει και αφήνει σημάδια. Μάσκα χωρίς καταπράυνση ερεθίζει. Αν μια κλινική σου κάνει «καθαρισμό» σε είκοσι λεπτά, κάποια βήματα δεν έγιναν.'),
            ('h2', u'Κάθε πότε'),
            ('p', u'Για τους περισσότερους τύπους δέρματος, κάθε τέσσερις έως έξι εβδομάδες στην αρχή και μετά κάθε δύο έως τρεις μήνες. Λιπαρό δέρμα με ενεργή ακμή μπορεί να χρειάζεται πιο συχνά, και τότε αξίζει να συζητήσεις και <a href="prx-t33-i-biorepeel.html">BioRePeel ή PRX-T33</a> παράλληλα.'),
        ],
    },
]


def head(title, desc, canon, img, extra_ld=u''):
    return (u'<!DOCTYPE html>\n<html lang="el">\n<head>\n'
            u'<meta charset="UTF-8">\n'
            u'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            u'<title>' + title + u'</title>\n'
            u'<meta name="description" content="' + desc + u'">\n'
            u'<meta name="robots" content="index,follow">\n'
            u'<link rel="canonical" href="' + canon + u'">\n'
            u'<meta property="og:type" content="article">\n'
            u'<meta property="og:title" content="' + title + u'">\n'
            u'<meta property="og:description" content="' + desc + u'">\n'
            u'<meta property="og:locale" content="el_GR">\n'
            u'<meta property="og:url" content="' + canon + u'">\n'
            u'<meta property="og:image" content="' + img + u'">\n'
            u'<meta name="twitter:card" content="summary_large_image">\n'
            u'<link rel="icon" href="../img/favicon.ico" sizes="any">\n'
            u'<link rel="icon" type="image/png" sizes="32x32" href="../img/icon-32.png">\n'
            u'<link rel="apple-touch-icon" href="../img/apple-icon.png">\n'
            u'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            u'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            u'<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n'
            + extra_ld +
            u'<style>' + SHELL_CSS + ART_CSS + FAQ_CSS + u'</style>\n</head>\n<body>\n')


FAQ_CSS = u"""
  .faq-group{margin-bottom:36px;}
  .faq-group h2{font-size:21px;margin-bottom:4px;padding-bottom:9px;
    border-bottom:2px solid var(--brass);display:inline-block;}
  .faq-item{border-bottom:1px solid var(--line);padding:20px 0;}
  .faq-item h3{font-size:17.5px;margin-bottom:9px;}
  .faq-item p{color:var(--ink-soft);font-size:15.5px;line-height:1.65;}
"""

ART_CSS = u"""
  article{padding:10px 0 0;}
  .meta{font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:var(--brass-ink);
    font-weight:700;margin-bottom:14px;}
  article h1{font-size:clamp(28px,5vw,44px);line-height:1.08;margin-bottom:16px;}
  .lede{font-size:18px;color:var(--ink-soft);margin-bottom:28px;}
  .hero-img{border-radius:var(--radius);overflow:hidden;margin-bottom:34px;box-shadow:var(--shadow-sm);}
  .hero-img img{width:100%;height:auto;}
  article h2{font-size:clamp(20px,3vw,27px);margin:34px 0 12px;}
  article p{margin-bottom:16px;color:var(--ink-soft);font-size:16.5px;}
  article ul{margin:0 0 18px 0;padding-left:20px;}
  article li{margin-bottom:10px;color:var(--ink-soft);font-size:16.5px;}
  article strong{color:var(--ink);}
  .post-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:44px;}
  @media (max-width:860px){.post-grid{grid-template-columns:1fr 1fr;}}
  @media (max-width:600px){.post-grid{grid-template-columns:1fr;}}
  .post{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
    overflow:hidden;box-shadow:var(--shadow-sm);display:flex;flex-direction:column;
    transition:transform .2s ease,box-shadow .2s ease;}
  .post:hover{transform:translateY(-4px);box-shadow:var(--shadow-md);}
  .post .shot{aspect-ratio:16/10;overflow:hidden;background:var(--cream-alt);}
  .post .shot img{width:100%;height:100%;object-fit:cover;}
  .post .pb{padding:22px 22px 24px;flex:1;display:flex;flex-direction:column;}
  .post .cat{font-size:11px;letter-spacing:.13em;text-transform:uppercase;color:var(--brass-ink);
    font-weight:700;margin-bottom:8px;}
  .post h2{font-size:18px;line-height:1.25;margin-bottom:9px;}
  .post p{font-size:14.5px;color:var(--ink-soft);margin:0;}
  .related{margin-top:52px;border-top:1px solid var(--line);padding-top:30px;}
  .related h2{font-size:19px;margin-bottom:16px;}
  .related a{display:block;background:var(--card);border:1px solid var(--line);
    border-radius:var(--radius);padding:18px 20px;margin-bottom:12px;
    transition:border-color .18s ease,transform .18s ease;}
  .related a:hover{border-color:var(--brass);transform:translateY(-2px);}
  .related strong{display:block;font-size:16px;font-weight:800;letter-spacing:-.02em;
    color:var(--ink);margin-bottom:5px;line-height:1.3;}
  .related span{font-size:14px;color:var(--ink-soft);line-height:1.5;}
  .blog-head{text-align:center;max-width:680px;margin:52px auto 0;}
  .blog-head h1{font-size:clamp(30px,5vw,46px);line-height:1.08;margin-bottom:14px;}
  .blog-head p{color:var(--ink-soft);font-size:17px;}
"""


def render_article(post):
    canon = BLOG + post['slug'] + '.html'
    img_abs = BASE + 'img/' + post['img']
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "headline": post['title'],
                "description": post['desc'],
                "image": img_abs,
                "datePublished": post['date'],
                "dateModified": post['date'],
                "inLanguage": "el",
                "mainEntityOfPage": canon,
                "articleSection": post['cat'],
                "author": {"@type": "Organization", "name": "Med Aesthetic Bookings", "url": BASE},
                "publisher": {"@type": "Organization", "name": "Med Aesthetic Bookings",
                              "logo": {"@type": "ImageObject", "url": BASE + "img/logo.png"}},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": u"Αρχική", "item": BASE},
                    {"@type": "ListItem", "position": 2, "name": "Blog", "item": BLOG},
                    {"@type": "ListItem", "position": 3, "name": post['title'], "item": canon},
                ],
            },
        ],
    }
    ld_s = (u'<script type="application/ld+json">'
            + json.dumps(ld, ensure_ascii=False) + u'</script>\n')

    # internal links: the next two posts in the list, so every article is reachable
    i = POSTS.index(post)
    rel = [POSTS[(i + 1) % len(POSTS)], POSTS[(i + 2) % len(POSTS)]]
    related = (u'  <div class="related">\n'
               u'    <h2>Διάβασε επίσης</h2>\n'
               + u''.join(u'    <a href="' + r['slug'] + u'.html"><strong>' + r['title']
                          + u'</strong><span>' + r['desc'] + u'</span></a>\n' for r in rel)
               + u'  </div>\n')

    body = u''
    for kind, val in post['body']:
        if kind == 'p':
            body += u'      <p>' + val + u'</p>\n'
        elif kind == 'h2':
            body += u'      <h2>' + val + u'</h2>\n'
        elif kind == 'ul':
            body += u'      <ul>\n' + u''.join(u'        <li>' + li + u'</li>\n' for li in val) + u'      </ul>\n'

    return (head(post['title'] + u' | Med Aesthetic Bookings', post['desc'], canon, img_abs, ld_s)
            + nav('../')
            + u'\n<div class="wrap narrow">\n'
            + u'  <div class="crumb"><a href="../index.html">Αρχική</a> › <a href="./">Blog</a></div>\n'
            + u'  <article>\n'
            + u'    <div class="meta">' + post['cat'] + u'</div>\n'
            + u'    <h1>' + post['title'] + u'</h1>\n'
            + u'    <p class="lede">' + post['desc'] + u'</p>\n'
            + u'    <div class="hero-img"><img src="../img/' + post['img'] + u'" alt="' + post['title'] + u'" width="1200" height="750"></div>\n'
            + body
            + u'  </article>\n'
            + related
            + u'  ' + CTA + u'\n'
            + u'</div>\n'
            + footer('../') + u'\n</body>\n</html>\n')


def render_index():
    title = (u'Blog — Οδηγοί για θεραπείες '
             u'αισθητικής | Med Aesthetic Bookings')
    desc = (u'Οδηγοί χωρίς μάρκετινγκ: '
            u'αποτρίχωση laser, λεύκανση δοντιών, '
            u'PRX-T33, BioRePeel και τι να ρωτήσεις πριν κλείσεις ραντεβού.')
    cards = u''
    for post in POSTS:
        cards += (u'    <a class="post" href="' + post['slug'] + u'.html">\n'
                  u'      <div class="shot"><img src="../img/' + post['img'] + u'" alt="' + post['title'] + u'" loading="lazy"></div>\n'
                  u'      <div class="pb">\n'
                  u'        <div class="cat">' + post['cat'] + u'</div>\n'
                  u'        <h2>' + post['title'] + u'</h2>\n'
                  u'        <p>' + post['desc'] + u'</p>\n'
                  u'      </div>\n    </a>\n')
    return (head(title, desc, BLOG, BASE + 'img/hero.jpg')
            + nav('../')
            + u'\n<div class="wrap">\n'
            + u'  <div class="blog-head">\n'
            + u'    <h1>Οδηγοί πριν κλείσεις ραντεβού</h1>\n'
            + u'    <p>' + desc + u'</p>\n'
            + u'  </div>\n'
            + u'  <div class="post-grid">\n' + cards + u'  </div>\n'
            + u'</div>\n'
            + footer('../') + u'\n</body>\n</html>\n')


# ---------------------------------------------------------------- FAQ page --
# Constraints baked in deliberately: coverage is Athens / Piraeus / Argyroupoli
# only, no euro figures anywhere (we do not set clinic prices), and the answers
# keep repeating that this is a referral service, not a clinic.
FAQ_GROUPS = [
    (u'Η υπηρεσία', [
        (u'Πόσο μου κοστίζει;',
         u'Τίποτα. Η υπηρεσία είναι δωρεάν για σένα. Πληρωνόμαστε από τις κλινικές με τις οποίες συνεργαζόμαστε, και η τιμή που πληρώνεις στην κλινική είναι η ίδια σαν να την είχες βρει μόνος σου.'),
        (u'Πώς βγάζετε χρήματα;',
         u'Οι συνεργαζόμενες κλινικές μάς πληρώνουν για τις παραπομπές. Αυτό σημαίνει ότι έχουμε λόγο να σου στείλουμε κλινική που θα σε κρατήσει ευχαριστημένο, όχι απλώς την πρώτη διαθέσιμη.'),
        (u'Κλείνετε εσείς το ραντεβού;',
         u'Όχι. Σου στέλνουμε τις επιλογές με τις τιμές τους και κλείνεις εσύ απευθείας με την '
         u'κλινική. Έτσι μιλάς από την αρχή με τον πάροχο που θα σε δει, και κρατάς τον έλεγχο '
         u'της ημερομηνίας.'),
        (u'Δεσμεύομαι σε κάτι;',
         u'Όχι. Παίρνεις τις επιλογές σου και αποφασίζεις εσύ. Μπορείς να μη συνεχίσεις καθόλου ή να μας ζητήσεις διαφορετικές προτάσεις, χωρίς καμία χρέωση.'),
        (u'Σε πόση ώρα θα έχω απάντηση;',
         u'Μέσα σε 24 ώρες τις εργάσιμες ημέρες. Αν αφήσεις τηλέφωνο, μπορεί να σε καλέσουμε πρώτα με δυο ερωτήσεις, ώστε οι προτάσεις να είναι πιο στοχευμένες.'),
        (u'Είστε κλινική;',
         u'Όχι. Είμαστε υπηρεσία παραπομπής. Δεν εκτελούμε θεραπείες, δεν κάνουμε διάγνωση και δεν δίνουμε ιατρικές συμβουλές. Κάθε θεραπεία γίνεται από την αδειοδοτημένη κλινική που θα επιλέξεις.'),
    ]),
    (u'Οι κλινικές', [
        (u'Πώς επιλέγετε τις κλινικές;',
         u'Με αυτή τη σειρά: άδεια λειτουργίας, ο εξοπλισμός που απαιτεί η συγκεκριμένη θεραπεία, τα προσόντα του προσωπικού, οι αξιολογήσεις των πελατών και τέλος η απόσταση από εσένα. Μια κλινική που κόβεται στα τρία πρώτα δεν φτάνει στη λίστα σου όσο κοντά κι αν είναι.'),
        (u'Σε ποιες περιοχές καλύπτετε;',
         u'Για την ώρα Αθήνα, Πειραιάς και Αργυρούπολη, και οι γύρω περιοχές. Προσθέτουμε κι άλλες καθώς συνεργαζόμαστε με νέες κλινικές — αν είσαι αλλού, στείλε τη φόρμα και θα σου πούμε ειλικρινά αν μπορούμε ήδη να βοηθήσουμε.'),
        (u'Μπορώ να ζητήσω άλλη κλινική;',
         u'Ναι. Πες μας τι δεν σου ταίριαξε — ωράριο, τοποθεσία, τρόπος επικοινωνίας — και στέλνουμε άλλες επιλογές.'),
        (u'Τι γίνεται αν δεν μείνω ευχαριστημένος;',
         u'Πες μας το. Το κρατάμε στην αξιολόγηση της κλινικής και σου προτείνουμε άλλη. Για ζήτημα που αφορά την ίδια τη θεραπεία, η κλινική είναι ο πάροχος και απευθύνεσαι πρώτα σε εκείνη.'),
    ]),
    (u'Οι θεραπείες', [
        (u'Ποιες θεραπείες καλύπτετε;',
         u'Λεύκανση δοντιών, αποτρίχωση με laser, facial 8 βημάτων, PRX-T33, BioRePeel και θεραπεία τριχόπτωσης. Αν ψάχνεις κάτι άλλο, ρώτησέ μας — αν δεν το καλύπτουμε, θα στο πούμε ευθέως.'),
        (u'Πόσο κοστίζει η θεραπεία;',
         u'Δεν ορίζουμε εμείς τις τιμές των κλινικών και δεν δημοσιεύουμε ποσά εδώ, γιατί διαφέρουν πραγματικά ανά κλινική και ανά περιοχή σώματος. Σου στέλνουμε τις τρέχουσες τιμές των κλινικών της περιοχής σου μαζί με τις προτάσεις.'),
        (u'Ποια θεραπεία χρειάζομαι;',
         u'Αυτό το κρίνει η κλινική αφού δει το δέρμα ή τα δόντια σου. Εμείς σε συνδέουμε με κάποια που κάνει σωστή αξιολόγηση πριν σου πουλήσει πακέτο. Στο blog εξηγούμε τι κάνει η καθεμία ώστε να πας με τις σωστές ερωτήσεις.'),
        (u'Είναι ασφαλείς;',
         u'Όταν γίνονται σε αδειοδοτημένη κλινική, από εκπαιδευμένο προσωπικό, μετά από αξιολόγηση. Για αυτό η άδεια και ο εξοπλισμός είναι τα δύο πρώτα κριτήριά μας. Δεν είμαστε γιατροί και τίποτα εδώ δεν είναι ιατρική συμβουλή.'),
    ]),
    (u'Τα στοιχεία σου', [
        (u'Τι γίνεται με τα στοιχεία μου;',
         u'Τα χρησιμοποιούμε για να βρούμε την κλινική σου και για να επικοινωνήσουμε μαζί σου για αυτό, και τα δίνουμε μόνο στις κλινικές που σου προτείνουμε πραγματικά. Δεν τα πουλάμε ποτέ σε τρίτους.'),
        (u'Πώς ζητάω διαγραφή;',
         u'Στείλε μήνυμα στο medaestheticbooking@outlook.com και τα διαγράφουμε. Δεν χρειάζεται να δικαιολογήσεις τον λόγο.'),
    ]),
]


def render_faq():
    title = u'Συχνές ερωτήσεις | Med Aesthetic Bookings'
    desc = (u'Πόσο κοστίζει, πώς επιλέγουμε τις κλινικές, σε ποιες περιοχές καλύπτουμε '
            u'και τι γίνεται με τα στοιχεία σου.')
    flat = [(q, a) for _g, qs in FAQ_GROUPS for q, a in qs]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in flat]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1,
             "name": u"Αρχική", "item": BASE},
            {"@type": "ListItem", "position": 2,
             "name": u"Συχνές ερωτήσεις", "item": FAQ}]}]}
    extra = (u'<script type="application/ld+json">'
             + json.dumps(ld, ensure_ascii=False) + u'</script>\n')

    body = u''
    for group, qs in FAQ_GROUPS:
        body += u'  <section class="faq-group">\n    <h2>' + group + u'</h2>\n'
        for q, a in qs:
            body += (u'    <div class="faq-item">\n'
                     u'      <h3>' + q + u'</h3>\n'
                     u'      <p>' + a + u'</p>\n'
                     u'    </div>\n')
        body += u'  </section>\n'

    return (head(title, desc, FAQ, BASE + 'img/hero.jpg', extra)
            + nav('../')
            + u'\n<div class="wrap">\n'
            + u'  <div class="crumb"><a href="../index.html">Αρχική</a> › <a href="./">Συχνές ερωτήσεις</a></div>\n'
            + u'  <div class="blog-head">\n'
            + u'    <h1>Συχνές ερωτήσεις</h1>\n'
            + u'    <p>' + desc + u'</p>\n'
            + u'  </div>\n'
            + body
            + CTA
            + u'</div>\n'
            + footer('../') + u'\n</body>\n</html>\n')


d = os.path.join(OUT, 'blog')
if not os.path.isdir(d):
    os.makedirs(d)

io.open(os.path.join(d, 'index.html'), 'w', encoding='utf-8', newline='').write(render_index())
fd = os.path.join(OUT, 'faq')
if not os.path.isdir(fd):
    os.makedirs(fd)
io.open(os.path.join(fd, 'index.html'), 'w', encoding='utf-8', newline='').write(render_faq())

for post in POSTS:
    io.open(os.path.join(d, post['slug'] + '.html'), 'w', encoding='utf-8', newline='').write(render_article(post))

# ---- robots.txt + sitemap ----
io.open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8', newline='').write(
    u'User-agent: *\nAllow: /\n\nSitemap: ' + BASE + u'sitemap.xml\n')

urls = [(BASE, '1.0'), (FAQ, '0.9'), (BLOG, '0.8')] + [(BLOG + p['slug'] + '.html', '0.7') for p in POSTS]
sm = u'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u_, pr in urls:
    sm += u'  <url><loc>%s</loc><lastmod>2026-10-09</lastmod><priority>%s</priority></url>\n' % (u_, pr)
sm += u'</urlset>\n'
io.open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8', newline='').write(sm)

print('blog built:', len(POSTS), 'posts + index + robots + sitemap')
