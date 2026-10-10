// ARUNA full paper (English) — A4, Arial 12, single spacing, margins L4 R3 T3 B3 cm, justified.
//   node design/competition/paper.js   ->  ARUNA_FullPaper.docx
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  ShadingType, BorderStyle, Footer, PageNumber, HeadingLevel, VerticalAlign, LevelFormat, PageBreak,
} = require("docx");

const FIG = path.join(__dirname, "fig");
const CM = 567; // dxa per cm
const TEXT_W = Math.round((21 - 7) * CM); // 7938 dxa
const FONT = "Arial";
const PT = 24; // 12 pt (half-points)

// ---------- helpers ----------
const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || PT, bold: o.b, italics: o.i,
  highlight: o.ph ? "yellow" : undefined, superScript: o.sup, subScript: o.sub, color: o.color });
// "teks dengan **tebal**, *miring*, [[placeholder]], CH_4_ (subscript)"
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|\[\[[^\]]+\]\]|_[^_]+_)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(run(text.slice(last, m.index), base));
    const t = m[0];
    if (t.startsWith("**")) out.push(run(t.slice(2, -2), { ...base, b: true }));
    else if (t.startsWith("[[")) out.push(run("[" + t.slice(2, -2) + "]", { ...base, ph: true }));
    else if (t.startsWith("_")) out.push(run(t.slice(1, -1), { ...base, sub: true }));
    else out.push(run(t.slice(1, -1), { ...base, i: true }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(run(text.slice(last), base));
  return out;
}
const P = (t, o = {}) => new Paragraph({ children: runs(t, o), alignment: o.align || AlignmentType.JUSTIFIED,
  spacing: { line: 240, after: o.after ?? 120, before: o.before || 0 }, indent: o.indent ? { firstLine: 567 } : undefined,
  keepNext: o.keepNext });
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [run(t, { b: true })],
  spacing: { before: 240, after: 120, line: 240 }, keepNext: true });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [run(t, { b: true })],
  spacing: { before: 160, after: 80, line: 240 }, keepNext: true });
const bullet = (t) => new Paragraph({ children: runs(t), numbering: { reference: "bul", level: 0 },
  alignment: AlignmentType.JUSTIFIED, spacing: { line: 240, after: 60 } });
const numbered = (t) => new Paragraph({ children: runs(t), numbering: { reference: "num", level: 0 },
  alignment: AlignmentType.JUSTIFIED, spacing: { line: 240, after: 60 } });

function figure(file, widthPx, caption) {
  const buf = fs.readFileSync(path.join(FIG, file));
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: buf, transformation: { width: widthPx, height: Math.round(widthPx * h / w) } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160, line: 240 }, children: runs(caption, { size: 20 }) }),
  ];
}
const border = { style: BorderStyle.SINGLE, size: 4, color: "8A9A92" };
function table(caption, header, rows, widthsCm) {
  const widths = widthsCm.map((c) => Math.round(c * CM));
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, head) => new TableCell({
    width: { size: widths[i], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
    shading: head ? { type: ShadingType.CLEAR, color: "auto", fill: "E3F3EA" } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 90 },
    borders: { top: border, bottom: border, left: border, right: border },
    children: [new Paragraph({ spacing: { line: 240 }, alignment: i === 0 ? AlignmentType.LEFT : AlignmentType.CENTER,
      children: runs(t, { size: 20, b: head }) })],
  });
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60, line: 240 },
      children: runs(caption, { size: 20 }) }),
    new Table({ width: { size: total, type: WidthType.DXA }, columnWidths: widths, alignment: AlignmentType.CENTER,
      rows: [new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, i, true)) }),
        ...rows.map((r) => new TableRow({ children: r.map((t, i) => cell(t, i, false)) }))] }),
    new Paragraph({ spacing: { after: 120 }, children: [] }),
  ];
}

// ---------- content ----------
const C = [];
C.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120, line: 240 }, children: [
  run("ARUNA: AN IoT-ENABLED SMART HOME BIODIGESTER FOR CONVERTING HOUSEHOLD FOOD WASTE INTO BIOGAS, LIQUID FERTILIZER AND COMPOST", { b: true })] }));
