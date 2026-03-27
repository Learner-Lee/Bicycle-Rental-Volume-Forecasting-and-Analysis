// ============================================================
// 我来当老板 · STEM 共享单车需求预测 · 演示文稿生成脚本
// ============================================================
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// ── Color Palette ────────────────────────────────────────────
const C = {
  navyDark:   "0F2340",
  navy:       "1E3A5F",
  teal:       "00B4D8",
  tealDark:   "0077A3",
  orange:     "FF6B35",
  white:      "FFFFFF",
  offWhite:   "F8FAFC",
  gray:       "64748B",
  grayLight:  "E2E8F0",
  textDark:   "1E293B",
  green:      "10B981",
  purple:     "7C3AED",
  yellow:     "F59E0B",
  yellowLight:"FFF3E0",
};

// ── Shadow factory (MUST be new object each call) ────────────
const makeShadow = (blur = 8, offset = 3, opacity = 0.15) => ({
  type: "outer", color: "000000", blur, offset, angle: 135, opacity,
});

// ── Slide header with left accent bar ────────────────────────
function addHeader(slide, title, accentColor = C.teal) {
  slide.addShape(slide.pres ? slide.pres.shapes.RECTANGLE : "rect", {
    x: 0.4, y: 0.32, w: 0.07, h: 0.52,
    fill: { color: accentColor }, line: { color: accentColor },
  });
  slide.addText(title, {
    x: 0.6, y: 0.29, w: 8.8, h: 0.62,
    fontSize: 22, bold: true, color: C.navy,
    fontFace: "Calibri", margin: 0,
  });
}

// ── Small tag chip ───────────────────────────────────────────
function addTag(slide, text, x, y, color = C.teal, w = 1.5) {
  slide.addShape("rect", { x, y, w, h: 0.30, fill: { color }, line: { color } });
  slide.addText(text, {
    x, y: y + 0.01, w, h: 0.28,
    fontSize: 10, bold: true, color: C.white,
    align: "center", fontFace: "Calibri", margin: 0,
  });
}

// ── Time chip ────────────────────────────────────────────────
function addTimeChip(slide, label, color = C.teal) {
  slide.addShape("rect", { x: 8.5, y: 0.30, w: 1.1, h: 0.32, fill: { color }, line: { color } });
  slide.addText(label, {
    x: 8.5, y: 0.31, w: 1.1, h: 0.30,
    fontSize: 10.5, bold: true, color: C.white,
    align: "center", fontFace: "Calibri", margin: 0,
  });
}

// ── Section divider slide ────────────────────────────────────
function addDivider(pres, partNum, titleZh, subtitleEn, bgColor, accentColor) {
  const s = pres.addSlide();
  s.background = { color: bgColor };
  s.addShape("rect", {
    x: 0, y: 0, w: 10, h: 5.625,
    fill: { color: accentColor, transparency: 90 },
    line: { color: accentColor, transparency: 90 },
  });
  // Large watermark number
  s.addText(partNum, {
    x: 5.2, y: -0.5, w: 4.6, h: 5,
    fontSize: 220, bold: true, color: C.white, transparency: 90,
    fontFace: "Calibri", align: "right",
  });
  // Eyebrow pill
  s.addShape("rect", {
    x: 0.65, y: 1.52, w: 1.25, h: 0.35,
    fill: { color: accentColor }, line: { color: accentColor },
  });
  s.addText(`PART  ${partNum}`, {
    x: 0.65, y: 1.525, w: 1.25, h: 0.335,
    fontSize: 11, bold: true, color: C.white,
    align: "center", fontFace: "Calibri", margin: 0,
  });
  // Main title
  s.addText(titleZh, {
    x: 0.65, y: 2.05, w: 8, h: 1.15,
    fontSize: 62, bold: true, color: C.white, fontFace: "Calibri",
  });
  // Sub
  s.addText(subtitleEn, {
    x: 0.65, y: 3.3, w: 8, h: 0.55,
    fontSize: 18, color: accentColor, fontFace: "Calibri",
  });
}

// ── Chart placeholder box ────────────────────────────────────
function addChartPlaceholder(slide, x, y, w, h, note1, note2) {
  slide.addShape("rect", {
    x, y, w, h,
    fill: { color: "EBF8FD" }, line: { color: C.teal, width: 1.5 },
  });
  slide.addText([
    { text: "【图表占位】\n", options: { bold: true, color: C.teal, fontSize: 15, breakLine: true } },
    { text: note1 + "\n", options: { color: C.gray, fontSize: 12, breakLine: true } },
    { text: note2, options: { color: C.grayLight, fontSize: 10, italic: true } },
  ], {
    x: x + 0.15, y: y + h * 0.35, w: w - 0.3, h: h * 0.5,
    align: "center", valign: "middle", fontFace: "Calibri",
  });
}

