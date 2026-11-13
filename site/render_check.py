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
        'print(n+" people rendered, plus index and methodology; "+S.filter(elect).length+" senators-elect, "'
        '+S.filter(s=>(STATUS[s.id]||{}).kind==="lame duck").length+" lame ducks");')
script = re.search(r"(?s)<script>(.*)</script>", open(sys.argv[1]).read()).group(1)
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
    f.write(STUBS + script + TAIL)
sys.exit(subprocess.run([JSC, f.name]).returncode)