C.push(P("[[Author 1]]¹, [[Author 2]]¹, [[Author 3]]², [[Supervisor]]¹", { align: AlignmentType.CENTER, after: 40 }));
C.push(P("¹[[Department, Institution, City, Indonesia]]   ²[[Department, Institution, City, Indonesia]]", { align: AlignmentType.CENTER, after: 40, size: 20 }));
C.push(P("Corresponding author: [[email address]]", { align: AlignmentType.CENTER, after: 200, size: 20 }));

C.push(P("**Abstract**", { align: AlignmentType.LEFT, after: 60 }));
C.push(P("Food waste is the largest component of municipal solid waste in Indonesia and a significant source of methane when it decomposes in landfills. Household-scale treatment options remain limited: composting does not recover energy, electric food recyclers consume energy, and conventional biogas digesters are bulky, manure-oriented and unmonitored. This study develops ARUNA (Anaerobic Recycling and Upcycling of Nutrient-rich food wAste), a waist-high (44 × 44 × 112 cm) smart biodigester that converts household food waste into biogas for cooking, liquid fertilizer and solid compost. The device integrates a twin-shaft shredder, an automatic stirrer and sensors for temperature, pH, methane composition (NDIR), slurry level and input weight controlled by an ESP32-S3 microcontroller, which streams data to a Firebase cloud backend and a progressive web application with harvest notifications and an AI educator. The research follows a Research and Development (R&D) approach using the 4D model (Define, Design, Develop, Disseminate). Performance is evaluated through laboratory digestion tests (temperature, pH, CH_4_ content and daily biogas volume) and a household field test with usability measured by the System Usability Scale (SUS). Design calculations based on mass balance and literature kinetics predict 214 L of biogas per day at the nominal load of 1.5 kg/day (about 43 minutes of cooking or 3.0 kg of LPG per month) and 0.72 t CO_2_e avoided per year. [[Summarise the measured results here: CH4 content, biogas yield per kg VS, SUS score.]] The design shows that anaerobic digestion can be made compact, guided and observable for ordinary households, supporting SDGs 7, 11, 12 and 13.", { after: 80 }));
C.push(P("**Keywords:** anaerobic digestion; food waste; household biogas; Internet of Things; smart biodigester", { after: 200 }));

// ---- 1
C.push(H1("1. INTRODUCTION"));
C.push(H2("1.1 Background"));
C.push(P("Food loss and waste (FLW) is a global problem with direct environmental, economic and social consequences. The UNEP Food Waste Index Report estimates that households generate the largest share of food waste worldwide (UNEP, 2021). In Indonesia, the National Waste Management Information System (SIPSN) of the Ministry of Environment and Forestry reports that food waste accounts for roughly 40% of municipal solid waste by composition (KLHK, 2023). The national FLW study by Bappenas estimated that Indonesia wasted 23–48 million tonnes of food per year in 2000–2019, equivalent to 115–184 kg per person per year, with an economic loss of IDR 213–551 trillion per year (4–5% of GDP) and cumulative emissions of about 1,702.9 Mt CO_2_-eq (Bappenas, 2021).", { indent: true }));
C.push(P("Most household food waste is mixed with other refuse and sent to landfills, where it decomposes anaerobically and releases methane, a greenhouse gas far more potent than carbon dioxide over a 100-year horizon. At the same time, food waste is rich in readily biodegradable organic matter and nutrients, which makes it an excellent feedstock for anaerobic digestion (AD) that produces biogas and nutrient-rich digestate (Zhang et al., 2007; Xu et al., 2018). Treating food waste at its source, in the household kitchen, avoids collection and transport, recovers energy for cooking and returns nutrients to home gardens.", { indent: true }));
C.push(H2("1.2 Problem Statement"));
C.push(P("Although household biogas technology is well established in rural areas with livestock manure, food-waste digestion at home faces practical barriers: (1) conventional digesters are large and require outdoor space; (2) the process is sensitive to temperature, pH and loading rate and can fail through acidification when operated without knowledge or monitoring (Chen et al., 2008); (3) users cannot see the state of the process and do not know when gas, fertilizer or compost are ready; and (4) food waste requires size reduction and mixing for stable digestion. Accordingly, this research addresses the question: *how can a compact, sensor-guided biodigester be designed so that ordinary households can safely convert daily food waste into biogas, liquid fertilizer and compost?*", { indent: true }));
C.push(H2("1.3 Objectives"));
C.push(numbered("To design a compact vertical biodigester (ARUNA) with integrated shredding, stirring and three separated outputs (biogas, liquid fertilizer and compost)."));
C.push(numbered("To develop an IoT monitoring system and companion web application that report process conditions and harvest readiness in real time."));
C.push(numbered("To evaluate digestion performance (temperature, pH, CH_4_ content and biogas volume) and user acceptance (SUS) in laboratory and household settings."));
C.push(H2("1.4 Significance"));
C.push(P("ARUNA contributes to SDG 7 (affordable and clean energy, target 7.1) through clean cooking gas, SDG 11 (sustainable cities, target 11.6) by reducing municipal waste, SDG 12 (responsible consumption and production, targets 12.3 and 12.5) by halving food waste and recycling it at source, and SDG 13 (climate action, target 13.2) by avoiding landfill methane (United Nations, 2015).", { indent: true }));

