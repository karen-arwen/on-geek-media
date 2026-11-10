# Publicador na nuvem: python3 cloud_publish.py <manifest_url>   (token em IG_TOKEN)
import sys, os, json, time, urllib.request, urllib.parse
B='https://graph.facebook.com/v21.0'; IG='17841445062125900'; T=os.environ['IG_TOKEN']
def req(url, data=None):
    if data is not None: data=urllib.parse.urlencode(data).encode()
    for i in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=120))
        except urllib.error.HTTPError as e:
            body=e.read().decode()[:400]
            if e.code<500: sys.exit(f'ERRO {e.code}: {body}')
        except Exception as e: print('retry',e)
        time.sleep(10)
    sys.exit('ERRO: rede')
def wait(cid):
    for _ in range(40):
        s=req(f'{B}/{cid}?fields=status_code&access_token={T}')['status_code']
        if s=='FINISHED': return
        if s=='ERROR': sys.exit('ERRO processando midia')
        time.sleep(4)
m=json.load(urllib.request.urlopen(sys.argv[1]+'?t='+str(time.time())))
# idempotência: não repete se já existe post com o mesmo início de legenda nas últimas 24h
if m['tipo']!='story':
    recent=req(f"{B}/{IG}/media?fields=caption,timestamp&limit=5&access_token={T}")['data']
    if any((x.get('caption') or '')[:60]==m['legenda'][:60] for x in recent): print('JA PUBLICADO'); sys.exit()
U=m['urls']
if m['tipo']=='story': cid=req(f'{B}/{IG}/media',{'image_url':U[0],'media_type':'STORIES','access_token':T})['id']
elif len(U)==1: cid=req(f'{B}/{IG}/media',{'image_url':U[0],'caption':m['legenda'],'access_token':T})['id']
else:
    kids=[req(f'{B}/{IG}/media',{'image_url':u,'is_carousel_item':'true','access_token':T})['id'] for u in U]
    for k in kids: wait(k)
    cid=req(f'{B}/{IG}/media',{'media_type':'CAROUSEL','children':','.join(kids),'caption':m['legenda'],'access_token':T})['id']
wait(cid); pid=req(f'{B}/{IG}/media_publish',{'creation_id':cid,'access_token':T})['id']
print('PUBLICADO', req(f'{B}/{pid}?fields=permalink&access_token={T}').get('permalink',pid))
