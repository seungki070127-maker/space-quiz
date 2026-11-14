// 사용법: node .claude/skills/game-playtest/smoke.cjs [index.html 경로] [스크린샷 폴더]
// 페이지를 열어 콘솔 에러를 모으고, 버튼을 계속 눌러 끝까지 진행한 뒤 데스크톱/모바일 스크린샷을 남긴다.
const { chromium } = require("playwright");
const { pathToFileURL } = require("node:url");
const path = require("node:path");

(async () => {

const file = path.resolve(process.argv[2] ?? "index.html");
const out = path.resolve(process.argv[3] ?? ".");
const url = pathToFileURL(file).href;
const errors = [];
const browser = await chromium.launch();

async function run(name, ctxOpts) {
  const page = await (await browser.newContext(ctxOpts)).newPage();
  page.on("pageerror", e => errors.push(`[${name}] ${e.message}`));
  page.on("console", m => m.type() === "error" && errors.push(`[${name}] console: ${m.text()}`));
  await page.goto(url);
  await page.screenshot({ path: path.join(out, `${name}-start.png`) });

  // 클릭 가능한 버튼을 차례로 눌러 진행 (최대 60회). 게임 전용 흐름은 SKILL.md 참고해 직접 작성.
  for (let n = 0; n < 60; n++) {
    const btn = page.locator("button:visible:enabled").first();
    if (!(await btn.count())) break;
    const label = (await btn.textContent())?.trim();
    if (/다시|재시작|restart/i.test(label ?? "")) { console.log(`[${name}] 결과 화면 도달 (${n}회 클릭)`); break; }
    await btn.click();
    await page.waitForTimeout(80);
  }
  await page.waitForTimeout(700); // 등장 애니메이션 끝난 뒤 촬영
  await page.screenshot({ path: path.join(out, `${name}-end.png`) });

  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  if (overflow) errors.push(`[${name}] 가로 스크롤 발생`);
}

await run("desktop", { viewport: { width: 1280, height: 800 } });
await run("mobile", { viewport: { width: 360, height: 740 }, isMobile: true, hasTouch: true });
await run("dark-reduced", { viewport: { width: 1280, height: 800 }, colorScheme: "dark", reducedMotion: "reduce" });
await browser.close();

if (errors.length) { console.error("❌ 문제 발견:\n" + errors.join("\n")); process.exit(1); }
console.log(`✅ 에러 없음. 스크린샷: ${out}`);
})();