// ---- 2
C.push(H1("2. LITERATURE REVIEW"));
C.push(H2("2.1 Anaerobic Digestion of Food Waste"));
C.push(P("Anaerobic digestion converts organic matter into biogas (mainly CH_4_ and CO_2_) through four sequential stages: hydrolysis, acidogenesis, acetogenesis and methanogenesis (Appels et al., 2008). Food waste has high volatile solids and high biodegradability, yielding substantial methane potential, but its rapid hydrolysis can cause accumulation of volatile fatty acids, a drop in pH and process inhibition (Zhang et al., 2007; Chen et al., 2008). Mesophilic conditions (around 30–40 °C), near-neutral pH (approximately 6.8–7.5), regular mixing and controlled organic loading rate are therefore critical to stable operation (Mata-Alvarez et al., 2000; Weiland, 2010). Typical biogas from food waste contains about 50–70% methane, which is sufficient for direct combustion in cooking stoves (Paritosh et al., 2017; Xu et al., 2018).", { indent: true }));
C.push(H2("2.2 Household-Scale Digesters"));
C.push(P("Household biogas digesters such as fixed-dome, floating-drum and flexible-bag designs have been widely deployed in developing countries, mainly fed with animal manure (Rajendran et al., 2012). In Indonesia, the BIRU (Biogas Rumah) programme promoted fixed-dome digesters for farming households. These systems are effective but require significant space, construction work and manure supply, which are uncommon in urban kitchens. Commercial home digesters for food waste exist, yet they generally rely on users to judge process health visually and offer limited real-time information. Meanwhile, electric food recyclers dehydrate and grind food waste into a soil amendment but consume electricity and do not recover energy (Kumar & Samadder, 2017).", { indent: true }));
C.push(H2("2.3 Monitoring and Usability"));
C.push(P("Low-cost microcontrollers and cloud platforms now make continuous monitoring feasible at household scale. Temperature, pH, gas composition and level measurements provide early warning of process imbalance, while mobile interfaces can translate these values into simple instructions. Because adoption depends on ease of use, usability is commonly assessed with the System Usability Scale (SUS), a ten-item questionnaire producing a score from 0 to 100, where scores above 68 are considered above average (Brooke, 1996; Bangor et al., 2009).", { indent: true }));
C.push(H2("2.4 State of the Art and Research Gap"));
C.push(P("Table 1 compares existing approaches. No single household option combines food-waste input, energy recovery, fertilizer output, live monitoring and a footprint that fits a kitchen. ARUNA targets this gap.", { indent: true, keepNext: true }));
C.push(...table("Table 1. Comparison of household food-waste treatment approaches",
  ["Approach", "Food waste", "Energy", "Fertilizer", "Live monitoring", "Fits a home"],
  [["Compost bin / Takakura", "Yes", "No", "Yes", "No", "Yes"],
   ["Electric food recycler", "Yes", "No", "Partly", "Partly", "Yes"],
   ["Home biogas bag", "Yes", "Yes", "Yes", "No", "Partly"],
   ["Fixed-dome digester (BIRU)", "Partly", "Yes", "Yes", "No", "No"],
   ["**ARUNA (this study)**", "**Yes**", "**Yes**", "**Yes**", "**Yes**", "**Yes**"]],
  [4.3, 1.9, 1.5, 1.9, 2.3, 1.9]));

