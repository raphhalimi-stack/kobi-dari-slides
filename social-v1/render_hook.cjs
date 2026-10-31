const {chromium}=require('playwright');const path=require('path');const fs=require('fs');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
const u='file://'+path.resolve(__dirname,'formats.html');
for(const f of process.argv.slice(2)){fs.mkdirSync(`/tmp/hook_${f}`,{recursive:true});
 for(let i=0;i<75;i++){await p.goto(`${u}?f=${f}&s=0&t=${(i/60).toFixed(3)}`);await p.screenshot({path:`/tmp/hook_${f}/${String(i).padStart(3,'0')}.png`});}}
await b.close();})();