// ════════════════════════════════════════════════════════════
async function main() {
  const pres = new pptxgen();
  pres.layout   = "LAYOUT_16x9";   // 10" × 5.625"
  pres.title    = "我来当老板：共享单车需求预测 STEM 课程展示";

  // ──────────────────────────────────────────────────────────
  // SLIDE 1 · 封面
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navyDark };

    // Decorative circles
    s.addShape("ellipse", { x: 7.5, y: -1.2, w: 4.5, h: 4.5, fill: { color: C.teal, transparency: 88 }, line: { color: C.teal, transparency: 88 } });
    s.addShape("ellipse", { x: 8.2, y: 3.0,  w: 2.8, h: 2.8, fill: { color: C.orange, transparency: 90 }, line: { color: C.orange, transparency: 90 } });
    s.addShape("ellipse", { x: 6.8, y: 4.0,  w: 1.5, h: 1.5, fill: { color: C.teal, transparency: 85 }, line: { color: C.teal, transparency: 85 } });

    // Left color stripe
    s.addShape("rect", { x: 0, y: 0, w: 0.1, h: 5.625, fill: { color: C.orange }, line: { color: C.orange } });
    s.addShape("rect", { x: 0.1, y: 0, w: 0.06, h: 5.625, fill: { color: C.teal, transparency: 50 }, line: { color: C.teal, transparency: 50 } });

    // Eyebrow
    s.addShape("rect", { x: 0.55, y: 0.55, w: 2.9, h: 0.34, fill: { color: C.orange }, line: { color: C.orange } });
    s.addText("STEM  ·  数据挖掘课程展示  ·  Group Project", {
      x: 0.55, y: 0.555, w: 2.9, h: 0.33,
      fontSize: 10.5, bold: true, color: C.white, align: "center",
      fontFace: "Calibri", margin: 0,
    });

    // Main title
    s.addText("我来当老板", {
      x: 0.55, y: 1.08, w: 7.2, h: 1.4,
      fontSize: 60, bold: true, color: C.white,
      fontFace: "Calibri", charSpacing: 4,
    });

    // Subtitle
    s.addText("基于决策树的共享单车需求预测", {
      x: 0.55, y: 2.42, w: 7.2, h: 0.72,
      fontSize: 26, color: C.teal, fontFace: "Calibri",
    });

    // Divider
    s.addShape("rect", { x: 0.55, y: 3.28, w: 6.5, h: 0.04, fill: { color: C.teal, transparency: 55 }, line: { color: C.teal, transparency: 55 } });

    // Meta
    s.addText([
      { text: "目标年级：中三（九年级）  ·  ", options: { color: "A8C4E0" } },
      { text: "演讲时长：18 分钟  ·  ", options: { color: "A8C4E0" } },
      { text: "INT6068  Neural Networks and Deep Learning", options: { color: C.teal } },
    ], { x: 0.55, y: 3.42, w: 8, h: 0.48, fontSize: 13, fontFace: "Calibri" });

    // Bottom ribbon
    s.addShape("rect", { x: 0, y: 5.18, w: 10, h: 0.445, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("数据分析  ·  数据挖掘  ·  课程设计  ·  课堂活动", {
      x: 0, y: 5.2, w: 10, h: 0.4,
      fontSize: 13, color: C.teal, align: "center", fontFace: "Calibri",
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 2 · 大纲
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "课程大纲  ·  Agenda");

    const sections = [
      { num: "01", zh: "数据分析",   en: "Data Analysis",  pct: "15%", min: "~3 min", color: C.teal,   bg: "E0F7FA" },
      { num: "02", zh: "数据挖掘",   en: "Data Mining",    pct: "15%", min: "~3 min", color: C.navy,   bg: "E8EAF6" },
      { num: "03", zh: "课程设计",   en: "Course Design",  pct: "35%", min: "~6 min", color: C.orange, bg: "FFF3E0" },
      { num: "04", zh: "课堂活动",   en: "Activities",     pct: "35%", min: "~6 min", color: C.green,  bg: "E8F5E9" },
    ];

    const cw = 2.1, gap = 0.08, x0 = 0.44;
    sections.forEach((sec, i) => {
      const x = x0 + i * (cw + gap);
      s.addShape("rect", { x, y: 1.05, w: cw, h: 4.15, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(6, 2, 0.1) });
      s.addShape("rect", { x, y: 1.05, w: cw, h: 0.1,  fill: { color: sec.color }, line: { color: sec.color } });
      // Large ghost number
      s.addText(sec.num, { x, y: 1.22, w: cw, h: 0.95, fontSize: 46, bold: true, color: sec.bg, align: "center", fontFace: "Calibri" });
      s.addText(sec.zh,  { x, y: 2.2,  w: cw, h: 0.52, fontSize: 21, bold: true, color: sec.color, align: "center", fontFace: "Calibri" });
      s.addText(sec.en,  { x, y: 2.72, w: cw, h: 0.38, fontSize: 11.5, color: C.gray, align: "center", fontFace: "Calibri" });
      s.addShape("rect", { x: x + 0.45, y: 3.2, w: cw - 0.9, h: 0.03, fill: { color: sec.bg }, line: { color: sec.bg } });
      s.addText(sec.pct, { x, y: 3.3,  w: cw, h: 0.6, fontSize: 28, bold: true, color: sec.color, align: "center", fontFace: "Calibri" });
      s.addText(sec.min, { x, y: 3.9,  w: cw, h: 0.36, fontSize: 13, color: C.gray, align: "center", fontFace: "Calibri" });
    });

    s.addText("总演讲时间：18 分钟  |  Q&A：2 分钟", {
      x: 0.44, y: 5.28, w: 9.1, h: 0.28,
      fontSize: 11, color: C.gray, align: "center", fontFace: "Calibri", italic: true,
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 3 · Section 1 Divider — 数据分析
  // ──────────────────────────────────────────────────────────
  addDivider(pres, "01", "数据分析", "Data Analysis  ·  15%  ·  ~3 min", "005F7A", C.teal);

  // ──────────────────────────────────────────────────────────
  // SLIDE 4 · 数据集介绍
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "数据集介绍 — UCI Bike Sharing Dataset");
    addTag(s, "数据分析", 0.4, 5.18, C.teal, 1.4);

    const stats = [
      { val: "17,379 条",   label: "数据总量",   sub: "小时级骑行记录" },
      { val: "2011 – 2012", label: "时间跨度",   sub: "华盛顿特区 Capital Bikeshare" },
      { val: "13 个特征",   label: "特征维度",   sub: "气象 / 时间 / 季节等多维特征" },
      { val: "70 : 30",     label: "训练 / 测试集比例", sub: "按时间序列划分，模拟真实预测" },
    ];
    stats.forEach((st, i) => {
      const y = 1.05 + i * 1.05;
      s.addShape("rect", { x: 0.4, y, w: 4.2, h: 0.9, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 1, 0.08) });
      s.addShape("rect", { x: 0.4, y, w: 0.08, h: 0.9, fill: { color: C.teal }, line: { color: C.teal } });
      s.addText(st.val,   { x: 0.62, y: y + 0.05, w: 3.8, h: 0.45, fontSize: 22, bold: true, color: C.navy, fontFace: "Calibri", margin: 0 });
      s.addText(`${st.label}  ·  ${st.sub}`, { x: 0.62, y: y + 0.52, w: 3.8, h: 0.3, fontSize: 11, color: C.gray, fontFace: "Calibri", margin: 0 });
    });

    addChartPlaceholder(s, 4.9, 1.05, 4.7, 3.85,
      "每日租赁量趋势图（2011–2012）", "建议使用 Dashboard 页面截图替换");
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 5 · 关键发现
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "数据探索关键发现  ·  Key Insights");
    addTag(s, "数据分析", 0.4, 5.18, C.teal, 1.4);

    const findings = [
      { icon: "🌡️", title: "温度驱动需求",   desc: "租赁量与温度正相关（r ≈ 0.40）；最适骑行温度 20–35°C，超过 38°C 后需求回落。", color: C.orange },
      { icon: "🕐", title: "双峰通勤规律",   desc: "工作日呈早高峰（8点）和晚高峰（17–18点），休息日则呈 10–15 点单峰休闲分布。",  color: C.teal },
      { icon: "🌧️", title: "天气决定性影响", desc: "晴天租赁量约为大雨 / 大雪天气的 10 倍，天气是用户出行决策最直接的外部变量。",  color: C.navy },
      { icon: "📈", title: "平台高速增长",   desc: "2012 年总租赁量较 2011 年增长约 64%，注册用户贡献约 80% 的总租赁量。",          color: C.green },
    ];

    findings.forEach((f, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = 0.4 + col * 4.7, y = 1.08 + row * 1.98;
      s.addShape("rect", { x, y, w: 4.45, h: 1.78, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 2, 0.08) });
      s.addShape("rect", { x, y, w: 0.08, h: 1.78, fill: { color: f.color }, line: { color: f.color } });
      s.addText(f.icon,  { x: x + 0.18, y: y + 0.12, w: 0.65, h: 0.55, fontSize: 26, align: "center" });
      s.addText(f.title, { x: x + 0.85, y: y + 0.12, w: 3.4,  h: 0.42, fontSize: 15, bold: true, color: f.color, fontFace: "Calibri", margin: 0 });
      s.addText(f.desc,  { x: x + 0.85, y: y + 0.58, w: 3.4,  h: 1.0,  fontSize: 11.5, color: C.textDark, fontFace: "Calibri", margin: 0 });
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 6 · Section 2 Divider — 数据挖掘
  // ──────────────────────────────────────────────────────────
  addDivider(pres, "02", "数据挖掘", "Data Mining  ·  15%  ·  ~3 min", C.navyDark, C.teal);

  // ──────────────────────────────────────────────────────────
  // SLIDE 7 · 决策树核心概念
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "决策树核心概念  ·  Decision Tree");
    addTag(s, "数据挖掘", 0.4, 5.18, C.navy, 1.4);

    // Left: 3 term cards
    const terms = [
      { zh: "根节点", en: "Root Node", desc: "第一个判断问题\n如：「温度 > 25°C 吗？」", color: C.orange },
      { zh: "分支",   en: "Branches",  desc: "是 Yes  /  否 No\n对应不同特征值的路径", color: C.teal },
      { zh: "叶子节点", en: "Leaf Node", desc: "最终预测结果\n如：「需求爆满」或「需求冷清」", color: C.green },
    ];
    terms.forEach((t, i) => {
      const y = 1.05 + i * 1.38;
      s.addShape("rect", { x: 0.4, y, w: 4.5, h: 1.18, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 1, 0.08) });
      s.addShape("rect", { x: 0.4, y, w: 0.08, h: 1.18, fill: { color: t.color }, line: { color: t.color } });
      s.addText(`${t.zh}  ${t.en}`, { x: 0.62, y: y + 0.1, w: 4.1, h: 0.42, fontSize: 14, bold: true, color: t.color, fontFace: "Calibri", margin: 0 });
      s.addText(t.desc, { x: 0.62, y: y + 0.58, w: 4.1, h: 0.55, fontSize: 12, color: C.textDark, fontFace: "Calibri", margin: 0 });
    });

    // Right: mini visual tree
    const TY = 1.1; // tree top y
    // Root
    s.addShape("rect", { x: 6.1, y: TY,     w: 2.6, h: 0.52, fill: { color: C.orange }, line: { color: C.orange }, shadow: makeShadow(3, 1, 0.1) });
    s.addText("温度 > 25°C ?",   { x: 6.1, y: TY,     w: 2.6, h: 0.52, fontSize: 13, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri" });

    // Branches
    s.addShape("line", { x: 6.6,  y: TY + 0.52, w: 0,   h: 0.5, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 8.2,  y: TY + 0.52, w: 0,   h: 0.5, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 6.6,  y: TY + 1.02, w: 1.6, h: 0,   line: { color: C.gray, width: 1.5 } });
    s.addText("是 ✓", { x: 5.72, y: TY + 0.7, w: 0.75, h: 0.28, fontSize: 11, bold: true, color: C.green, fontFace: "Calibri" });
    s.addText("否 ✗", { x: 8.28, y: TY + 0.7, w: 0.75, h: 0.28, fontSize: 11, bold: true, color: "D32F2F", fontFace: "Calibri" });

    // Level 2 left node
    s.addShape("rect", { x: 5.75, y: TY + 1.02, w: 1.7, h: 0.48, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("工作日 ?", { x: 5.75, y: TY + 1.02, w: 1.7, h: 0.48, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri" });

    // Level 2 right leaf
    s.addShape("rect", { x: 7.9, y: TY + 1.02, w: 1.7, h: 0.48, fill: { color: C.grayLight }, line: { color: C.grayLight } });
    s.addText("❄️  需求冷清", { x: 7.9, y: TY + 1.02, w: 1.7, h: 0.48, fontSize: 12, bold: true, color: C.gray, align: "center", valign: "middle", fontFace: "Calibri" });

    // Level 2 left → Level 3
    s.addShape("line", { x: 5.9,  y: TY + 1.5,  w: 0,   h: 0.42, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 7.3,  y: TY + 1.5,  w: 0,   h: 0.42, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 5.9,  y: TY + 1.92, w: 1.4, h: 0,    line: { color: C.gray, width: 1.5 } });

    s.addShape("rect", { x: 5.6,  y: TY + 1.92, w: 1.6, h: 0.48, fill: { color: C.green }, line: { color: C.green } });
    s.addText("🔥  需求爆满", { x: 5.6, y: TY + 1.92, w: 1.6, h: 0.48, fontSize: 11.5, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri" });

    s.addShape("rect", { x: 7.1,  y: TY + 1.92, w: 1.6, h: 0.48, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("📊  需求一般", { x: 7.1, y: TY + 1.92, w: 1.6, h: 0.48, fontSize: 11.5, bold: true, color: C.white, align: "center", valign: "middle", fontFace: "Calibri" });

    s.addText("💡  信息增益 = 每次分裂后数据「纯度」的提升量", {
      x: 5.6, y: 4.68, w: 4.1, h: 0.38,
      fontSize: 11, italic: true, color: C.gray, fontFace: "Calibri", align: "center",
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 8 · 五种模型对比
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "机器学习模型性能对比");
    addTag(s, "数据挖掘", 0.4, 5.18, C.navy, 1.4);

    addChartPlaceholder(s, 0.4, 1.05, 5.5, 3.85,
      "五种模型 R² & RMSE 对比柱状图", "建议使用 Summary 页面截图替换");

    // Right: model ranking
    const models = [
      { rank: "🥇", name: "XGBoost",  r2: "≈ 0.950", rmse: "≈ 53.4", color: C.orange },
      { rank: "🥈", name: "梯度提升", r2: "≈ 0.930", rmse: "≈ 63.2", color: C.teal },
      { rank: "🥉", name: "随机森林", r2: "≈ 0.920", rmse: "≈ 67.8", color: C.navy },
      { rank: "4️⃣",  name: "岭回归",  r2: "≈ 0.730", rmse: "≈ 124",  color: C.gray },
      { rank: "5️⃣",  name: "线性回归",r2: "≈ 0.730", rmse: "≈ 124",  color: C.gray },
    ];
    models.forEach((m, i) => {
      const y = 1.05 + i * 0.75;
      s.addShape("rect", { x: 6.2, y, w: 3.4, h: 0.65, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(3, 1, 0.07) });
      s.addText(m.rank, { x: 6.25, y: y + 0.05, w: 0.5,  h: 0.55, fontSize: 18, align: "center", fontFace: "Calibri" });
      s.addText(m.name, { x: 6.8,  y: y + 0.06, w: 1.7,  h: 0.38, fontSize: 14, bold: true, color: m.color, fontFace: "Calibri", margin: 0 });
      s.addText(`R² ${m.r2}  ·  RMSE ${m.rmse}`, { x: 6.8, y: y + 0.38, w: 2.65, h: 0.24, fontSize: 10.5, color: C.gray, fontFace: "Calibri", margin: 0 });
    });

    s.addText("No Free Lunch 定理：没有任何模型在所有问题上都最优，选型需权衡精度、速度与可解释性", {
      x: 6.2, y: 4.9, w: 3.4, h: 0.55,
      fontSize: 11, color: C.gray, italic: true, fontFace: "Calibri", align: "center",
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 9 · Section 3 Divider — 课程设计
  // ──────────────────────────────────────────────────────────
  addDivider(pres, "03", "课程设计", "Course Design  ·  35%  ·  ~6 min", "7B2D00", C.orange);

  // ──────────────────────────────────────────────────────────
  // SLIDE 10 · STEM 学习成果
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "STEM 学习成果  ·  Learning Outcomes");
    addTag(s, "课程设计", 0.4, 5.18, C.orange, 1.4);

    const outcomes = [
      {
        subj: "🌆  科学 · 城市研究",
        color: C.teal,
        pts: ["了解环境因素（温度、湿度、天气）对城市交通的实际影响",
              "掌握时间因素（工作日 vs 节假日）如何改变出行模式"],
      },
      {
        subj: "💻  技术",
        color: C.navy,
        pts: ["理解数据可视化如何帮助从原始数据中发现规律",
              "认识机器学习与数据挖掘的基本概念和应用场景"],
      },
      {
        subj: "⚙️  工程 · 系统思维",
        color: C.orange,
        pts: ["将真实商业问题（调度不当）转化为可解决的数据问题",
              "体验算法如何量化优化共享单车的运营效率"],
      },
      {
        subj: "📐  数学",
        color: C.green,
        pts: ["用 If-Then 逻辑规则构建决策树模型（无需复杂公式）",
              "直觉性理解信息增益与数据分类纯度的概念"],
      },
    ];

    outcomes.forEach((o, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = 0.4 + col * 4.7, y = 1.05 + row * 2.05;
      s.addShape("rect", { x, y, w: 4.45, h: 1.85, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 2, 0.08) });
      s.addShape("rect", { x, y, w: 4.45, h: 0.44, fill: { color: o.color }, line: { color: o.color } });
      s.addText(o.subj, { x: x + 0.12, y: y + 0.06, w: 4.2, h: 0.35, fontSize: 14, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
      o.pts.forEach((pt, j) => {
        s.addText([{ text: pt, options: { bullet: true } }], {
          x: x + 0.18, y: y + 0.54 + j * 0.58, w: 4.1, h: 0.54,
          fontSize: 11.5, color: C.textDark, fontFace: "Calibri",
        });
      });
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 11 · 40分钟课程结构（5活动时间线）
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "课程结构总览 — 40 分钟时间线");
    addTag(s, "课程设计", 0.4, 5.18, C.orange, 1.4);

    // Horizontal spine
    s.addShape("rect", { x: 0.55, y: 2.88, w: 9.0, h: 0.06, fill: { color: C.grayLight }, line: { color: C.grayLight } });

    const acts = [
      { n: "1", zh: "竞猜游戏", t: "5 min",  sub: "破冰引入",  color: C.teal,   x: 0.6  },
      { n: "2", zh: "数据侦探", t: "7 min",  sub: "图表探秘",  color: C.navy,   x: 2.65 },
      { n: "3", zh: "概念讲解", t: "5 min",  sub: "决策树入门", color: C.orange, x: 4.7  },
      { n: "4", zh: "老板挑战", t: "15 min", sub: "★ 核心活动", color: C.green,  x: 6.75 },
      { n: "5", zh: "巅峰对决", t: "8 min",  sub: "测试与总结", color: C.purple, x: 8.65 },
    ];

    acts.forEach((a, i) => {
      const even = i % 2 === 0;
      // Dot on spine
      s.addShape("ellipse", { x: a.x, y: 2.715, w: 0.36, h: 0.36, fill: { color: a.color }, line: { color: a.color } });
      s.addText(a.n, { x: a.x, y: 2.72, w: 0.36, h: 0.34, fontSize: 14, bold: true, color: C.white, align: "center", fontFace: "Calibri" });

      const cy = a.x + 0.18;          // center x of dot
      const cw2 = 1.5, cx = cy - 0.75; // card x

      if (even) {
        // Card above
        s.addShape("line", { x: cy, y: 2.52, w: 0, h: 0.22, line: { color: a.color, width: 2 } });
        s.addShape("rect", { x: cx, y: 1.12, w: cw2, h: 1.32, fill: { color: C.white }, line: { color: a.color }, shadow: makeShadow(4, 1, 0.1) });
        s.addShape("rect", { x: cx, y: 1.12, w: cw2, h: 0.08, fill: { color: a.color }, line: { color: a.color } });
        s.addText(a.zh,  { x: cx, y: 1.26, w: cw2, h: 0.44, fontSize: 14, bold: true, color: a.color, align: "center", fontFace: "Calibri" });
        s.addText(a.t,   { x: cx, y: 1.70, w: cw2, h: 0.32, fontSize: 13, color: C.gray, align: "center", fontFace: "Calibri" });
        s.addText(a.sub, { x: cx, y: 2.02, w: cw2, h: 0.3,  fontSize: 11, color: C.gray, align: "center", italic: true, fontFace: "Calibri" });
      } else {
        // Card below
        s.addShape("line", { x: cy, y: 3.09, w: 0, h: 0.22, line: { color: a.color, width: 2 } });
        s.addShape("rect", { x: cx, y: 3.33, w: cw2, h: 1.32, fill: { color: C.white }, line: { color: a.color }, shadow: makeShadow(4, 1, 0.1) });
        s.addShape("rect", { x: cx, y: 3.33, w: cw2, h: 0.08, fill: { color: a.color }, line: { color: a.color } });
        s.addText(a.zh,  { x: cx, y: 3.47, w: cw2, h: 0.44, fontSize: 14, bold: true, color: a.color, align: "center", fontFace: "Calibri" });
        s.addText(a.t,   { x: cx, y: 3.91, w: cw2, h: 0.32, fontSize: 13, color: C.gray, align: "center", fontFace: "Calibri" });
        s.addText(a.sub, { x: cx, y: 4.23, w: cw2, h: 0.3,  fontSize: 11, color: C.gray, align: "center", italic: true, fontFace: "Calibri" });
      }
    });

    // Total
    s.addText("合计：40 分钟", {
      x: 0.55, y: 5.08, w: 9, h: 0.35,
      fontSize: 11, color: C.gray, align: "center", fontFace: "Calibri", italic: true,
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 12 · 教学材料设计
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "教学材料设计  ·  Teaching Materials");
    addTag(s, "课程设计", 0.4, 5.18, C.orange, 1.4);

    const mats = [
      {
        title: "样本卡  ×  20",
        icon: "🗂️",
        color: C.orange,
        pts: [
          "🔴  红色 = 需求爆满（高租赁）",
          "🔵  蓝色 = 需求冷清（低租赁）",
          "包含温度、天气、工作日等特征",
          "真实数据驱动，增加可信度",
        ],
      },
      {
        title: "条件卡（判断节点）",
        icon: "❓",
        color: C.teal,
        pts: [
          "「温度 > 25°C 吗？」",
          "「今天是工作日吗？」",
          "「天气好吗？」",
          "学生选卡片拼接决策树，零编程",
        ],
      },
      {
        title: "测试卡  ×  5",
        icon: "🏆",
        color: C.green,
        pts: [
          "全新未见的数据样本（测试集）",
          "各组用自己的决策树做预测",
          "激励竞争，提升投入感",
          "对应现实中「模型泛化」概念",
        ],
      },
    ];

    mats.forEach((m, i) => {
      const x = 0.4 + i * 3.1;
      s.addShape("rect", { x, y: 1.05, w: 2.95, h: 3.95, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(5, 2, 0.1) });
      s.addShape("rect", { x, y: 1.05, w: 2.95, h: 0.95, fill: { color: m.color }, line: { color: m.color } });
      s.addText(m.icon,  { x, y: 1.1,  w: 2.95, h: 0.48, fontSize: 24, align: "center" });
      s.addText(m.title, { x, y: 1.58, w: 2.95, h: 0.38, fontSize: 12.5, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
      m.pts.forEach((p, j) => {
        s.addText([{ text: p, options: { bullet: true } }], {
          x: x + 0.15, y: 2.1 + j * 0.7, w: 2.65, h: 0.62,
          fontSize: 11, color: C.textDark, fontFace: "Calibri",
        });
      });
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 13 · 课程设计亮点
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "课程设计亮点  ·  Design Highlights");
    addTag(s, "课程设计", 0.4, 5.18, C.orange, 1.4);

    const pts = [
      { icon: "🔌", title: "不插电  Unplugged",     desc: "无需电脑，用物理卡片完成训练→测试→评估的完整ML流程。降低技术门槛，让全体同学都能参与建模。", color: C.teal },
      { icon: "👔", title: "角色代入  Roleplay",    desc: "「我来当老板」情境设计，学生以运营顾问身份解决真实商业问题，大幅提升动机与课堂投入感。",  color: C.orange },
      { icon: "🎮", title: "竞争机制  Gamification", desc: "组间对抗 + 测试卡大考验，测试准确率高的小组赢得奖励。将课堂变成游戏，强化正向反馈循环。",   color: C.navy },
      { icon: "📊", title: "数据驱动  Data-Led",    desc: "先做数据侦探再建模，体验从原始数据→可视化探索→算法建模的完整数据科学思维链。",              color: C.green },
    ];

    pts.forEach((p, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const x = 0.4 + col * 4.7, y = 1.05 + row * 2.05;
      s.addShape("rect", { x, y, w: 4.45, h: 1.85, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 2, 0.08) });
      s.addShape("rect", { x, y, w: 0.08, h: 1.85, fill: { color: p.color }, line: { color: p.color } });
      s.addText(`${p.icon}  ${p.title}`, { x: x + 0.22, y: y + 0.12, w: 4.0, h: 0.44, fontSize: 14, bold: true, color: p.color, fontFace: "Calibri", margin: 0 });
      s.addText(p.desc, { x: x + 0.22, y: y + 0.62, w: 4.05, h: 1.1, fontSize: 11.5, color: C.textDark, fontFace: "Calibri", margin: 0 });
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 14 · Section 4 Divider — 课堂活动
  // ──────────────────────────────────────────────────────────
  addDivider(pres, "04", "课堂活动", "Classroom Activities  ·  35%  ·  ~6 min", "064E3B", C.green);

  // ──────────────────────────────────────────────────────────
  // SLIDE 15 · 活动1 — 破冰竞猜
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "活动 1  ·  交通工具竞猜游戏（破冰）");
    addTag(s, "课堂活动", 0.4, 5.18, C.green, 1.4);
    addTimeChip(s, "⏱  5 min", C.teal);

    const steps = [
      { n: "1", text: "教师宣布本节课与一种交通工具有关，不透露答案", color: C.teal },
      { n: "2", text: "学生轮流提问「是 / 否」问题（如：它有轮子吗？）", color: C.teal },
      { n: "3", text: "教师同步在黑板上画出是否分支逻辑图", color: C.teal },
      { n: "4", text: "猜出「自行车」的学生获奖，教师引出共享单车老板情境", color: C.orange },
    ];

    steps.forEach((st, i) => {
      const y = 1.1 + i * 0.97;
      s.addShape("ellipse", { x: 0.4, y: y + 0.1, w: 0.42, h: 0.42, fill: { color: st.color }, line: { color: st.color } });
      s.addText(st.n, { x: 0.4, y: y + 0.11, w: 0.42, h: 0.4, fontSize: 15, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
      s.addText(st.text, { x: 1.0, y: y + 0.08, w: 4.15, h: 0.52, fontSize: 13, color: C.textDark, fontFace: "Calibri", valign: "middle" });
      if (i < 3) s.addShape("line", { x: 0.61, y: y + 0.52, w: 0, h: 0.46, line: { color: C.grayLight, width: 1.5, dashType: "dash" } });
    });

    // Right: goal box
    s.addShape("rect", { x: 5.55, y: 1.05, w: 4.05, h: 3.95, fill: { color: "EBF8FD" }, line: { color: C.teal, width: 1 } });
    s.addShape("rect", { x: 5.55, y: 1.05, w: 4.05, h: 0.48, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("🎯  学习目标", { x: 5.62, y: 1.07, w: 3.9, h: 0.44, fontSize: 14, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });

    const goals = [
      "体验「是/否」二分类决策的核心逻辑",
      "在游戏中无意识运行决策树推理过程",
      "为正式学习决策树概念搭建认知脚手架",
      "通过竞猜激活课堂氛围，打破陌生感",
    ];
    goals.forEach((g, i) => {
      s.addText([{ text: g, options: { bullet: true } }], {
        x: 5.7, y: 1.65 + i * 0.68, w: 3.75, h: 0.6,
        fontSize: 12, color: C.textDark, fontFace: "Calibri",
      });
    });

    // Quote
    s.addShape("rect", { x: 5.55, y: 4.55, w: 4.05, h: 0.45, fill: { color: C.teal, transparency: 80 }, line: { color: C.teal, transparency: 80 } });
    s.addText("「太棒了！现在你们要帮我的共享单车公司解决调度问题！」", {
      x: 5.62, y: 4.57, w: 3.95, h: 0.4,
      fontSize: 10, italic: true, color: C.navy, fontFace: "Calibri", align: "center",
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 16 · 活动2 — 数据侦探
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "活动 2  ·  数据侦探任务");
    addTag(s, "课堂活动", 0.4, 5.18, C.green, 1.4);
    addTimeChip(s, "⏱  7 min", C.teal);

    addChartPlaceholder(s, 0.4, 1.05, 5.3, 3.85,
      "分发给学生的可视化图表（时段分布 / 温度相关 / 天气影响）",
      "建议截取 Dashboard 页面图表打印 / 投影");

    s.addShape("rect", { x: 6.0, y: 1.05, w: 3.6, h: 0.48, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("学生预期发现", { x: 6.05, y: 1.07, w: 3.5, h: 0.44, fontSize: 14, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });

    const obs = [
      { txt: "黄金骑行温度：20–35°C", color: C.orange },
      { txt: "工作日出现早晚双高峰",   color: C.teal },
      { txt: "大雨天气租赁量骤降 90%", color: C.navy },
      { txt: "秋季是全年最高需求季",   color: C.green },
    ];
    obs.forEach((o, i) => {
      const y = 1.68 + i * 0.9;
      s.addShape("rect", { x: 6.0, y, w: 3.6, h: 0.76, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(3, 1, 0.07) });
      s.addShape("rect", { x: 6.0, y, w: 0.08, h: 0.76, fill: { color: o.color }, line: { color: o.color } });
      s.addText(o.txt, { x: 6.2, y: y + 0.2, w: 3.2, h: 0.36, fontSize: 12.5, color: C.textDark, fontFace: "Calibri", margin: 0 });
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 17 · 活动3 — 概念讲解
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "活动 3  ·  概念讲解：什么是决策树？");
    addTag(s, "课堂活动", 0.4, 5.18, C.green, 1.4);
    addTimeChip(s, "⏱  5 min", C.teal);

    // Bridge banner
    s.addShape("rect", { x: 0.4, y: 1.05, w: 4.5, h: 0.78, fill: { color: C.yellowLight }, line: { color: C.yellow, width: 1 } });
    s.addText("💡  回顾活动1：黑板上的分支图就是决策树！", {
      x: 0.5, y: 1.1, w: 4.3, h: 0.65, fontSize: 12.5, bold: true, color: "7B5800", fontFace: "Calibri",
    });

    // 3 term cards
    const terms = [
      { zh: "根节点", en: "Root Node",  icon: "🌱", desc: "第一个判断\n「温度 > 25°C？」", color: C.orange },
      { zh: "分支",   en: "Branches",   icon: "🔀", desc: "是 / 否\n两条路径分叉",       color: C.teal },
      { zh: "叶子节点", en: "Leaf Node", icon: "🍃", desc: "最终结果\n「爆满 / 冷清」",   color: C.green },
    ];
    terms.forEach((t, i) => {
      const x = 0.4 + i * 1.55;
      s.addShape("rect", { x, y: 2.05, w: 1.4, h: 2.5, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 1, 0.1) });
      s.addShape("rect", { x, y: 2.05, w: 1.4, h: 0.08, fill: { color: t.color }, line: { color: t.color } });
      s.addText(t.icon, { x, y: 2.18, w: 1.4, h: 0.5, fontSize: 22, align: "center" });
      s.addText(t.zh,   { x, y: 2.68, w: 1.4, h: 0.4, fontSize: 14, bold: true, color: t.color, align: "center", fontFace: "Calibri" });
      s.addText(t.en,   { x, y: 3.08, w: 1.4, h: 0.3, fontSize: 10, color: C.gray, align: "center", italic: true, fontFace: "Calibri" });
      s.addText(t.desc, { x, y: 3.42, w: 1.4, h: 0.85, fontSize: 10.5, color: C.textDark, align: "center", fontFace: "Calibri" });
    });

    // Right: real-life example
    s.addShape("rect", { x: 5.45, y: 1.05, w: 4.15, h: 3.85, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 2, 0.08) });
    s.addShape("rect", { x: 5.45, y: 1.05, w: 4.15, h: 0.48, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("📌  生活例子：周末出去玩吗？", { x: 5.5, y: 1.07, w: 4.05, h: 0.44, fontSize: 13, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });

    // Mini tree
    s.addShape("rect", { x: 5.95, y: 1.72, w: 2.1, h: 0.44, fill: { color: "E3F2FD" }, line: { color: C.teal, width: 0.75 } });
    s.addText("天气好吗？", { x: 5.95, y: 1.73, w: 2.1, h: 0.42, fontSize: 12, color: C.navy, align: "center", fontFace: "Calibri" });
    s.addShape("line", { x: 6.2,  y: 2.16, w: 0,   h: 0.38, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 7.7,  y: 2.16, w: 0,   h: 0.38, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 6.2,  y: 2.54, w: 1.5, h: 0,    line: { color: C.gray, width: 1.5 } });

    s.addShape("rect", { x: 5.9, y: 2.54, w: 1.6, h: 0.44, fill: { color: "E8F5E9" }, line: { color: C.green, width: 0.75 } });
    s.addText("作业写完了？", { x: 5.9, y: 2.55, w: 1.6, h: 0.42, fontSize: 11, color: C.navy, align: "center", fontFace: "Calibri" });
    s.addShape("rect", { x: 7.6, y: 2.54, w: 1.6, h: 0.44, fill: { color: "FFEBEE" }, line: { color: "D32F2F", width: 0.75 } });
    s.addText("✗  在家宅", { x: 7.6, y: 2.55, w: 1.6, h: 0.42, fontSize: 11, color: "D32F2F", align: "center", fontFace: "Calibri" });

    s.addShape("line", { x: 6.3, y: 2.98, w: 0, h: 0.35, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 7.2, y: 2.98, w: 0, h: 0.35, line: { color: C.gray, width: 1.5 } });
    s.addShape("line", { x: 6.3, y: 3.33, w: 0.9, h: 0, line: { color: C.gray, width: 1.5 } });

    s.addShape("rect", { x: 5.95, y: 3.33, w: 1.5, h: 0.42, fill: { color: C.green }, line: { color: C.green } });
    s.addText("✓  出发！", { x: 5.95, y: 3.34, w: 1.5, h: 0.4, fontSize: 11, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
    s.addShape("rect", { x: 7.05, y: 3.33, w: 1.5, h: 0.42, fill: { color: C.orange }, line: { color: C.orange } });
    s.addText("学习完再说", { x: 7.05, y: 3.34, w: 1.5, h: 0.4, fontSize: 11, bold: true, color: C.white, align: "center", fontFace: "Calibri" });

    s.addText("「决策树把我们日常的 If-Then 推理变成算法」", {
      x: 5.5, y: 3.92, w: 4.05, h: 0.38, fontSize: 11, italic: true, color: C.gray, align: "center", fontFace: "Calibri",
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 18 · 活动4 — 老板大挑战
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "活动 4  ·  「老板大挑战」— 物理数据分类");
    addTag(s, "课堂活动", 0.4, 5.18, C.green, 1.4);
    addTimeChip(s, "⏱  15 min ★", C.orange);

    // 4 step cards
    const steps = [
      { n: "①", title: "首次分裂",   desc: "基于活动2的发现，选一张条件卡，将 20 张样本卡物理分成两堆", color: C.teal },
      { n: "②", title: "检查纯度",   desc: "观察每堆红/蓝比例——颜色越单一=分类效果越好（信息增益↑）", color: C.orange },
      { n: "③", title: "迭代循环",   desc: "对颜色不纯的卡堆继续选新的条件卡分裂，直到两类尽可能清晰", color: C.navy },
      { n: "④", title: "绘制树形图", desc: "在海报纸上画出分类路径 → 完成决策树「训练」！", color: C.green },
    ];

    steps.forEach((st, i) => {
      const x = 0.4 + i * 2.35;
      s.addShape("rect", { x, y: 1.05, w: 2.12, h: 3.0, fill: { color: C.white }, line: { color: st.color }, shadow: makeShadow(4, 1, 0.1) });
      s.addShape("rect", { x, y: 1.05, w: 2.12, h: 0.65, fill: { color: st.color }, line: { color: st.color } });
      s.addText(st.n,     { x: x + 0.05, y: 1.1,  w: 0.5,  h: 0.5, fontSize: 22, bold: true, color: C.white, align: "center", fontFace: "Calibri" });
      s.addText(st.title, { x: x + 0.56, y: 1.15, w: 1.5,  h: 0.45, fontSize: 14, bold: true, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0 });
      s.addText(st.desc,  { x: x + 0.1,  y: 1.82, w: 1.9,  h: 1.85, fontSize: 11.5, color: C.textDark, fontFace: "Calibri" });
      if (i < 3) {
        s.addShape("rect", { x: x + 2.17, y: 2.3, w: 0.18, h: 0.08, fill: { color: C.gray }, line: { color: C.gray } });
      }
    });

    // Bottom callout
    s.addShape("rect", { x: 0.4, y: 4.25, w: 9.2, h: 0.75, fill: { color: C.yellowLight }, line: { color: C.yellow, width: 1 } });
    s.addText("🏆  测试大考验：老师持有 5 张全新测试卡，各组用自己的决策树预测——准确率最高的小组赢得奖励！", {
      x: 0.55, y: 4.3, w: 9.0, h: 0.65, fontSize: 12, bold: true, color: "7B5800", fontFace: "Calibri",
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 19 · 活动5 — 巅峰对决与总结
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "活动 5  ·  巅峰对决与课程总结");
    addTag(s, "课堂活动", 0.4, 5.18, C.green, 1.4);
    addTimeChip(s, "⏱  8 min", C.green);

    // Left 2 blocks
    const leftBlocks = [
      {
        title: "🏆  测试集大考验",
        desc: "两组上台展示海报 → 老师逐张出示测试卡 → 各组套用自己的决策树预测 → 准确率高者获胜！",
        color: C.green,
      },
      {
        title: "💻  AI vs 人类对比",
        desc: "展示计算机真实生成的决策树，讨论人类和机器如何通过识别规律来学习和做决策。",
        color: C.teal,
      },
    ];
    leftBlocks.forEach((b, i) => {
      const y = 1.05 + i * 2.05;
      s.addShape("rect", { x: 0.4, y, w: 4.5, h: 1.85, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(4, 1, 0.08) });
      s.addShape("rect", { x: 0.4, y, w: 4.5, h: 0.47, fill: { color: b.color }, line: { color: b.color } });
      s.addText(b.title, { x: 0.5, y: y + 0.06, w: 4.3, h: 0.4, fontSize: 14, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });
      s.addText(b.desc,  { x: 0.55, y: y + 0.62, w: 4.25, h: 1.1, fontSize: 12, color: C.textDark, fontFace: "Calibri" });
    });

    // Right: extension examples
    s.addShape("rect", { x: 5.2, y: 1.05, w: 4.4, h: 3.85, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(5, 2, 0.1) });
    s.addShape("rect", { x: 5.2, y: 1.05, w: 4.4, h: 0.47, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText("🔭  拓展思考：生活中的决策树", { x: 5.25, y: 1.07, w: 4.3, h: 0.43, fontSize: 13, bold: true, color: C.white, fontFace: "Calibri", margin: 0 });

    const exts = [
      { icon: "📧", text: "电子邮件垃圾过滤（垃圾 / 正常分类）" },
      { icon: "🏥", text: "医疗疾病诊断（症状分类辅助决策）" },
      { icon: "🎬", text: "流媒体内容推荐（用户偏好分类）" },
      { icon: "🚦", text: "交通信号灯智能控制（流量预测）" },
      { icon: "💳", text: "银行风控反欺诈检测（交易分类）" },
    ];
    exts.forEach((e, i) => {
      s.addText(`${e.icon}  ${e.text}`, {
        x: 5.38, y: 1.65 + i * 0.62, w: 4.08, h: 0.54,
        fontSize: 12, color: C.textDark, fontFace: "Calibri",
      });
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 20 · 小组成员贡献
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    addHeader(s, "小组成员贡献  ·  Group Contributions");

    const members = [
      { name: "成员 A", role: "数据分析 & 可视化", pts: ["UCI 数据集清洗与处理", "Dashboard 可视化开发", "EDA 关键发现总结"],    color: C.teal },
      { name: "成员 B", role: "机器学习建模",      pts: ["五种模型训练与调优", "XGBoost 参数优化",    "模型性能评估报告"],      color: C.navy },
      { name: "成员 C", role: "课程设计 & 活动",   pts: ["STEM 课程方案设计",  "物理卡片材料制作",    "课堂活动流程规划"],       color: C.orange },
    ];

    members.forEach((m, i) => {
      const x = 0.4 + i * 3.15;
      s.addShape("rect", { x, y: 1.0, w: 2.95, h: 4.38, fill: { color: C.white }, line: { color: C.grayLight }, shadow: makeShadow(5, 2, 0.1) });
      s.addShape("rect", { x, y: 1.0, w: 2.95, h: 0.1, fill: { color: m.color }, line: { color: m.color } });
      s.addShape("ellipse", { x: x + 1.1, y: 1.18, w: 0.75, h: 0.75, fill: { color: m.color, transparency: 20 }, line: { color: m.color } });
      s.addText("👤", { x: x + 1.1, y: 1.2, w: 0.75, h: 0.7, fontSize: 22, align: "center" });
      s.addText(m.name, { x, y: 2.08, w: 2.95, h: 0.46, fontSize: 17, bold: true, color: C.textDark, align: "center", fontFace: "Calibri" });
      s.addText(m.role, { x, y: 2.52, w: 2.95, h: 0.35, fontSize: 11.5, color: m.color, align: "center", italic: true, fontFace: "Calibri" });
      s.addShape("rect", { x: x + 0.55, y: 2.95, w: 1.85, h: 0.03, fill: { color: C.grayLight }, line: { color: C.grayLight } });
      m.pts.forEach((pt, j) => {
        s.addText([{ text: pt, options: { bullet: true } }], {
          x: x + 0.2, y: 3.1 + j * 0.7, w: 2.6, h: 0.62,
          fontSize: 11, color: C.textDark, fontFace: "Calibri",
        });
      });
    });

    s.addText("请在提交前按实际情况修改姓名与贡献内容", {
      x: 0.4, y: 5.28, w: 9.2, h: 0.25,
      fontSize: 10, color: C.gray, italic: true, fontFace: "Calibri", align: "center",
    });
  }

  // ──────────────────────────────────────────────────────────
  // SLIDE 21 · 总结 & Q&A
  // ──────────────────────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.navyDark };

    // Decorative circles
    s.addShape("ellipse", { x: -1.5, y: -1.5, w: 5.5, h: 5.5, fill: { color: C.teal, transparency: 90 }, line: { color: C.teal, transparency: 90 } });
    s.addShape("ellipse", { x: 7.5,  y: 2.5,  w: 4.5, h: 4.5, fill: { color: C.orange, transparency: 92 }, line: { color: C.orange, transparency: 92 } });
    s.addShape("rect", { x: 0, y: 0, w: 0.1, h: 5.625, fill: { color: C.orange }, line: { color: C.orange } });

    s.addText("感谢聆听", {
      x: 0.5, y: 0.5, w: 9, h: 1.35,
      fontSize: 58, bold: true, color: C.white, fontFace: "Calibri", charSpacing: 5,
    });
    s.addText("Thank you for listening", {
      x: 0.5, y: 1.8, w: 9, h: 0.62,
      fontSize: 24, color: C.teal, fontFace: "Calibri",
    });

    // 4 summary chips
    const chips = [
      { icon: "📊", txt: "17K+ 数据记录驱动分析" },
      { icon: "🌲", txt: "决策树 · 5 种 ML 模型对比" },
      { icon: "🎓", txt: "中三 STEM 不插电课程设计" },
      { icon: "🎮", txt: "5 段式互动课堂活动" },
    ];
    chips.forEach((c, i) => {
      const x = 0.5 + i * 2.28;
      s.addShape("rect", { x, y: 2.62, w: 2.12, h: 0.65, fill: { color: C.teal, transparency: 75 }, line: { color: C.teal, transparency: 65 } });
      s.addText(`${c.icon}  ${c.txt}`, {
        x, y: 2.66, w: 2.12, h: 0.56, fontSize: 11, color: C.white, align: "center", fontFace: "Calibri",
      });
    });

    // Q&A bar
    s.addShape("rect", { x: 0.5, y: 3.55, w: 9, h: 1.0, fill: { color: C.teal, transparency: 82 }, line: { color: C.teal, transparency: 72 } });
    s.addText("Q & A  ·  欢迎提问", {
      x: 0.5, y: 3.62, w: 9, h: 0.85,
      fontSize: 30, bold: true, color: C.white, align: "center", fontFace: "Calibri", charSpacing: 3,
    });

    s.addText("INT6068  Neural Networks and Deep Learning  ·  Group Project", {
      x: 0.5, y: 4.75, w: 9, h: 0.38,
      fontSize: 11, color: "4A6FA5", align: "center", fontFace: "Calibri", italic: true,
    });
  }

  // ──────────────────────────────────────────────────────────
  await pres.writeFile({ fileName: "/storage/Project/Data_Mining_Group/presentation.pptx" });
  console.log("✅  Saved: /storage/Project/Data_Mining_Group/presentation.pptx");
}

main().catch(err => { console.error(err); process.exit(1); });