// ---- 3
C.push(H1("3. RESEARCH METHODS"));
C.push(H2("3.1 Research Design"));
C.push(P("This study uses a Research and Development (R&D) design following the 4D model of Thiagarajan et al. (1974), adapted for product engineering (Figure 1). The **Define** stage audits household food waste and user needs. The **Design** stage produces the 3D model, component sizing and IoT/application architecture. The **Develop** stage builds the prototype and performs laboratory digestion tests and expert validation. The **Disseminate** stage tests the device in households and measures usability.", { indent: true }));
C.push(...figure("fig_method_4d.png", 520, "Figure 1. Research flow based on the 4D model"));
C.push(H2("3.2 Hardware Design"));
C.push(P("ARUNA is a vertical, gravity-fed unit (Figure 2). Food waste enters through a top lid (opened by hand or foot pedal), is weighed by a load cell and reduced by a twin-shaft shredder before entering the digester tank, where an automatic stirrer mixes the slurry every two hours. Biogas accumulates above the slurry and leaves through a valve with a pressure gauge to a household stove. Liquid digestate is drawn through a tap into a bottle in the front niche, and solid digestate settles into the bottom compost drawer. The main components are listed in Table 2.", { indent: true }));
C.push(...figure("fig_hardware_xray.png", 520, "Figure 2. ARUNA hardware layout (x-ray view of the 3D model)"));
C.push(...table("Table 2. Main hardware components",
  ["Component", "Specification", "Function"],
  [["Controller", "ESP32-S3, Wi-Fi + BLE", "Data acquisition, control, connectivity"],
   ["Temperature sensor", "DS18B20, ±0.5 °C", "Slurry temperature (°C)"],
   ["pH sensor", "Analog pH probe", "Acidity of slurry"],
   ["Methane composition", "NDIR (Winsen MH-440D), 0–100 % vol", "CH4 fraction of biogas"],
   ["Leak sensor", "MQ-4, 300–10,000 ppm", "Safety alarm near the unit"],
   ["Level sensor", "Ultrasonic", "Slurry level / fill ratio"],
   ["Load cell", "HX711 amplifier", "Weight of each input"],
   ["Shredder & stirrer", "DC gear motors", "Size reduction and mixing"],
   ["Display", "7\" touch panel", "Local status and controls"]],
  [3.4, 3.6, 6.0]));
C.push(H2("3.3 Software Design"));
C.push(P("The system architecture is shown in Figure 3. Sensor readings are sampled every [[15]] minutes, sent by the ESP32-S3 to Firebase Realtime Database, and displayed in a progressive web application (PWA) that also works on low-end phones. Firestore stores user profiles, and Firebase Authentication secures access. Bluetooth Low Energy (BLE) allows offline provisioning of Wi-Fi credentials. An AI educator answers user questions using the device's own data (e.g., explaining low gas pressure). The application is deployed at https://aruna-id.web.app.", { indent: true }));
C.push(...figure("fig_architecture.png", 520, "Figure 3. ARUNA IoT and software architecture"));
C.push(H2("3.4 Testing Procedure"));
C.push(P("**Laboratory test.** The prototype is inoculated with [[inoculum source, e.g., digestate from an active biogas plant]] and fed with [[x]] kg/day of mixed household food waste for [[n]] days at ambient temperature. Temperature, pH, CH_4_ content and daily biogas volume are recorded; CH_4_ readings are cross-checked with [[reference instrument, e.g., portable gas analyser or GC]].", { indent: true }));
C.push(P("**Field test.** [[n]] households in [[location]] operate ARUNA for [[30]] days. Each household records daily food-waste input (automatically weighed), stove use and harvested fertilizer volume. After the test, participants complete the SUS questionnaire and a short interview. Measured parameters and targets are summarised in Table 3.", { indent: true }));
C.push(...table("Table 3. Measured parameters, instruments and targets",
  ["Parameter", "Instrument", "Target / reference"],
  [["Temperature", "DS18B20", "30–38 °C (mesophilic)"],
   ["pH", "pH probe (calibrated)", "6.8–7.5"],
   ["CH4 content", "NDIR sensor + [[reference analyser]]", "≥ 50%"],
   ["Biogas volume", "Gas flow meter", "[[target L/day]]"],
   ["Fertilizer", "Lab analysis (N, P, K)", "[[standard used]]"],
   ["Usability", "SUS questionnaire", "≥ 68 (above average)"]],
  [3.4, 4.6, 5.0]));
