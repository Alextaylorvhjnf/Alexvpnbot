import re
import asyncio
import aiohttp
import json
import base64
import logging
import time
import random
from urllib.parse import unquote

logger = logging.getLogger(__name__)

SPEED_TEST_FILES = [
    "https://speed.cloudflare.com/__down?bytes=500000",
    "https://speed.cloudflare.com/__down?bytes=2000000",
    "https://speed.cloudflare.com/__down?bytes=5000000",
    "http://speedtest.tele2.net/1MB.zip",
    "http://speedtest.tele2.net/5MB.zip",
    "https://speed.hetzner.de/1MB.bin",
    "https://speed.hetzner.de/10MB.bin",
]

UPLOAD_TEST_URLS = ["https://httpbin.org/post"]

def get_speed_emoji(latency_ms):
    if latency_ms < 80: return "🟢"
    elif latency_ms < 150: return "🟢"
    elif latency_ms < 250: return "🟡"
    elif latency_ms < 400: return "🟠"
    elif latency_ms < 700: return "🔴"
    else: return "⚫"

def get_speed_label(latency_ms):
    if latency_ms < 80: return "عالی"
    elif latency_ms < 150: return "خیلی خوب"
    elif latency_ms < 250: return "خوب"
    elif latency_ms < 400: return "معمولی"
    elif latency_ms < 700: return "کند"
    else: return "خیلی کند"

