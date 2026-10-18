import sys, os
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")

CSS = """<style>
.taxi-check{border:1px solid var(--line);border-top:3px solid var(--accent);background:var(--paper);padding:18px 20px;margin:30px 0}
.taxi-check h3{margin:0 0 4px}
.taxi-check .tc-intro{margin:0 0 14px;color:var(--muted);font-size:.95rem}
.taxi-check fieldset{border:0;padding:0;margin:0 0 14px}
.taxi-check legend{font-weight:600;color:var(--ink);margin-bottom:6px;font-size:.95rem}
.taxi-check .tc-opts{display:flex;flex-wrap:wrap;gap:8px}
.taxi-check .tc-opts label{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);padding:8px 12px;cursor:pointer;font-size:.95rem;line-height:1.3;background:var(--sand)}
.taxi-check .tc-opts input{accent-color:var(--accent);margin:0}
.taxi-check .tc-opts label:has(input:checked){border-color:var(--accent);background:#fff}
.taxi-check .tc-price{display:flex;align-items:center;gap:8px}
.taxi-check .tc-price input{width:120px;font:inherit;padding:8px 10px;border:1px solid var(--line)}
.taxi-check .tc-out{margin-top:6px;padding:14px 16px;background:var(--sand);border-left:4px solid var(--muted)}
.taxi-check .tc-out p{margin:0}
.taxi-check .tc-out .tc-verdict{font-weight:700;color:var(--ink);margin-bottom:4px}
.taxi-check .tc-out.ok{border-left-color:#2e7d4f}
.taxi-check .tc-out.warn{border-left-color:#b7791f}
.taxi-check .tc-out.bad{border-left-color:#b3261e}
.taxi-check .tc-foot{margin:10px 0 0;font-size:.8rem;color:var(--muted)}
</style>"""

T = {
 "fr": dict(
  title="Ce prix de taxi est-il normal ?",
  intro="Répondez à trois questions et entrez le prix affiché ou annoncé : on vous dit s'il correspond aux repères d'un habitant.",
  meter="Le compteur est-il allumé ?", yes="Oui", no="Non, le chauffeur annonce un prix",
  when="Quand ?", day="Journée", night="Soir ou nuit",
  trip="Quel trajet ?", t1="Trajet habituel en ville (ex. gare → Al Massira)", t2="Long trajet, environ 4 km", t3="Très long trajet, plus de 8 km",
  price="Prix affiché ou demandé", unit="DH",
  nometer="Arnaque probable", nometer_t="Un petit taxi roule exclusivement au compteur. Demandez qu'il l'allume, sinon descendez et prenez le suivant.",
  expect="Repère", upto="jusqu'à {a} DH environ", range="{a} à {b} DH environ", over="{a} DH et plus",
  ok="Prix normal", ok_t="Ce montant correspond aux repères locaux.",
  warn="Un peu élevé", warn_t="Légèrement au-dessus des repères. Vérifiez que le compteur tourne depuis le départ et qu'il est sur le bon tarif.",
  bad="Anormalement élevé", bad_t="Bien au-dessus des repères locaux. Vérifiez le compteur et la vignette des tarifs, et n'hésitez pas à contester.",
  long_ok="Plausible", long_ok_t="Sur un trajet de plus de 8 km, un montant élevé est normal. L'essentiel est que le compteur tourne depuis le départ.",
  night_note=" (tarif de nuit +50 % inclus)",
  enter="Entrez un prix pour obtenir un avis.",
  foot="Outil indicatif fondé sur les repères d'un habitant à Marrakech. Le compteur fait foi, et les tarifs varient selon les villes.",
 ),
 "en": dict(
  title="Is this taxi fare normal?",
  intro="Answer three questions and enter the fare shown or quoted: we tell you whether it matches a local's benchmarks.",
  meter="Is the meter on?", yes="Yes", no="No, the driver quotes a price",
  when="When?", day="Daytime", night="Evening or night",
  trip="What kind of trip?", t1="Usual trip in town (e.g. station → Al Massira)", t2="Long trip, about 4 km", t3="Very long trip, over 8 km",
  price="Fare shown or quoted", unit="DH",
  nometer="Likely scam", nometer_t="A petit taxi runs on the meter only. Ask the driver to switch it on, or get out and take the next one.",
  expect="Benchmark", upto="up to about {a} DH", range="about {a} to {b} DH", over="{a} DH or more",
  ok="Normal fare", ok_t="This amount matches local benchmarks.",
  warn="A bit high", warn_t="Slightly above the benchmarks. Check that the meter has been running since the start and is on the right rate.",
  bad="Abnormally high", bad_t="Well above local benchmarks. Check the meter and the fare card, and don't hesitate to dispute it.",
  long_ok="Plausible", long_ok_t="On a trip of over 8 km, a higher fare is normal. What matters is that the meter has been running since the start.",
  night_note=" (50% night rate included)",
  enter="Enter a fare to get a verdict.",
  foot="Indicative tool based on a local's benchmarks in Marrakech. The meter is what counts, and fares vary between cities.",
 ),
}