C.push(H2("3.5 Design Calculation"));
C.push(P("The digester was sized from a daily mass balance. With food-waste input F, total solids TS = 25 % and VS/TS = 90 % (Zhang et al., 2007; Xu et al., 2018), the organic loading rate is OLR = F·TS·(VS/TS)/V_w_ and the hydraulic retention time is HRT = V_w_/Q, where V_w_ = 100 L and Q is the diluted feed flow (1:1 water). Methane production assumes an in-situ yield of 0.38 m³ CH_4_/kg VS, below the experimental BMP of about 390 mL CH_4_/g VS and the Buswell theoretical value of about 643 mL CH_4_/g VS (Buswell & Mueller, 1952). Energy is E = V_CH4_·LHV (35.8 MJ/m³), cooking time uses a stove demand of 0.30 m³/h, and avoided landfill methane follows the IPCC (2006) first-order-decay parameters (DOC 0.15, DOC_f_ 0.5, MCF 0.8, F 0.5) with GWP_100_ = 28. Methane kinetics will be fitted with the modified Gompertz model (Zwietering et al., 1990). Table 4 gives the results for three load scenarios.", { indent: true }));
C.push(...table("Table 4. Design calculation for three load scenarios",
  ["Parameter", "Household of 4", "Nominal", "Peak"],
  [["Food-waste input (kg/d)", "0.58", "1.5", "3.0"],
   ["OLR (kg VS/m³·d)", "1.3", "3.4", "6.8"],
   ["HRT (d)", "88", "34", "17"],
   ["Biogas (L/d, 60 % CH4)", "83", "214", "428"],
   ["Cooking time (min/d)", "17", "43", "86"],
   ["LPG equivalent (kg/month)", "1.2", "3.0", "6.0"],
   ["Avoided GHG (t CO2e/yr)", "0.28", "0.72", "1.44"]],
  [5.2, 2.8, 2.4, 2.4]));
C.push(H2("3.6 Data Analysis"));
C.push(P("Specific biogas yield is calculated as the cumulative biogas volume divided by the mass of volatile solids added (L/kg VS). Daily values are presented as mean ± standard deviation. The SUS score is computed following Brooke (1996): for odd items the contribution is the response minus 1, for even items it is 5 minus the response, and the sum is multiplied by 2.5. Results are compared against the targets in Table 3 and against values reported in the literature.", { indent: true }));

// ---- 4
C.push(H1("4. RESULTS AND DISCUSSION"));
C.push(H2("4.1 Prototype Design"));
C.push(P("The Design and Develop stages produced a complete 3D model and prototype specification (Figure 4, Table 5). The vertical layout keeps the footprint to 44 × 44 cm so that the device fits in a kitchen corner, and the lid height of 112 cm allows waste to be added at waist level. Each user step is labelled on the front of the device (1 add waste, 2 take liquid fertilizer, 3 take compost), and the biogas outlet is placed on the side, away from the user's hands.", { indent: true }));
C.push(...figure("fig_product.png", 230, "Figure 4. ARUNA prototype design (3D render)"));
C.push(...table("Table 5. Prototype specification",
  ["Item", "Value"],
  [["Dimensions (W × D × H)", "44 × 44 × 112 cm, on lockable castors"],
   ["Food-waste capacity", "1.5 kg/day nominal; 3 kg/day short peaks"],
   ["Digester working volume", "100 L"],
   ["Hydraulic retention time", "≈ 34 days at nominal load"],
   ["Organic loading rate", "≈ 3.4 kg VS/m³·d at nominal load"],
   ["Power", "≈ 38 W average (design estimate)"],
   ["Connectivity", "Wi-Fi, Bluetooth Low Energy"],
   ["Outputs", "Biogas (side valve), liquid fertilizer (tap), compost (drawer)"]],
  [5.0, 8.0]));
