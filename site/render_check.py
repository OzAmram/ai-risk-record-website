"""Check that every page of the built site renders without a script error, with no browser.

Runs the page's script in macOS's built-in JavaScript engine with stand-ins for the browser,
then calls each view. It does not check how the page looks.

    python3 site/render_check.py site/index.html
"""
import re
import subprocess
import sys
import tempfile

JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc"
STUBS = ('function URL(u){this.hostname=u.replace(/^https?:\\/\\//,"").split("/")[0];}var location={hash:""};var els={};'
         'var document={getElementById:i=>els[i]||(els[i]={innerHTML:"",value:"",addEventListener(){}}),addEventListener(){} };'
         'var window={scrollTo(){},addEventListener(){}};var addEventListener=()=>{};\n')
TAIL = ('\nlet n=0;for(const s of S){const h=viewSenator(s);if(/undefined|NaN|\\[object/.test(h))throw new Error("bad text on page of "+s.id);n++;}'
        'for(const h of [viewIndex(),viewMethod()]){if(/undefined|NaN|\\[object/.test(h))throw new Error("bad text on index or methodology");}'
        'query="vermont";if(S.filter(matches).some(s=>stateOf(s)!=="Vermont"))throw new Error("search by state matched another state");'
        'if(/undefined|NaN|\\[object/.test(viewIndex()))throw new Error("bad text on filtered index");query="";'
        'const order=S.map(s=>s.name);for(const[a,b]of[["Tommy Tuberville","Chris Van Hollen"],["Chris Van Hollen","Mark Warner"],["John Cornyn","Catherine Cortez Masto"],["Catherine Cortez Masto","Tom Cotton"],["Richard Blumenthal","Lisa Blunt Rochester"],["Lisa Blunt Rochester","Cory Booker"]]){if(order.indexOf(a)<0||order.indexOf(b)<0||order.indexOf(a)>order.indexOf(b))throw new Error("not sorted by last name: "+a+" / "+b);}'
        'for(const which of["current","next"]){senate=which;const n=S.filter(inSenate).length;if(n!==100)throw new Error(which+" Senate has "+n+" members, not 100");'
        'for(const st of Object.keys(STATE_PATHS)){if(S.filter(s=>stateOf(s)===st&&inSenate(s)).length!==2)throw new Error(which+" Senate: "+st+" does not have two senators");}'
        'if(/undefined|NaN|\\[object/.test(viewIndex()))throw new Error("bad text on index for "+which+" Senate");}senate="current";'
        'query="x";if(viewIndex().includes("class=\\"map\\""))throw new Error("map still shown while searching");query="";'
        'const nh=S.filter(house).length;if(nh){chamber="house";const h=viewIndex();if(/undefined|NaN|\\[object/.test(h))throw new Error("bad text on House index");if(h.includes("class=\\"map\\""))throw new Error("map shown on House index");'
        'if(S.filter(s=>!house(s)).some(s=>h.includes("#"+s.id+"\\"")))throw new Error("a senator is listed on the House index");chamber="senate";'
        'if(S.filter(house).some(s=>viewIndex().includes("#"+s.id+"\\"")))throw new Error("a representative is listed on the Senate index");}'
        'for(const ch of["senate","house"]){chamber=ch;for(const which of["current","next"]){senate=which;const people=S.filter(ch==="house"?inHouse:inSenate);'
        'for(const f of FIELDS){policy=f[0];const h=viewPolicyHist();if(/undefined|NaN|\\[object/.test(h))throw new Error("bad text on policy chart");'
        'const nums=[...h.matchAll(/class="n">(\\d+)</g)].map(m=>+m[1]);if(nums.length!==4||nums.reduce((a,b)=>a+b,0)!==people.length)throw new Error("policy chart bars do not add up to the members for "+ch+" "+which+" "+f[0]);}}}'
        'chamber="senate";senate="current";policy="slow";if(!viewIndex().includes("data-policy"))throw new Error("policy chart missing from index");'
        'for(const[z,st,nrep]of[["10001","New York",1],["99501","Alaska",1],["05401","Vermont",1],["90210","California",2]]){query=z;const got=S.filter(matches);'
        'if(got.some(s=>stateOf(s)!==st))throw new Error("zip "+z+" matched someone outside "+st);if(got.filter(s=>!house(s)&&!elect(s)).length!==2)throw new Error("zip "+z+" did not list two sitting senators");'
        'if(got.filter(house).length!==nrep)throw new Error("zip "+z+" listed "+got.filter(house).length+" representatives, expected "+nrep);if(got.some(s=>house(s)&&elect(s)))throw new Error("zip "+z+" listed a representative-elect");'
        'const h=viewIndex();if(/undefined|NaN|\\[object/.test(h))throw new Error("bad text on zip result");if(h.includes("data-policy")||h.includes("class=\\"map\\""))throw new Error("charts shown on zip result");}'
        'query="00000";if(S.filter(matches).length||!viewIndex().includes("was not found"))throw new Error("unknown zip code not handled");query="";'
        'if(S.length-nh!==117)throw new Error("Senate side no longer has 117 people");'
        'print(nh+" House records; "+(n-nh)+" Senate-side records");'
        'const sen=S.filter(s=>!house(s)),hou=S.filter(house);'
        'print(n+" people rendered, plus index and methodology; Senate: "+sen.filter(elect).length+" senators-elect, "+sen.filter(lame).length+" lame ducks; House: "'
        '+hou.filter(elect).length+" representatives-elect, "+hou.filter(lame).length+" lame ducks");')
script = re.search(r"(?s)<script>(.*)</script>", open(sys.argv[1]).read()).group(1)
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
    f.write(STUBS + script + TAIL)
sys.exit(subprocess.run([JSC, f.name]).returncode)
