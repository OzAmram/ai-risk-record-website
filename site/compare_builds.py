"""Compare each person's grade, positions and statements between two builds of the site.
    python3 compare.py old.html new.html scratch_folder"""
import re,subprocess,sys,json
JSC="/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
STUBS=('function URL(u){this.hostname=u.replace(/^https?:\\/\\//,"").split("/")[0];}var location={hash:""};var els={};'
 'var document={getElementById:i=>els[i]||(els[i]={innerHTML:"",value:"",addEventListener(){}}),addEventListener(){} };'
 'var window={scrollTo(){},addEventListener(){}};var addEventListener=()=>{};\n')
TAIL='\nprint(JSON.stringify(S.map(s=>({id:s.id,name:s.name,grade:s.grade,pos:Object.fromEntries(Object.entries(s.pos).map(([k,v])=>[k,v[0]])),q:candidates(s).map(c=>c.quote),shown:statements(s).map(c=>c.quote)}))));'
def load(path):
    html=open(path).read(); src=max(re.findall(r"<script>(.*?)</script>",html,re.S),key=len)
    f=sys.argv[3]+"/tmp.js"; open(f,"w").write(STUBS+src+TAIL)
    out=subprocess.run([JSC,f],capture_output=True,text=True)
    if out.returncode: raise SystemExit(out.stderr[:500])
    return {x["id"]:x for x in json.loads(out.stdout.strip().split("\n")[-1])}
a,b=load(sys.argv[1]),load(sys.argv[2]); ch=0
for i,s in b.items():
    o=a.get(i)
    if not o: print("NEW",s["name"]); continue
    d=[]
    if o["grade"]!=s["grade"]: d.append(f"grade {o['grade']}->{s['grade']}")
    d+=[f"{k} {o['pos'].get(k)}->{v}" for k,v in s["pos"].items() if o["pos"].get(k)!=v]
    n=len([q for q in s["q"] if q not in o["q"]]); m=len([q for q in s["shown"] if q not in o["shown"]])
    if n: d.append(f"+{n} statements ({m} shown)")
    if d: ch+=1; print(s["name"]+": "+"; ".join(d))
print(ch,"people changed")