C.push(H2("4.2 Software Implementation"));
C.push(P("The companion application has been implemented and deployed. It provides (1) a home screen summarising machine status, four live sensor values and harvest readiness; (2) a monitoring screen with 24-hour, 7-day and 30-day charts showing the ideal range; (3) an AI educator that answers questions using the user's own sensor data; and (4) a device screen for Wi-Fi/BLE connection and automation settings (Figure 5). Displaying ideal ranges directly on the charts lets users judge whether the process is healthy without memorising values.", { indent: true }));
C.push(...figure("fig_app.png", 520, "Figure 5. Companion web application (interface in Bahasa Indonesia)"));
C.push(H2("4.3 Digestion Performance"));
C.push(P("[[Insert measured laboratory results here.]] Figure 6 shows the expected course of CH_4_ content and temperature over a 14-day digestion cycle, derived from the design targets and typical food-waste AD behaviour in the literature; it must be replaced with the measured curve. In a typical start-up, CH_4_ content remains low during the first days while hydrolysis and acidogenesis dominate and rises once methanogenic activity is established (Appels et al., 2008; Xu et al., 2018).", { indent: true }));
C.push(...figure("fig_results_ch4.png", 500, "Figure 6. Expected CH4 content and temperature during digestion (illustrative target curve; replace with measured data)"));
C.push(...table("Table 6. Laboratory and field results (to be completed)",
  ["Parameter", "Measured (mean ± SD)", "Target", "Status"],
  [["Temperature (°C)", "[[value]]", "30–38", "[[met / not met]]"],
   ["pH", "[[value]]", "6.8–7.5", "[[ ]]"],
   ["CH4 content (%)", "[[value]]", "≥ 50", "[[ ]]"],
   ["Biogas (L/day)", "[[value]]", "[[target]]", "[[ ]]"],
   ["Specific yield (L/kg VS)", "[[value]]", "literature range", "[[ ]]"],
   ["Food waste diverted (kg/household/day)", "[[value]]", "≤ 3", "[[ ]]"],
   ["SUS score", "[[value]]", "≥ 68", "[[ ]]"]],
  [4.8, 3.3, 2.6, 2.3]));
C.push(H2("4.4 Discussion"));
C.push(P("[[Interpret the measured results against the targets.]] Three design decisions are expected to matter most. First, shredding increases the surface area of food waste and accelerates hydrolysis, which shortens start-up but raises the risk of acid accumulation; the pH sensor and app warnings are intended to let users pause feeding before the process fails (Chen et al., 2008). Second, scheduled stirring every two hours prevents scum formation and keeps temperature uniform, which supports stable methanogenesis (Weiland, 2010). Third, translating sensor values into plain-language status and harvest notifications addresses the main non-technical barrier, namely that users cannot see what happens inside a digester. [[Discuss SUS score and interview findings.]]", { indent: true }));
C.push(P("**Limitations.** The prototype has been evaluated at a single scale and for a limited number of cycles. Low-cost NDIR sensors require periodic calibration against a reference gas analyser, and ambient temperature in Indonesia may vary between regions and seasons. Long-term durability, safety certification of the gas line and fertilizer quality standards require further study.", { indent: true }));

// ---- 5
C.push(H1("5. CONCLUSION"));
C.push(H2("5.1 Conclusion"));
C.push(P("This study designed and developed ARUNA, a compact IoT-enabled household biodigester that converts food waste into biogas, liquid fertilizer and compost. The vertical gravity-fed design with integrated shredder, stirrer and five sensors fits in a kitchen corner, while the deployed web application turns sensor data into simple status, alerts and guidance. [[Add the main quantitative findings: CH4 content, biogas yield, food waste diverted and SUS score.]] The results indicate that household anaerobic digestion can be made compact, guided and observable, contributing to SDGs 7, 11, 12 and 13.", { indent: true }));
C.push(H2("5.2 Recommendations"));
C.push(bullet("Validate methane readings with a calibrated gas analyser and extend testing to several cycles and climates."));
C.push(bullet("Add on-device AI recognition of food-waste type to warn users about unsuitable inputs (bones, oil, plastics)."));
C.push(bullet("Power the controller with a small solar panel and reduce standby energy use."));
C.push(bullet("Pilot ARUNA in school kitchens of the free nutritious meal (MBG) programme and evaluate carbon-credit accounting at community scale."));

