const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { setTimeout: sleep } = require("node:timers/promises");

async function until(check, timeout = 10000) {
  const end = Date.now() + timeout;
  while (Date.now() < end) {
    const value = await check();
    if (value) return value;
    await sleep(20);
  }
  throw new Error("Timed out waiting for Chromium");
}

// Always launch a disposable instance on loopback. Never attach to a user's browser.
async function withBrowser(executable, { headed = false } = {}, task) {
  const profile = await fs.mkdtemp(path.join(os.tmpdir(), "chonoi-browser-"));
  const args = [
    ...(headed ? [] : ["--headless=new"]),
    "--disable-gpu", "--disable-background-networking", "--no-first-run", "--no-default-browser-check",
    "--remote-debugging-port=0", "--remote-debugging-address=127.0.0.1",
    "--window-size=1280,800", "--user-data-dir=" + profile, "about:blank",
  ];
  const browser = spawn(executable, args, { stdio: "ignore", windowsHide: !headed });
  let spawnError, socket;
  browser.once("error", error => { spawnError = error; });
  const pending = new Map();
  const errors = [];
  let serial = 0;
  try {
    const port = await until(async () => {
      if (spawnError) throw spawnError;
      if (browser.exitCode !== null) throw new Error("Chromium stopped during startup");
      try { return (await fs.readFile(path.join(profile, "DevToolsActivePort"), "utf8")).split("\n")[0]; }
      catch (error) { if (error.code !== "ENOENT") throw error; }
    });
    const pages = await (await fetch("http://127.0.0.1:" + port + "/json/list")).json();
    const page = pages.find(entry => entry.type === "page");
    if (!page) throw new Error("Chromium has no test page");
    socket = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => {
      socket.addEventListener("open", resolve, { once: true });
      socket.addEventListener("error", () => reject(new Error("Chromium connection failed")), { once: true });
    });
    socket.addEventListener("message", event => {
      const message = JSON.parse(event.data);
      if (message.method === "Runtime.exceptionThrown") {
        const detail = message.params.exceptionDetails;
        errors.push(detail.exception?.description || detail.text);
      }
      const waiting = pending.get(message.id);
      if (waiting) {
        pending.delete(message.id);
        clearTimeout(waiting.timer);
        if (message.error) waiting.reject(new Error(message.error.message));
        else waiting.resolve(message.result);
      }
    });
    function call(method, params = {}) {
      return new Promise((resolve, reject) => {
        const id = ++serial;
        const timer = setTimeout(() => {
          pending.delete(id);
          reject(new Error("Timed out in " + method));
        }, 10000);
        pending.set(id, { resolve, reject, timer });
        socket.send(JSON.stringify({ id, method, params }));
      });
    }
    async function evaluate(expression) {
      const response = await call("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
      if (response.exceptionDetails) throw new Error(response.exceptionDetails.exception?.description || response.exceptionDetails.text);
      return response.result.value;
    }
    await call("Runtime.enable");
    await call("Page.enable");
    await call("Emulation.setDeviceMetricsOverride", { width: 1280, height: 720, deviceScaleFactor: 1, mobile: false });
    return await task({ call, evaluate, errors });
  } finally {
    for (const waiting of pending.values()) clearTimeout(waiting.timer);
    socket?.close();
    if (browser.pid && browser.exitCode === null) {
      browser.kill();
      await Promise.race([new Promise(resolve => browser.once("exit", resolve)), sleep(2000)]);
    }
    await fs.rm(profile, { recursive: true, force: true, maxRetries: 8, retryDelay: 80 });
  }
}

if (require.main === module) {
  const [executable, url, source, headed] = process.argv.slice(2);
  const measure = async ({call, evaluate, errors}) => {
    const navigation = await call("Page.navigate", { url });
    if (navigation.errorText) throw new Error(navigation.errorText);
    await until(() => evaluate("typeof snap !== 'undefined' && snap && snap.phase === 'gather' && document.querySelector('[data-action=start]:enabled') !== null"));
    if (!(await evaluate("innerWidth === 1280 && innerHeight === 720"))) throw new Error("Benchmark viewport must be 1280×720");
    await evaluate(source);
    await evaluate("document.querySelector('[data-action=start]').click()");
    await until(() => evaluate("window.__phase4Bench?.done"), Number(process.env.CHONOI_BENCH_TIMEOUT));
    if (errors.length) throw new Error(errors[0]);
    return evaluate("window.__phase4Bench");
  };
  withBrowser(executable, { headed: headed === "headed" }, measure)
    .then(result => process.stdout.write(JSON.stringify(result)))
    .catch(error => { console.error(error); process.exitCode = 1; });
}

module.exports = { withBrowser, until };
