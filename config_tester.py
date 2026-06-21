import re, asyncio, aiohttp, json, base64, logging, time, random
from urllib.parse import unquote

logger = logging.getLogger(__name__)

SPEED_TEST_FILES = [
    "https://speed.cloudflare.com/__down?bytes=500000",
    "https://speed.cloudflare.com/__down?bytes=2000000",
    "http://speedtest.tele2.net/1MB.zip",
    "https://speed.hetzner.de/1MB.bin",
]
UPLOAD_TEST_URLS = ["https://httpbin.org/post"]

def get_speed_emoji(ms):
    if ms < 80: return "🟢"
    elif ms < 150: return "🟢"
    elif ms < 250: return "🟡"
    elif ms < 400: return "🟠"
    elif ms < 700: return "🔴"
    else: return "⚫"

def get_label(ms):
    if ms < 80: return "Excellent"
    elif ms < 150: return "Very Good"
    elif ms < 250: return "Good"
    elif ms < 400: return "Average"
    elif ms < 700: return "Slow"
    else: return "Very Slow"

class ConfigTester:
    @staticmethod
    def extract_info(text):
        info = {"type": "unknown", "server": "", "port": "", "protocol": "", "valid": False, "name": ""}
        if text.startswith("vless://"): info["type"]="VLESS"; info["protocol"]="vless"
        elif text.startswith("vmess://"): info["type"]="VMess"; info["protocol"]="vmess"
        elif text.startswith("trojan://"): info["type"]="Trojan"; info["protocol"]="trojan"
        elif text.startswith("ss://"): info["type"]="Shadowsocks"; info["protocol"]="ss"
        elif "://" in text and "sub" in text.lower(): info["type"]="Subscription Link"; info["protocol"]="subscription"; info["valid"]=True; return info
        try:
            if "#" in text:
                try: info["name"]=unquote(text.split("#")[-1])[:30]
                except: info["name"]=text.split("#")[-1][:30]
            m=re.search(r'@([^:/]+):(\d+)', text)
            if m: info["server"]=m.group(1); info["port"]=m.group(2); info["valid"]=True
        except: pass
        return info

    @staticmethod
    async def tcp_ping(host, port=443, timeout=5):
        r={"reachable":False,"latency_ms":0,"error":""}
        if not host: return r
        try:
            s=time.perf_counter()
            _,w=await asyncio.wait_for(asyncio.open_connection(host,port),timeout)
            r["latency_ms"]=round((time.perf_counter()-s)*1000,1)
            w.close(); await w.wait_closed(); r["reachable"]=True
        except asyncio.TimeoutError: r["error"]="Timeout"
        except ConnectionRefusedError: r["error"]="Refused"
        except Exception as e: r["error"]=str(e)[:20]
        return r

    @staticmethod
    async def speed_test(timeout=15):
        r={"download_mb":0,"upload_mb":0,"latency_ms":0}
        dls=[]
        for url in random.sample(SPEED_TEST_FILES,min(3,len(SPEED_TEST_FILES))):
            try:
                s=time.perf_counter()
                conn=aiohttp.TCPConnector(force_close=True)
                async with aiohttp.ClientSession(connector=conn) as ses:
                    async with ses.get(url,timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                        data=b""
                        async for c in resp.content.iter_chunked(65536):
                            data+=c
                            if len(data)>5000000: break
                        t=time.perf_counter()-s
                        if t>0.1 and len(data)>10000:
                            dls.append((len(data)/1e6)/t)
            except: continue
        if dls: r["download_mb"]=round(max(dls),1)
        for url in UPLOAD_TEST_URLS[:1]:
            try:
                td=b"X"*131072; s=time.perf_counter()
                conn=aiohttp.TCPConnector(force_close=True)
                async with aiohttp.ClientSession(connector=conn) as ses:
                    async with ses.post(url,data=td,timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        await resp.read()
                        t=time.perf_counter()-s
                        if t>0: r["upload_mb"]=round((len(td)/1e6)/t,1)
            except: continue
        try:
            s=time.perf_counter()
            conn=aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=conn) as ses:
                async with ses.get("https://cloudflare.com/cdn-cgi/trace",timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    await resp.text()
                    r["latency_ms"]=round((time.perf_counter()-s)*1000,1)
        except: pass
        return r

    @staticmethod
    async def fetch_sub(url, timeout=15):
        r={"reachable":False,"configs_count":0,"configs":[],"response_time_ms":0,"error":""}
        if "://" not in url: r["error"]="Invalid"; return r
        try:
            s=time.time()
            conn=aiohttp.TCPConnector(force_close=True,ssl=False)
            async with aiohttp.ClientSession(connector=conn) as ses:
                async with ses.get(url,headers={"User-Agent":"V2rayN/6.0"},timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    r["response_time_ms"]=round((time.time()-s)*1000,1)
                    c=await resp.text(); r["reachable"]=True
                    cfgs=[]
                    if "://" in c:
                        for l in c.split('\n'):
                            l=l.strip()
                            if l and '://' in l:
                                inf=ConfigTester.extract_info(l)
                                if inf["valid"]: cfgs.append(inf)
                    if not cfgs:
                        try:
                            dc=base64.b64decode(c).decode('utf-8',errors='ignore')
                            for l in dc.split('\n'):
                                l=l.strip()
                                if l and '://' in l:
                                    inf=ConfigTester.extract_info(l)
                                    if inf["valid"]: cfgs.append(inf)
                        except: pass
                    r["configs"]=cfgs; r["configs_count"]=len(cfgs)
        except Exception as e: r["error"]=str(e)[:50]
        return r

    @staticmethod
    async def test_subscription(sub_url):
        r=await ConfigTester.fetch_sub(sub_url)
        t="🔗 **Subscription Test (Real TCP)**\n\n"
        t+=f"🔗 `{sub_url[:50]}...`\n"
        t+=f"⏱️ Response: `{r['response_time_ms']}ms` | 📦 `{r['configs_count']}` Servers\n\n"
        t+="━"*35+"\n\n"
        if not r["reachable"]: return t+f"❌ **Error:** {r['error']}\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        if r["configs_count"]==0: return t+"⚠️ No configs found!\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        
        t+="📡 **All Servers Ping:**\n\n"
        pings=[]
        for i,cfg in enumerate(r["configs"],1):
            nm=cfg.get("name",f"Server {i}")[:25]
            srv=cfg["server"]; prt=int(cfg.get("port",443))
            p=await ConfigTester.tcp_ping(srv,prt,5)
            if p["reachable"]:
                e=get_speed_emoji(p['latency_ms']); lb=get_label(p['latency_ms'])
                pings.append(p['latency_ms'])
                t+=f"{i:2d}. {e} `{nm}`\n     ⏱️ `{p['latency_ms']}ms` ({lb})\n\n"
            else:
                t+=f"{i:2d}. ⚫ `{nm}`\n     ❌ {p['error']}\n\n"
        
        t+="━"*35+"\n"
        t+="🚀 **Real Speed Test (CDN Download):**\n\n"
        sp=await ConfigTester.speed_test(20)
        if sp["download_mb"]>0:
            de="🟢" if sp["download_mb"]>5 else "🟡" if sp["download_mb"]>2 else "🟠"
            t+=f"📥 **Download:** `{sp['download_mb']}MB/s` {de}\n"
        if sp["upload_mb"]>0:
            ue="🟢" if sp["upload_mb"]>2 else "🟡" if sp["upload_mb"]>1 else "🟠"
            t+=f"📤 **Upload:** `{sp['upload_mb']}MB/s` {ue}\n"
        if sp["latency_ms"]>0: t+=f"⏱️ **Latency:** `{sp['latency_ms']}ms`\n"
        
        t+="\n💡 **Analysis:**\n"
        if sp["download_mb"]>5: t+="🟢 4K YouTube, Gaming, Heavy Download"
        elif sp["download_mb"]>2: t+="🟡 1080p YouTube, Streaming"
        elif sp["download_mb"]>1: t+="🟠 720p YouTube, Browsing"
        else: t+="🔴 Basic Browsing"
        
        if pings:
            bp=min(pings); ap=sum(pings)/len(pings)
            t+=f"\n\n📊 **Ping Stats:** ⚡ Best: `{bp}ms` | 📊 Avg: `{ap:.0f}ms` | ✅ {len(pings)}/{r['configs_count']} Online"
        t+="\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        return t

    @staticmethod
    async def test_config(text):
        inf=ConfigTester.extract_info(text)
        if inf["type"]=="Subscription Link": return await ConfigTester.test_subscription(text)
        if not inf["valid"]: return "❌ Invalid config\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        nm=inf.get("name","Unknown")[:25]; srv=inf["server"]; prt=int(inf.get("port",443))
        p=await ConfigTester.tcp_ping(srv,prt); sp=await ConfigTester.speed_test(15)
        t=f"🔍 **Config Test**\n\n📋 **{inf['type']}** | 🏷️ `{nm}`\n🌐 `{srv}:{prt}`\n\n━"+"35"+"\n\n"
        if p["reachable"]:
            e=get_speed_emoji(p['latency_ms'])
            t+=f"⏱️ **Ping:** `{p['latency_ms']}ms` {e}\n"
        if sp["download_mb"]>0: t+=f"📥 **Download:** `{sp['download_mb']}MB/s`\n"
        if sp["upload_mb"]>0: t+=f"📤 **Upload:** `{sp['upload_mb']}MB/s`\n"
        t+="\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        return t

    @staticmethod
    async def speed_test_only():
        sp=await ConfigTester.speed_test(20)
        t="🚀 **Speed Test**\n\n"
        if sp["download_mb"]>0: t+=f"📥 Download: `{sp['download_mb']}MB/s`\n"
        if sp["upload_mb"]>0: t+=f"📤 Upload: `{sp['upload_mb']}MB/s`\n"
        if sp["latency_ms"]>0: t+=f"⏱️ Latency: `{sp['latency_ms']}ms`\n"
        t+="\n🔗 [Speedtest.net](https://www.speedtest.net)\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        return t
