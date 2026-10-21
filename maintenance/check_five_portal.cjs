const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const root=path.resolve(__dirname,'..'),qa=path.join(__dirname,'qa');
fs.mkdirSync(qa,{recursive:true});
const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'catalog.json'),'utf8'));
const categories=cfg.documents.filter(d=>d.kind==='category').sort((a,b)=>a.order-b.order);
const expectedTotal=cfg.documents.find(d=>d.id==='master').question_ids.length;
const organization=JSON.parse(fs.readFileSync(path.join(root,cfg.organization),'utf8'));
const expectedMaterials=organization.categories.find(c=>c.id==='knowledge').groups.find(g=>g.code==='T2').question_ids.length;
function assert(ok,message){if(!ok)throw Error(message)}
(async()=>{
 const browser=await chromium.launch({headless:true,...(process.env.EDGE_BINARY?{executablePath:process.env.EDGE_BINARY}:{})});
 const page=await browser.newPage({viewport:{width:1440,height:1080}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const url=pathToFileURL(path.join(root,'index.html')).href;
 await page.goto(url);
 const data=JSON.parse(await page.locator('#site-data').textContent());
 assert(await page.locator('.category-card').count()===5,'Five entry cards');
 assert(await page.locator('.category-index').count()===5,'Five dedicated indexes');
 assert(await page.locator('.subject-link').count()===4,'Four theory subjects');
 assert(data.questions.length===expectedTotal&&new Set(data.questions.map(q=>q.id)).size===expectedTotal,'Question completeness');
 await page.screenshot({path:path.join(qa,'five-sections-desktop.png')});
 await page.locator('#more').click();assert(await page.locator('.result').count()===40,'Pagination');
 for(const d of categories){
  await page.locator('#topic').selectOption(d.id);
  assert((await page.locator('#result-count').textContent()).startsWith(d.question_ids.length+' /'),'Category filter '+d.id);
  assert(await page.locator('#index-'+d.id).count()===1,'Dedicated index '+d.id);
 }
 await page.locator('#subject').selectOption({label:'材料力学'});
 assert(await page.locator('#topic').inputValue()==='knowledge','Subject selects theory');
 assert((await page.locator('#result-count').textContent()).startsWith(expectedMaterials+' /'),'Materials subject filter');
 await page.locator('#reset').click();await page.locator('#search').fill('Q347');
 assert(await page.locator('.result').count()===1,'Exact question search');
 assert((await page.locator('.result h3 a').getAttribute('href')).startsWith('03-'),'Primary category of Q347');
 await page.locator('#preview-toggle').click();assert(!await page.locator('.oral-preview').isVisible(),'Hide answers');await page.locator('#preview-toggle').click();
 await page.locator('.result h3 a').click();const frame=page.frameLocator('#reader-frame');await frame.locator('#Q347').waitFor();
 await page.reload();await frame.locator('#Q347').waitFor();
 await page.locator('#back-home').click();
 // A reload intentionally resets search controls; verify navigation preserves live controls.
 await page.locator('#search').fill('Q347');await page.locator('.result h3 a').click();await frame.locator('#Q347').waitFor();await page.locator('#back-home').click();
 assert(await page.locator('#search').inputValue()==='Q347','Reader returns to current search');
 await page.locator('#search').fill('无匹配XYZ9987');assert(await page.locator('#empty').isVisible(),'Empty state');await page.locator('#reset').click();
 await page.locator('#index-knowledge .group-index h3 a').filter({hasText:'材料力学'}).click();await frame.locator('#chapter-t2').waitFor();
 await frame.locator('#Q027').waitFor();await page.locator('#back-home').click();
 await page.locator('#index-reference').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(qa,'five-sections-reference-index.png')});
 // Old saved reader links still work, including cross-document links from unchanged answers.
 await page.goto(url+'#read='+encodeURIComponent('理论力学与消费电子刚体分析专题.html#Q303'));await frame.locator('#Q303').waitFor();
 await frame.locator('.question').filter({has:frame.locator('#Q303')}).locator('.question-links a').filter({hasText:'理论知识'}).click();
 await page.waitForFunction(()=>document.querySelector('#reader-title').textContent==='理论知识');await frame.locator('#Q303').waitFor();
 await page.setViewportSize({width:390,height:844});await page.goto(url);
 assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'Mobile portal overflow');
 await page.screenshot({path:path.join(qa,'five-sections-mobile.png')});
 const reports=[];
 for(const d of categories){
  await page.goto(pathToFileURL(path.join(root,d.file.replace('.md','.html'))).href);
  assert(await page.locator('.question').count()===d.question_ids.length,'Rendered count '+d.id);
  assert(await page.locator('.oral-answer').count()===d.question_ids.length,'Oral answers '+d.id);
  assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),'Mobile document overflow '+d.id);
  const sample=d.question_ids[0];await page.locator('#query').fill(sample);assert(await page.locator('.question:visible').count()===1,'Document exact filter '+d.id);
  await page.locator('.question:visible summary').click();assert(await page.locator('.question:visible .technical-details').getAttribute('open')!==null,'Question detail '+d.id);
  await page.locator('#query').fill('');
  const broken=await page.evaluate(()=>[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(decodeURIComponent(a.hash.slice(1)))).map(a=>a.hash));
  assert(!broken.length,'Local anchors '+d.id+': '+broken.join(','));
  await page.evaluate(()=>window.dispatchEvent(new Event('beforeprint')));assert(await page.locator('.technical-details[open]').count()===d.question_ids.length,'Print expand '+d.id);await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
  reports.push({id:d.id,questions:d.question_ids.length,mobileOverflow:false,filter:true,detail:true,print:true});
 }
 await page.setViewportSize({width:1440,height:1080});await page.goto(pathToFileURL(path.join(root,'02-理论知识.html')).href+'#chapter-t2');await page.screenshot({path:path.join(qa,'five-sections-theory.png')});
 await page.goto(pathToFileURL(path.join(root,'06-常用数据和公式汇总.html')).href+'#chapter-r2');await page.screenshot({path:path.join(qa,'five-sections-formulas.png')});
 assert(!errors.length,errors.join(';'));
 const result={version:cfg.current_version,cards:5,indexes:5,theorySubjects:4,uniqueQuestions:expectedTotal,documents:reports,legacyReaderLinks:true,deepLinkReload:true,errors};
 fs.writeFileSync(path.join(qa,'five-sections-check.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