JS = r"""<script>
(function(){
  var root=document.getElementById('tc-%(lang)s'); if(!root) return;
  var L=%(labels)s;
  var out=root.querySelector('.tc-out'), price=root.querySelector('input[name=tc-price]');
  function val(n){var e=root.querySelector('input[name='+n+']:checked');return e?e.value:null;}
  function fmt(s,o){return s.replace(/\{(\w)\}/g,function(_,k){return o[k];});}
  function r(n){return Math.round(n);}
  function show(cls,head,text){
    out.className='tc-out'+(cls?' '+cls:'');
    out.innerHTML='';
    var p1=document.createElement('p');p1.className='tc-verdict';p1.textContent=head;
    var p2=document.createElement('p');p2.textContent=text;
    out.appendChild(p1);out.appendChild(p2);
  }
  function update(){
    var m=val('tc-meter'),w=val('tc-when'),t=val('tc-trip');
    var k=(w==='night')?1.5:1, nn=(w==='night')?L.night_note:'';
    if(m==='no'){show('bad',L.nometer,L.nometer_t);return;}
    var exp;
    if(t==='t1') exp=fmt(L.upto,{a:r(20*k)});
    else if(t==='t2') exp=fmt(L.range,{a:r(20*k),b:r(30*k)});
    else exp=fmt(L.over,{a:r(30*k)});
    exp=L.expect+' : '+exp+nn+'.';
    if(document.documentElement.lang==='en') exp=exp.replace(' : ',': ');
    var v=parseFloat(String(price.value).replace(',','.'));
    if(!(v>0)){show('',exp,L.enter);return;}
    if(t==='t3'){show('ok',L.long_ok,L.long_ok_t+' '+exp);return;}
    var cap=(t==='t1'?20:30)*k;
    if(v<=cap) show('ok',L.ok,L.ok_t+' '+exp);
    else if(v<=cap*1.3) show('warn',L.warn,L.warn_t+' '+exp);
    else show('bad',L.bad,L.bad_t+' '+exp);
  }
  root.addEventListener('change',update);
  price.addEventListener('input',update);
  update();
})();
</script>"""

def block(lang):
    t = T[lang]
    def opt(name, value, label, checked=False):
        return f'<label><input type="radio" name="{name}" value="{value}"{" checked" if checked else ""}> {label}</label>'
    import json
    labels = json.dumps({k: t[k] for k in ("nometer","nometer_t","expect","upto","range","over","ok","ok_t","warn","warn_t","bad","bad_t","long_ok","long_ok_t","night_note","enter")}, ensure_ascii=False)
    html = (CSS + "\n"
      f'<aside class="taxi-check" id="tc-{lang}" aria-labelledby="tc-title-{lang}">\n'
      f'  <h3 id="tc-title-{lang}">{t["title"]}</h3>\n'
      f'  <p class="tc-intro">{t["intro"]}</p>\n'
      f'  <fieldset><legend>{t["meter"]}</legend><div class="tc-opts">{opt("tc-meter","yes",t["yes"],True)}{opt("tc-meter","no",t["no"])}</div></fieldset>\n'
      f'  <fieldset><legend>{t["when"]}</legend><div class="tc-opts">{opt("tc-when","day",t["day"],True)}{opt("tc-when","night",t["night"])}</div></fieldset>\n'
      f'  <fieldset><legend>{t["trip"]}</legend><div class="tc-opts">{opt("tc-trip","t1",t["t1"],True)}{opt("tc-trip","t2",t["t2"])}{opt("tc-trip","t3",t["t3"])}</div></fieldset>\n'
      f'  <fieldset><legend><label for="tc-price-{lang}">{t["price"]}</label></legend><div class="tc-price"><input id="tc-price-{lang}" name="tc-price" type="number" inputmode="decimal" min="0" step="1" placeholder="25"> {t["unit"]}</div></fieldset>\n'
      f'  <div class="tc-out" role="status" aria-live="polite"></div>\n'
      f'  <p class="tc-foot">{t["foot"]}</p>\n'
      f'</aside>\n' + (JS % {"lang": lang, "labels": labels}))
    return html

for lang in ("fr", "en"):
    open(os.path.join(HERE, f"tool_{lang}.html"), "w", encoding="utf-8").write(block(lang))
print("ok")
