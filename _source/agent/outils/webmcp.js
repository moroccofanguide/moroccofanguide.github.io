(function(){var mc=document.modelContext||navigator.modelContext;if(!mc||!mc.registerTool)return;
var G=__GUIDES__,ac=new AbortController();
mc.registerTool({name:"list_guides",description:"List Morocco Fan Guide travel guides (Morocco, Marrakech, taxis, prices, safety, ferries), optionally filtered by language or keyword.",
inputSchema:{type:"object",properties:{lang:{type:"string",enum:["fr","en"],description:"fr or en"},query:{type:"string",description:"Keyword to match in title, topic or description"}}},
annotations:{readOnlyHint:true},execute:async function(a){a=a||{};var q=(a.query||"").toLowerCase();
var r=G.filter(function(g){return(!a.lang||g.lang===a.lang)&&(!q||(g.title+" "+g.topic+" "+g.description).toLowerCase().indexOf(q)>=0)});
return{content:[{type:"text",text:JSON.stringify(r)}]}}},{signal:ac.signal});
mc.registerTool({name:"read_guide",description:"Read one Morocco Fan Guide page as Markdown (title, URL, update date, full text).",
inputSchema:{type:"object",properties:{url:{type:"string",description:"Page URL on moroccofanguide.com, from list_guides"}},required:["url"]},
annotations:{readOnlyHint:true},execute:async function(a){var u=new URL(a.url,location.origin);
if(u.origin!==location.origin)throw new Error("Only moroccofanguide.com pages");var p=u.pathname.replace(/[^/]*$/,"");
var r=await fetch(p+"index.md");if(!r.ok)throw new Error("Page not found");return{content:[{type:"text",text:await r.text()}]}}},{signal:ac.signal});
})();
