// Verify the cross-category topic without treating it as a sixth primary category.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..'),qa=path.join(__dirname,'qa');
fs.mkdirSync(qa,{recursive:true});
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'catalog.json'),'utf8'));
const topic=cfg.documents.find(d=>d.id==='joint_motor');
const url=pathToFileURL(path.join(root,'index.html')).href;
function assert(value,label){if(!value)throw Error(label)}
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.EDGE_BINARY?{executablePath:process.env.EDGE_BINARY}:{})});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1080}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);
  const entry=page.locator('#topic-joint_motor');
  assert(await entry.count()===1,'Dedicated topic entry');
  await entry.scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(qa,'motor-topic-entry.png')});
  await entry.getByRole('link',{name:'进入专题',exact:true}).click();
  const reader=page.frameLocator('#reader-frame');
  await reader.locator('#Q549').waitFor();
  assert(await reader.locator('.question').count()===topic.question_ids.length,'Topic membership');
  await page.reload();await reader.locator('#Q549').waitFor();
  await page.locator('#back-home').click();
  await entry.getByRole('link',{name:'结构与装配场景',exact:true}).click();
  await reader.locator('#chapter-m3').waitFor();
  await page.locator('#back-home').click();
  await entry.getByRole('link',{name:'公式与算例',exact:true}).click();
  await reader.locator('#chapter-m5').waitFor();
  await page.locator('#back-home').click();
  for(const [q,prefix] of [['Q549','02-'],['Q565','03-'],['Q569','04-'],['Q579','05-'],['Q585','06-']]){
   await page.locator('#search').fill(q);
   assert(await page.locator('.result').count()===1,'Deduplicated search '+q);
   assert((await page.locator('.result h3 a').getAttribute('href')).startsWith(prefix),'Primary owner '+q);
  }
  await page.goto(pathToFileURL(path.join(root,topic.file.replace('.md','.html'))).href);
  assert(await page.locator('.oral-answer').count()===60,'Oral answers');
  assert((await page.locator('body').innerText()).includes('优先掌握12题'),'Priority route');
  await page.locator('#query').fill('Q571');
  await page.locator('.question:visible summary').click();
  await page.locator('.question:visible').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(qa,'motor-assembly-desktop.png')});
  await page.setViewportSize({width:390,height:844});
  for(const q of ['Q551','Q569','Q571','Q578','Q585','Q586','Q587','Q588']){
   await page.locator('#query').fill(q);
   const question=page.locator('.question:visible');
   assert(await question.count()===1,'Topic filter '+q);
   if(await question.locator('details').getAttribute('open')===null)await question.locator('summary').click();
   assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'Mobile overflow '+q);
   assert((await question.locator('.technical-details').innerText()).length>200,'Details body '+q);
  }
  await page.locator('.question:visible').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(qa,'motor-calculation-mobile.png')});
  await page.locator('#query').fill('');
  await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));
  assert(await page.locator('.technical-details[open]').count()===60,'Topic print expansion');
  await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
  await page.goto(url);await page.locator('#topic-joint_motor').scrollIntoViewIfNeeded();
  assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'Mobile topic entry overflow');
  await page.screenshot({path:path.join(qa,'motor-topic-entry-mobile.png')});
  assert(!errors.length,errors.join(';'));
  const report={version:cfg.current_version,topicQuestions:60,newQuestions:40,entry:true,topicDeepLinkReload:true,categoryOwnership:true,mobileOverflow:false,print:true,errors};
  fs.writeFileSync(path.join(qa,'motor-topic-check.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
