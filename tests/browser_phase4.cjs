const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const { setTimeout: sleep } = require("node:timers/promises");
const { withBrowser, until } = require("../tools/chromium.cjs");

const [executable, dangerUrl, dayUrl, proof] = process.argv.slice(2);

async function test({call, evaluate, errors}) {
  async function wait(condition, description, timeout) {
    try { return await until(() => evaluate(condition), timeout); }
    catch (error) {
      const state = await evaluate("typeof snap === 'undefined' ? null : [snap?.phase,snap?.phase_tick,snap?.ui?.screen,snap?.player?.pos,snap?.error]");
      throw new Error(description + " — " + JSON.stringify(state) + ": " + error.message);
    }
  }

  async function mouse(action) {
    const selector = '[data-action="' + action + '"]';
    const loc = await evaluate(
      "(() => { const element = document.querySelector(" + JSON.stringify("dialog[open] " + selector) +
      ") || document.querySelector(" + JSON.stringify(selector) +
      "); if (!element || element.disabled || element.hidden) return null;" +
      "element.scrollIntoView({block:'nearest'}); const b=element.getBoundingClientRect(); return {x:b.x+b.width/2,y:b.y+b.height/2}; })()");
    assert.ok(loc, "missing enabled button " + action);
    await call("Input.dispatchMouseEvent", {type:"mousePressed", button:"left", clickCount:1, ...loc});
    await call("Input.dispatchMouseEvent", {type:"mouseReleased", button:"left", clickCount:1, ...loc});
  }

  async function key(key, pressed) {
    const code = { " ":"Space", Escape:"Escape" }[key] || "Key" + key.toUpperCase();
    const virtual = {" ":32, Escape:27}[key] || key.toUpperCase().charCodeAt(0);
    await call("Input.dispatchKeyEvent", {type:pressed?"rawKeyDown":"keyUp", key, code, windowsVirtualKeyCode:virtual});
  }
  async function press(keyName) {
    await key(keyName, true);
    await sleep(45);
    await key(keyName, false);
  }
  async function move(keyName, condition) {
    await key(keyName, true);
    try { await wait(condition, "move " + keyName, 6000); }
    finally { await key(keyName, false); }
  }
  async function screen(name) {
    const result = await call("Page.captureScreenshot", {format:"png"});
    await fs.writeFile(path.join(proof, name + ".png"), Buffer.from(result.data, "base64"));
  }
  async function open(url) {
    const result = await call("Page.navigate", {url});
    assert.equal(result.errorText, undefined);
    await wait("typeof snap !== 'undefined' && snap && document.querySelector('[data-action=start]:enabled')", "menu");
    assert.ok(await evaluate("innerWidth === 1280 && innerHeight === 720 && typeof Pixel.river === 'function'"));
  }

  await fs.mkdir(proof, {recursive:true});
  await open(dangerUrl);
  await mouse("contrast");
  await wait("document.documentElement.dataset.contrast==='high'", "high contrast menu");
  await mouse("start");
  await wait("!document.querySelector('#warnings').hidden && document.querySelector('#warnings').children.length===2", "diving alerts");
  const riverAlerts = await evaluate("Array.from(document.querySelector('#warnings').children, n => n.textContent)");
  assert.match(riverAlerts[0], /Thủy quái/);
  assert.match(riverAlerts[1], /Oxy sắp hết/);
  assert.equal(await evaluate("document.documentElement.dataset.contrast"), "high");
  await screen("gather-contrast");

  await open(dayUrl);
  await screen("menu");
  await mouse("start");
  await wait("snap.ui.screen==='day_intro' && document.querySelector('#dialog-title')?.textContent.includes('Má Tư')", "day intro");
  await mouse("next");
  await wait("!dialog.open && snap.phase==='gather'", "play gather");
  await press("Escape");
  await wait("document.querySelector('#dialog-title')?.textContent==='Tạm dừng'", "pause");
  const pausedTick = await evaluate("snap.phase_tick");
  await sleep(230);
  assert.equal(await evaluate("snap.phase_tick"), pausedTick);
  await mouse("pause");
  await wait("!dialog.open", "resume");
  await press(" ");
  await wait("snap.hold.some(i=>i.id==='I1' && i.kind==='ca_loc')", "catch fish");
  await move("w", "snap.player.at_surface");
  await move("a", "snap.player.pos[0]<4.7");
  await press("e");
  await wait("snap.ui.screen==='evening_intro' && document.querySelector('#dialog-title')?.textContent.includes('nhà bè')", "dock and handoff");
  assert.ok(await evaluate("snap.stock.length===1 && snap.stock[0].id==='I1' && snap.stock[0].fresh<100"));
  await press("c");
  assert.equal(await evaluate("document.documentElement.dataset.contrast"), "high");
  await mouse("next");
  await wait("!dialog.open && document.querySelector('#warnings').textContent.includes('Khách sắp giận')", "customer alert");
  await screen("quan-contrast");
  await press("c");
  await press("e");
  await wait("snap.stoves[0].state==='cooking' && document.querySelector('#hud').textContent.includes('Đang nấu')", "cook using stock");
  await screen("quan");
  await wait("snap.stoves[0].state==='ready'", "food ready", 9000);
  await press("e");
  await wait("snap.hand?.dish_id==='ca_loc_nuong_trui'", "pick up food");
  await move("d", "snap.player.pos[0]>=8.8");
  await move("s", "snap.player.pos[1]<=2.8");
  await press("e");
  await wait("snap.customers[0]?.state==='eating'", "serve at T1");
  await wait("snap.ui.screen==='day_result' && document.querySelector('#dialog-title')?.textContent==='Kết quả ngày'", "day result", 12000);
  const result = await evaluate("snap.ui.result");
  assert.equal(result.served, 1);
  assert.equal(result.left, 0);
  assert.ok(result.shift_earned > 0);
  await mouse("next");
  await wait("document.querySelector('#dialog-title')?.textContent==='Shop cuối ngày'", "Shop");
  await mouse("buy:oxygen");
  await wait("snap.upgrades.oxygen===1 && !snap.active_upgrades.oxygen", "upgrade pending");
  await screen("shop");
  await mouse("close-shop");
  await wait("snap.finished && snap.reason==='days_complete' && document.querySelector('#dialog-title')?.textContent==='Tổng kết chợ nổi'", "day summary");
  await call("Emulation.setDeviceMetricsOverride", {width:390,height:844,deviceScaleFactor:1,mobile:true});
  assert.ok(await evaluate("document.documentElement.scrollWidth<=innerWidth && dialog.getBoundingClientRect().width<=innerWidth"));
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({
    chromium: await evaluate("navigator.userAgent"),
    riverAlerts, customerAlert:"T1 · Khách sắp giận!",
    result, oxygen:1, reason:"days_complete",
    checked:["1280x720", "menu", "pause/resume", "fish catch", "same item in stock", "cook/serve", "result",
      "Shop buy/close", "summary", "390x844 layout", "no JavaScript exceptions"],
  }, null, 2));
}

withBrowser(executable, {}, test).catch(error => { console.error(error); process.exitCode = 1; });