class ConfigTester:
    @staticmethod
    def extract_info(config_text):
        info = {"type": "unknown", "server": "", "port": "", "protocol": "", "valid": False, "name": ""}
        if config_text.startswith("vless://"): info["type"]="VLESS"; info["protocol"]="vless"
        elif config_text.startswith("vmess://"): info["type"]="VMess"; info["protocol"]="vmess"
        elif config_text.startswith("trojan://"): info["type"]="Trojan"; info["protocol"]="trojan"
        elif config_text.startswith("ss://"): info["type"]="Shadowsocks"; info["protocol"]="ss"
        elif "://" in config_text and ("sub" in config_text.lower() or "subscribe" in config_text.lower()):
            info["type"]="Subscription Link"; info["protocol"]="subscription"; info["valid"]=True; return info
        try:
            if "#" in config_text:
                try: info["name"]=unquote(config_text.split("#")[-1])[:35]
                except: info["name"]=config_text.split("#")[-1][:35]
            match=re.search(r'@([^:/]+):(\d+)', config_text)
            if match: info["server"]=match.group(1); info["port"]=match.group(2); info["valid"]=True
        except: pass
        return info

    @staticmethod
    async def real_tcp_ping(host, port=443, timeout=5):
        result={"reachable":False,"latency_ms":0,"error":""}
        if not host: return result
        try:
            start=time.perf_counter()
            reader,writer=await asyncio.wait_for(asyncio.open_connection(host,port),timeout=timeout)
            result["latency_ms"]=round((time.perf_counter()-start)*1000,1)
            writer.close(); await writer.wait_closed()
            result["reachable"]=True
        except asyncio.TimeoutError: result["error"]="Timeout"
        except ConnectionRefusedError: result["error"]="Refused"
        except Exception as e: result["error"]=str(e)[:20]
        return result

    @staticmethod
    async def real_speed_test(timeout=15):
        result={"download_mb":0,"upload_mb":0,"download_size_mb":0,"upload_size_kb":0,"latency_ms":0}
        dl_speeds=[]; total_dl=0; total_dl_time=0
        test_files=random.sample(SPEED_TEST_FILES,min(3,len(SPEED_TEST_FILES)))
        for url in test_files:
            try:
                start=time.perf_counter()
                connector=aiohttp.TCPConnector(force_close=True)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.get(url,timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                        data=b""
                        async for chunk in resp.content.iter_chunked(65536):
                            data+=chunk
                            if len(data)>10000000: break
                        elapsed=time.perf_counter()-start
                        if elapsed>0.1 and len(data)>10000:
                            mb=len(data)/1000000
                            speed=mb/elapsed  # MB/s
                            dl_speeds.append(speed)
                            total_dl+=len(data); total_dl_time+=elapsed
            except: continue
        if dl_speeds:
            result["download_mb"]=round(max(dl_speeds),1)
            result["download_size_mb"]=round(total_dl/1000000,1)
        for url in UPLOAD_TEST_URLS[:1]:
            try:
                test_data=b"X"*262144
                start=time.perf_counter()
                connector=aiohttp.TCPConnector(force_close=True)
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(url,data=test_data,timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        await resp.read()
                        elapsed=time.perf_counter()-start
                        if elapsed>0:
                            mb=len(test_data)/1000000
                            result["upload_mb"]=round(mb/elapsed,1)
                            result["upload_size_kb"]=256
            except: continue
        try:
            start=time.perf_counter()
            connector=aiohttp.TCPConnector(force_close=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get("https://cloudflare.com/cdn-cgi/trace",timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    await resp.text()
                    result["latency_ms"]=round((time.perf_counter()-start)*1000,1)
        except: pass
        return result

    @staticmethod
    async def fetch_subscription(sub_url, timeout=15):
        result={"reachable":False,"configs_count":0,"configs":[],"response_time_ms":0,"error":""}
        if not sub_url or "://" not in sub_url: result["error"]="لینک نامعتبر"; return result
        try:
            start=time.time()
            connector=aiohttp.TCPConnector(force_close=True,ssl=False)
            async with aiohttp.ClientSession(connector=connector) as session:
                headers={"User-Agent":"V2rayN/6.0"}
                async with session.get(sub_url,headers=headers,timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    result["response_time_ms"]=round((time.time()-start)*1000,1)
                    content=await resp.text(); result["reachable"]=True
                    configs=[]
                    if "://" in content:
                        for line in content.split('\n'):
                            line=line.strip()
                            if line and '://' in line:
                                info=ConfigTester.extract_info(line)
                                if info["valid"]: configs.append(info)
                    if not configs:
                        try:
                            decoded=base64.b64decode(content).decode('utf-8',errors='ignore')
                            for line in decoded.split('\n'):
                                line=line.strip()
                                if line and '://' in line:
                                    info=ConfigTester.extract_info(line)
                                    if info["valid"]: configs.append(info)
                        except: pass
                    result["configs"]=configs; result["configs_count"]=len(configs)
        except Exception as e: result["error"]=str(e)[:50]
        return result

    @staticmethod
    async def test_subscription(sub_url):
        result=await ConfigTester.fetch_subscription(sub_url)
        text="🔗 **تست لینک اشتراک**\n\n"
        text+=f"🔗 `{sub_url[:45]}...`\n"
        text+=f"⏱️ پاسخ: `{result['response_time_ms']}ms` | 📦 `{result['configs_count']}` سرور\n\n"
        text+="━"*30+"\n\n"
        if not result["reachable"]: text+=f"❌ **خطا:** {result['error']}\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"; return text
        if result["configs_count"]==0: text+="⚠️ کانفیگی پیدا نشد!\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"; return text
        
        text+="📡 **پینگ سرورها:**\n\n"
        all_pings=[]
        for i,cfg in enumerate(result["configs"],1):
            name=cfg.get("name",f"سرور {i}")[:28]; server=cfg["server"]; port=int(cfg.get("port",443))
            ping=await ConfigTester.real_tcp_ping(server,port,timeout=5)
            if ping["reachable"]:
                emoji=get_speed_emoji(ping['latency_ms']); label=get_speed_label(ping['latency_ms'])
                all_pings.append(ping['latency_ms'])
                text+=f"{i:2d}. {emoji} `{name}` ⏱️ `{ping['latency_ms']}ms` ({label})\n"
            else: text+=f"{i:2d}. ⚫ `{name}` ❌\n"
        
        text+=f"\n━"*30+"\n🚀 **تست سرعت واقعی:**\n\n⏳ دانلود از CDN...\n\n"
        speed=await ConfigTester.real_speed_test(timeout=20)
        
        if speed["download_mb"]>0:
            dl_emoji="🟢" if speed["download_mb"]>5 else "🟡" if speed["download_mb"]>2 else "🟠" if speed["download_mb"]>1 else "🔴"
            text+=f"📥 **دانلود:** `{speed['download_mb']}MB/s` {dl_emoji}\n"
        if speed["upload_mb"]>0:
            ul_emoji="🟢" if speed["upload_mb"]>2 else "🟡" if speed["upload_mb"]>1 else "🟠"
            text+=f"📤 **آپلود:** `{speed['upload_mb']}MB/s` {ul_emoji}\n"
        if speed["latency_ms"]>0: text+=f"⏱️ **تأخیر:** `{speed['latency_ms']}ms`\n"
        
        text+="\n💡 **تحلیل:**\n"
        if speed["download_mb"]>5: text+="🟢 4K/8K یوتیوب، گیم آنلاین، دانلود سنگین"
        elif speed["download_mb"]>2: text+="🟢 4K یوتیوب، استریم، گیم"
        elif speed["download_mb"]>1: text+="🟡 1080p یوتیوب، وب‌گردی سریع"
        elif speed["download_mb"]>0.5: text+="🟠 720p یوتیوب، وب‌گردی"
        elif speed["download_mb"]>0.1: text+="🔴 وب‌گردی ساده"
        else: text+="⚫ خیلی کند"
        
        if all_pings:
            best_ping=min(all_pings); avg_ping=sum(all_pings)/len(all_pings)
            text+=f"\n\n📊 **پینگ:** ⚡ `{best_ping}ms` | 📊 `{avg_ping:.0f}ms` | ✅ `{len(all_pings)}`/{result['configs_count']}"
        text+="\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        return text

    @staticmethod
    async def test_config(config_text):
        info=ConfigTester.extract_info(config_text)
        if info["type"]=="Subscription Link": return await ConfigTester.test_subscription(config_text)
        if not info["valid"]: return "❌ **کانفیگ نامعتبر**\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        name=info.get("name","بی‌نام")[:30]; server=info["server"]; port=int(info.get("port",443))
        ping=await ConfigTester.real_tcp_ping(server,port)
        speed=await ConfigTester.real_speed_test(timeout=15)
        text=f"🔍 **تست کانفیگ**\n\n📋 **{info['type']}** | 🏷️ `{name}`\n🌐 `{server}:{port}`\n\n━"+"30"+"\n\n"
        if ping["reachable"]:
            text+=f"⏱️ **پینگ:** `{ping['latency_ms']}ms` {get_speed_emoji(ping['latency_ms'])}\n"
        if speed["download_mb"]>0: text+=f"📥 **دانلود:** `{speed['download_mb']}MB/s`\n"
        if speed["upload_mb"]>0: text+=f"📤 **آپلود:** `{speed['upload_mb']}MB/s`\n"
        text+="\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        return text

    @staticmethod
    async def speed_test():
        text="🚀 **تست سرعت واقعی**\n\n⏳ دانلود از CDN...\n\n"
        speed=await ConfigTester.real_speed_test(timeout=20)
        if speed["download_mb"]>0: text+=f"📥 **دانلود:** `{speed['download_mb']}MB/s`\n"
        if speed["upload_mb"]>0: text+=f"📤 **آپلود:** `{speed['upload_mb']}MB/s`\n"
        if speed["latency_ms"]>0: text+=f"⏱️ **تأخیر:** `{speed['latency_ms']}ms`\n"
        text+="\n💡 "
        if speed["download_mb"]>5: text+="4K یوتیوب و گیم"
        elif speed["download_mb"]>2: text+="1080p یوتیوب"
        elif speed["download_mb"]>1: text+="720p یوتیوب"
        else: text+="وب‌گردی"
        text+="\n\n🛍️ @Alexvpn98bot | 🆘 @Alexvpnsupport"
        return text
