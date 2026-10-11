"""Génère calendrier-chalet.ics et calendrier-appartement.ics à partir du registre.

Usage : python3 make_ics.py <dossier contenant les séjours en JSON (un fichier par séjour)>

Ces fichiers sont importés par Abritel pour bloquer les dates des réservations
directes et des vacances de la famille. Ils sont publics : uniquement des dates,
jamais de nom, de contact ni de montant.

Règle : un séjour est exporté s'il n'est pas un exemple, que son départ est
postérieur à aujourd'hui, et
  - soit c'est « Nos vacances » (statut "bloque", source "Famille / amis"),
  - soit son statut est "confirme" ou "bloque" et il ne vient pas d'Abritel
    (origine différente de "ical" et "abritel").
Les options (demandes non confirmées) et les séjours annulés ne sont pas exportés.
"""
import datetime
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def charger(dossier):
    sejours = []
    for f in sorted(glob.glob(os.path.join(dossier, '**', '*.json'), recursive=True)):
        with open(f, encoding='utf-8') as fh:
            d = json.load(fh)
        if isinstance(d, dict) and isinstance(d.get('data'), dict):
            d = dict(d['data'], id=d.get('id'))
        d.setdefault('id', os.path.splitext(os.path.basename(f))[0])
        sejours.append(d)
    return sejours


def exporte(s, aujourdhui):
    if s.get('exemple') or not s.get('arrivee') or not s.get('depart'):
        return False
    if s['depart'] <= aujourdhui:
        return False
    if s.get('statut') == 'bloque' and s.get('source') == 'Famille / amis':
        return True
    return s.get('statut') in ('confirme', 'bloque') and s.get('origine') not in ('ical', 'abritel')


def ics(logement, sejours, stamp):
    lignes = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//ledahudelatania.fr//Calendrier ' + logement + '//FR',
              'CALSCALE:GREGORIAN', 'METHOD:PUBLISH']
    for s in sorted(sejours, key=lambda x: x['arrivee']):
        lignes += ['BEGIN:VEVENT',
                   'UID:' + s['id'] + '@ledahudelatania.fr',
                   'DTSTAMP:' + stamp,
                   'DTSTART;VALUE=DATE:' + s['arrivee'].replace('-', ''),
                   'DTEND;VALUE=DATE:' + s['depart'].replace('-', ''),
                   'SUMMARY:Indisponible',
                   'TRANSP:OPAQUE',
                   'END:VEVENT']
    lignes.append('END:VCALENDAR')
    return '\r\n'.join(lignes) + '\r\n'


def main():
    sejours = charger(sys.argv[1])
    now = datetime.datetime.now(datetime.timezone.utc)
    aujourdhui = now.date().isoformat()
    stamp = now.strftime('%Y%m%dT%H%M%SZ')
    for logement in ('chalet', 'appartement'):
        choisis = [s for s in sejours if s.get('logement') == logement and exporte(s, aujourdhui)]
        chemin = os.path.join(HERE, 'calendrier-%s.ics' % logement)
        nouveau = ics(logement, choisis, stamp)
        # Ne réécrit pas le fichier si seules les dates de génération changent.
        if os.path.exists(chemin):
            ancien = open(chemin, encoding='utf-8', newline='').read()
            sans = lambda t: '\n'.join(l for l in t.splitlines() if not l.startswith('DTSTAMP:'))
            if sans(ancien) == sans(nouveau):
                print(logement, 'inchangé', len(choisis), 'séjours')
                continue
        with open(chemin, 'w', encoding='utf-8', newline='') as fh:
            fh.write(nouveau)
        print(logement, 'écrit', len(choisis), 'séjours :', ', '.join(s['arrivee'] + '→' + s['depart'] for s in sorted(choisis, key=lambda x: x['arrivee'])))


if __name__ == '__main__':
    main()
