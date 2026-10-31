const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
const u='file://'+path.resolve(__dirname,'formats.html');
for(const f of ['K1','K2','K3','D1','D2','D3'])for(const s of [0,1,2]){
 await p.goto(`${u}?f=${f}&s=${s}&t=1`);await p.waitForTimeout(250);
 await p.screenshot({path:`proto/${f}_${s}.png`});}
await b.close();})();
