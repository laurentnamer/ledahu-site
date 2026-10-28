"""Génère la page « Planning conciergerie » à partir du registre.

Usage : python3 make_conciergerie.py <dossier des séjours JSON> <fichier html de sortie> [page publiée actuelle]

La page contient uniquement ce dont la conciergerie a besoin : logement, dates,
nom, nombre de personnes, e-mail et téléphone. Jamais de montant, d'acompte,
de caution, de note ni de lien vers les outils du propriétaire.
Le fichier produit contient des données personnelles : il ne doit JAMAIS être
ajouté au dépôt GitHub (public). Il est publié uniquement comme page Claude.

Si une page publiée est donnée en 3e argument, le script dit « inchangé »
quand les séjours affichés sont les mêmes, et « changé » sinon.
"""
import datetime
import glob
import json
import os
import re
import sys


def charger(dossier):
    out = []
    for f in sorted(glob.glob(os.path.join(dossier, '**', '*.json'), recursive=True)):
        with open(f, encoding='utf-8') as fh:
            d = json.load(fh)
        if isinstance(d, dict) and isinstance(d.get('data'), dict):
            d = dict(d['data'], id=d.get('id'))
        d.setdefault('id', os.path.splitext(os.path.basename(f))[0])
        out.append(d)
    return out


def contact(s):
    mail, tel = '', ''
    for part in re.split(r'\s*[·|,;/]\s*', (s.get('contact') or '').strip()):
        if '@' in part and not mail:
            mail = part.strip()
        elif re.search(r'\d{6,}', re.sub(r'\D', '', part)) and not tel:
            tel = part.strip()
    return mail, tel


def garder(s, aujourdhui):
    if s.get('exemple') or s.get('statut') == 'annule':
        return False
    if not s.get('arrivee') or not s.get('depart') or s['depart'] <= aujourdhui:
        return False
    if (s.get('client') or '').startswith('Bloqué'):
        return False  # fermetures d'intersaison : rien à préparer
    return True


def composition(s):
    if (s.get('composition') or '').strip():
        return s['composition'].strip()
    m = re.search(r'(\d+)\s+adultes?(?:,\s*(\d+)\s+enfants?)?', s.get('notes') or '', re.I)
    if m:
        a, e = int(m.group(1)), int(m.group(2) or 0)
        txt = '%d adulte%s' % (a, 's' if a > 1 else '')
        if e:
            txt += ', %d enfant%s' % (e, 's' if e > 1 else '')
        return txt
    return ''


def ligne(s):
    mail, tel = contact(s)
    vac = s.get('statut') == 'bloque' and s.get('source') == 'Famille / amis'
    nom = 'Famille Namer' if vac else (s.get('client') or '').strip()
    a = datetime.date.fromisoformat(s['arrivee'])
    b = datetime.date.fromisoformat(s['depart'])
    return {
        'logement': s.get('logement'),
        'arrivee': s['arrivee'],
        'depart': s['depart'],
        'nuits': (b - a).days,
        'nom': nom,
        'personnes': s.get('nbPersonnes') if isinstance(s.get('nbPersonnes'), int) else None,
        'email': mail,
        'tel': tel,
        'statut': 'proprio' if vac else ('option' if s.get('statut') == 'option' else 'confirme'),
        'source': s.get('source') if s.get('source') in ('Abritel', 'Direct') else '',
        'aCompleter': (not vac) and not (mail or tel),
        'composition': '' if vac else composition(s),
        'demandes': (s.get('demandes') or '').strip(),
    }


def main():
    sejours = charger(sys.argv[1])
    aujourdhui = datetime.date.today().isoformat()
    lignes = sorted((ligne(s) for s in sejours if garder(s, aujourdhui)),
                    key=lambda x: (x['arrivee'], x['logement']))
    data = json.dumps({'sejours': lignes, 'majLe': aujourdhui}, ensure_ascii=False, separators=(',', ':'))
    if len(sys.argv) > 3 and os.path.exists(sys.argv[3]):
        ancien = open(sys.argv[3], encoding='utf-8').read()
        m = re.search(r'<script type="application/json" id="planning">(.*?)</script>', ancien, re.S)
        if m:
            try:
                if json.loads(m.group(1)).get('sejours') == lignes:
                    print('inchangé', len(lignes), 'séjours')
                    return
            except ValueError:
                pass
    gabarit = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conciergerie_gabarit.html'), encoding='utf-8').read()
    xl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'occupants_xlsx.js'), encoding='utf-8').read()
    html = gabarit.replace('__XLSX_JS__', xl).replace('__DATA__', data.replace('</', '<\\/'))
    with open(sys.argv[2], 'w', encoding='utf-8') as fh:
        fh.write(html)
    print('changé', len(lignes), 'séjours')


if __name__ == '__main__':
    main()
