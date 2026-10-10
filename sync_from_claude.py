"""Régénère index.html à partir de la page Claude (fichier HTML passé en argument)."""
import sys
s=open(sys.argv[1],encoding='utf-8').read()
old='<!doctype html><html><head><meta charset=utf8>'
assert s.startswith(old)
head=('<!doctype html><html lang="fr"><head><meta charset="utf-8">'
 '<meta name="description" content="Chalet Le Dahu du Hameau (12 pers.) et appartement Le Petit Dahu (6 pers.) à La Tania, Courchevel. Disponibilités, prix et réservation en direct.">'
 '<script data-goatcounter="https://ledahu.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
 '<script src="stats.js" defer></script>')
open('index.html','w',encoding='utf-8').write(head+s[len(old):])
