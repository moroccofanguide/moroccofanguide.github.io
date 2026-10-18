#!/bin/bash
# Test de débordement horizontal sur 12 largeurs (téléphones 280-440 px, tablettes 768-1024 px), via microlink
# (navigateur distant, gratuit : 25 appels/jour, code ≤ 1024 octets). Un appel par page.
# Lancer : bash outils/test-ecrans.sh [/chemin ...]   → une ligne par page, « largeur:ok » ou « largeur:KO éléments »
F='async({page})=>{const r=[];for(const w of [280,320,360,375,390,402,412,430,440,768,820,1024]){await page.setViewport({width:w,height:900,isMobile:w<1000,hasTouch:true,deviceScaleFactor:2});await page.reload();r.push(await page.evaluate(()=>{const d=document.documentElement,W=d.clientWidth,b=[];for(const e of document.querySelectorAll("body *")){const x=e.getBoundingClientRect();if(x.width&&x.right>W+1&&!e.closest(".table-wrap"))b.push(e.tagName+"."+e.className)}return W+":"+(d.scrollWidth>W||b.length?"KO "+b.slice(0,3):"ok")}))}return r.join(" ")}'
[ $# -gt 0 ] || set -- / /en/ /que-faire-a-marrakech/ /excursions-depuis-marrakech/ /traversee-bateau-espagne-maroc/ /en/ferry-spain-morocco/
for p in "$@"; do
  printf '%s  ' "$p"
  curl -s -G https://api.microlink.io/ --data-urlencode "url=https://moroccofanguide.com$p?nc=$RANDOM" \
    --data-urlencode "function=$F" -d meta=false \
    | python3 -I -c 'import json,sys;d=json.load(sys.stdin);f=d.get("data",{}).get("function",{});print(f["value"] if f.get("isFulfilled") else d.get("message") or f.get("value"))'
done