// ---- References (APA 7)
const REFS = [
  "Appels, L., Baeyens, J., Degrève, J., & Dewil, R. (2008). Principles and potential of the anaerobic digestion of waste-activated sludge. *Progress in Energy and Combustion Science, 34*(6), 755–781.",
  "Bangor, A., Kortum, P., & Miller, J. (2009). Determining what individual SUS scores mean: Adding an adjective rating scale. *Journal of Usability Studies, 4*(3), 114–123.",
  "Bappenas. (2021). *Food loss and waste in Indonesia: Supporting the implementation of circular economy and low carbon development*. Ministry of National Development Planning/Bappenas.",
  "Brooke, J. (1996). SUS: A \"quick and dirty\" usability scale. In P. W. Jordan, B. Thomas, B. A. Weerdmeester, & I. L. McClelland (Eds.), *Usability evaluation in industry* (pp. 189–194). Taylor & Francis.",
  "Buswell, A. M., & Mueller, H. F. (1952). Mechanism of methane fermentation. *Industrial & Engineering Chemistry, 44*(3), 550–552.",
  "Chen, Y., Cheng, J. J., & Creamer, K. S. (2008). Inhibition of anaerobic digestion process: A review. *Bioresource Technology, 99*(10), 4044–4064.",
  "IPCC. (2006). *2006 IPCC guidelines for national greenhouse gas inventories, Volume 5: Waste*. Institute for Global Environmental Strategies.",
  "KLHK. (2023). *Sistem Informasi Pengelolaan Sampah Nasional (SIPSN): Komposisi sampah*. Ministry of Environment and Forestry of the Republic of Indonesia. https://sipsn.menlhk.go.id",
  "Kumar, A., & Samadder, S. R. (2017). A review on technological options of waste to energy for effective management of municipal solid waste. *Waste Management, 69*, 407–422.",
  "Mata-Alvarez, J., Macé, S., & Llabrés, P. (2000). Anaerobic digestion of organic solid wastes. An overview of research achievements and perspectives. *Bioresource Technology, 74*(1), 3–16.",
  "Paritosh, K., Kushwaha, S. K., Yadav, M., Pareek, N., Chawade, A., & Vivekanand, V. (2017). Food waste to energy: An overview of sustainable approaches for food waste management and nutrient recycling. *BioMed Research International, 2017*, 2370927.",
  "Rajendran, K., Aslanzadeh, S., & Taherzadeh, M. J. (2012). Household biogas digesters: A review. *Energies, 5*(8), 2911–2942.",
  "Thiagarajan, S., Semmel, D. S., & Semmel, M. I. (1974). *Instructional development for training teachers of exceptional children: A sourcebook*. Indiana University.",
  "UNEP. (2021). *Food waste index report 2021*. United Nations Environment Programme.",
  "UNEP. (2024). *Food waste index report 2024*. United Nations Environment Programme.",
  "United Nations. (2015). *Transforming our world: The 2030 Agenda for Sustainable Development* (A/RES/70/1).",
  "Weiland, P. (2010). Biogas production: Current state and perspectives. *Applied Microbiology and Biotechnology, 85*(4), 849–860.",
  "Xu, F., Li, Y., Ge, X., Yang, L., & Li, Y. (2018). Anaerobic digestion of food waste: Challenges and opportunities. *Bioresource Technology, 247*, 1047–1058.",
  "Zhang, R., El-Mashad, H. M., Hartman, K., Wang, F., Liu, G., Choate, C., & Gamble, P. (2007). Characterization of food waste as feedstock for anaerobic digestion. *Bioresource Technology, 98*(4), 929–935.",
  "Zwietering, M. H., Jongenburger, I., Rombouts, F. M., & van 't Riet, K. (1990). Modeling of the bacterial growth curve. *Applied and Environmental Microbiology, 56*(6), 1875–1881.",
];
C.push(new Paragraph({ children: [new PageBreak()] }));
C.push(H1("REFERENCES"));
for (const r of REFS) C.push(new Paragraph({ children: runs(r), alignment: AlignmentType.JUSTIFIED,
  spacing: { line: 240, after: 100 }, indent: { left: 567, hanging: 567 } }));

const doc = new Document({
  creator: "ARUNA Team", title: "ARUNA Full Paper",
  styles: {
    default: { document: { run: { font: FONT, size: PT } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: PT, bold: true, color: "000000" }, paragraph: { outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { font: FONT, size: PT, bold: true, color: "000000" }, paragraph: { outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 567, hanging: 283 } } } }] },
    { reference: "num", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 567, hanging: 340 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { left: 4 * CM, right: 3 * CM, top: 3 * CM, bottom: 3 * CM, header: 708, footer: 708 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children: C,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(path.join(__dirname, "ARUNA_FullPaper.docx"), b); console.log("docx ok", b.length); });
