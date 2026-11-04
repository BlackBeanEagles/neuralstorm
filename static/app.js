const $ = (selector) => document.querySelector(selector);

const locationSelect = $("#location");
const locationDescription = $("#location-description");
const locationSource = $("#location-source");
const languageSelect = $("#language");
const fileInput = $("#file-input");
const uploadZone = $("#upload-zone");
const preview = $("#preview");
const scanButton = $("#scan-button");
const statusLine = $("#status");
const textForm = $("#text-form");
const textInput = $("#text-input");
const textStatus = $("#text-status");
const quickItems = $("#quick-items");
const resultEmpty = $("#result-empty");
const resultContent = $("#result-content");
const prepBox = $("#prep-box");
const listenButton = $("#listen-button");
const qrOpen = $("#qr-open");
const qrPanel = $("#qr-panel");
const qrImage = $("#qr-image");
const qrUrl = $("#qr-url");
const feedbackBox = $("#feedback-box");
const demoMode = new URLSearchParams(location.search).get("demo") === "1";

const copy = {
  en: {
    languageLabel: "Language",
    heroEyebrow: "Small action. Cleaner sorting.",
    heroLineOne: "Know where",
    heroLineTwo: "it ",
    heroEm: "goes.",
    heroBody: "Take a photo or choose an item. Get a sorting step based on the guidance for your area.",
    heroCta: "Start sorting",
    artItem: "Plastic bottle",
    artAdvice: "Check local rules",
    artCaption: "SCAN → SORT → DONE",
    scanEyebrow: "GET STARTED",
    scanTitle: "Sort an item",
    locationLabel: "Guidance area",
    locationHint: "Local collection rules may differ",
    itemLabel: "Your item",
    itemHint: "One item per photo",
    uploadTitle: "Take a photo or upload one",
    uploadSubtitle: "JPEG, PNG or WebP · up to 10 MB",
    unsupportedWarning:
      "Batteries, medicines, sanitary waste, and e-waste may need special handling. Check local instructions.",
    textTitle: "No camera? Type your item",
    textHint: "Choose a known item from the suggestions. No photo is sent.",
    textLabel: "Item name",
    textButton: "Look up",
    quickTitle: "Or choose a common item",
    textPlaceholder: "e.g. plastic bottle or food scraps",
    textNoMatch: "No clear match. Try plastic bottle, cardboard box, food scraps, or battery.",
    textUnavailable: "This profile has no rule for that item. Choose the India profile or check local guidance.",
    textReady: "Item selected. Check the preparation questions if shown.",
    resultKicker: "SORTING STEP",
    emptyTitle: "Your answer appears here",
    emptyHint: "Scan or type one item to see its material and sorting step.",
    takeTo: "SORT AS",
    differentMaterial: "Is the material different?",
    prepTitle: "Quick preparation check",
    emptyQuestion: "Is the item empty?",
    cleanQuestion: "Is it free of food and liquid?",
    yes: "Yes",
    noUnsure: "No / unsure",
    prepWait: "Answer these before following a sorting step.",
    prepReady: "Ready to follow the guidance below.",
    prepFix: "Empty and clean it if possible. If you cannot, check local instructions before sorting.",
    prepPaper: "Food-soiled paper or cardboard needs a local check before sorting.",
    prepCaveat: "BinWise cannot verify hidden food or liquid. Follow local collection rules.",
    listen: "Read advice aloud",
    stop: "Stop reading",
    speechUnavailable: "Read-aloud is unavailable in this browser.",
    officialSource: "View official rules",
    changePhoto: "Change photo",
    scanButton: "Check this item",
    scanning: "Looking at the item",
    chooseItem: "Choose an item to start.",
    ready: "Ready to scan.",
    analysing: "Analysing the photo…",
    scanComplete: "Item recognised. Check its preparation before sorting.",
    confirmMaterial: "Please confirm the material.",
    unsupportedStatus: "No automatic suggestion. Check the item and local rules.",
    locationChanged: "Guidance area changed. Choose an item again.",
    invalidFile: "Choose a JPEG, PNG, or WebP image.",
    largeFile: "Choose an image under 10 MB.",
    noFile: "Choose an image first.",
    scanFailed: "The scan failed.",
    loadFailed: "Guidance could not load. Please refresh the page.",
    guidanceFailed: "Could not load guidance.",
    qualityTitle: "Please retake the photo",
    too_small: "The photo is too small. Move closer and try again.",
    too_dark: "The photo is too dark. Add light and try again.",
    too_blurry: "The photo is too blurry or plain. Hold steady and show one item clearly.",
    photoSuggestion: "Photo suggestion",
    needsCheck: "Check item type",
    noAuto: "Needs your check",
    selectedByYou: "Selected by you",
    confirmedByYou: "Confirmed by you",
    noBin: "No bin suggestion",
    somethingElse: "Something else",
    outsideScope: "This item may need special handling. Choose its type below or check local instructions.",
    tentative: "We are not sure what this is. Choose the right material below.",
    recognised: "Check the item and answer any preparation questions below.",
    textSelected: "You selected this item from the text list.",
    manualSelected: "You confirmed this material.",
    checkYourself: "Please check the item yourself.",
    helpCheck: "Help us check this one.",
    unsupportedHelp: "Select a known item type below, or choose Something else and follow local rules.",
    confirmHelp: "Choose the correct material below before following guidance.",
    otherIntro: "BinWise cannot choose a category for this item. Check local instructions or ask your collection provider.",
    otherDisclaimer: "Do not place batteries, e-waste, sanitary waste, or unfamiliar items in a regular bin based on a photo guess.",
    noSuggestion: "No automatic bin suggestion for this item.",
    guidanceUpdated: "Guidance updated.",
    qrOpen: "Show guide QR code",
    qrTitle: "Share this guide",
    qrLinkLabel: "Link encoded in the QR code",
    qrLocalWarning: "This preview link works only on this computer. Open a shared version of BinWise before printing a QR card.",
    qrCopy: "Copy link",
    qrDownload: "Download QR",
    qrPrint: "Print card",
    qrCopied: "Link copied.",
    qrCopyFailed: "Select and copy the link above.",
    qrFailed: "Could not create the QR code.",
    feedbackTitle: "Was this advice correct?",
    feedbackPrivacy: "Help us spot mistakes. No photo or name is saved with feedback.",
    feedbackCorrect: "Yes, correct",
    feedbackMaterial: "Wrong material",
    feedbackRule: "Local rule differs",
    feedbackChoose: "What material is it?",
    feedbackSend: "Send correction",
    feedbackSelect: "Choose a different material to send a correction.",
    feedbackSaved: "Thanks. Your feedback was saved.",
    feedbackFailed: "Feedback could not be saved. Please try again.",
    howEyebrow: "A SIMPLE WAY TO SORT",
    howTitle: "How to use BinWise",
    howOneTitle: "Choose one item",
    howOneBody: "Take a clear photo or pick a common item from the list.",
    howTwoTitle: "Check its condition",
    howTwoBody: "Tell us if the item is empty and free of food or liquid.",
    howThreeTitle: "Follow the guide",
    howThreeBody: "Read the sorting step, then check local collection instructions.",
    noteEyebrow: "SORT WITH CARE",
    noteTitle: "Local rules come first.",
    noteBody: "BinWise shows India-wide sorting guidance. It does not identify your exact bin or pickup point. It cannot check hidden food or liquid. Follow your local authority’s instructions.",
    noteBodySample: "This is an example location with sample rules. Check the signs at your actual collection point before sorting.",
    footerNote: "Check local instructions before disposal.",
  },
  hi: {
    languageLabel: "भाषा",
    heroEyebrow: "छोटा कदम। बेहतर छँटाई।",
    heroLineOne: "कचरा सही जगह",
    heroLineTwo: "पर ",
    heroEm: "डालें।",
    heroBody: "फोटो लें या वस्तु चुनें। अपने क्षेत्र के निर्देशों के अनुसार कचरा अलग करने का तरीका देखें।",
    heroCta: "कचरा अलग करें",
    artItem: "प्लास्टिक बोतल",
    artAdvice: "स्थानीय नियम देखें",
    artCaption: "देखें → अलग करें → पूरा",
    scanEyebrow: "शुरू करें",
    scanTitle: "कचरा अलग करें",
    locationLabel: "निर्देश का क्षेत्र",
    locationHint: "स्थानीय संग्रह नियम अलग हो सकते हैं",
    itemLabel: "आपकी वस्तु",
    itemHint: "एक फोटो में एक वस्तु",
    uploadTitle: "फोटो लें या अपलोड करें",
    uploadSubtitle: "JPEG, PNG या WebP · अधिकतम 10 MB",
    unsupportedWarning:
      "बैटरी, दवाएँ, सैनिटरी कचरा और ई-कचरे के लिए विशेष व्यवस्था हो सकती है। स्थानीय निर्देश देखें।",
    textTitle: "कैमरा नहीं? वस्तु का नाम लिखें",
    textHint: "सुझावों में से वस्तु चुनें। कोई फोटो नहीं भेजा जाएगा।",
    textLabel: "वस्तु का नाम",
    textButton: "खोजें",
    quickTitle: "या सामान्य वस्तु चुनें",
    textPlaceholder: "जैसे प्लास्टिक बोतल या बचा हुआ खाना",
    textNoMatch: "स्पष्ट मिलान नहीं मिला। प्लास्टिक बोतल, गत्ते का डिब्बा, खाना या बैटरी लिखें।",
    textUnavailable: "इस स्थान के लिए नियम नहीं है। भारत वाला विकल्प चुनें या स्थानीय निर्देश देखें।",
    textReady: "वस्तु चुनी गई। यदि तैयारी के सवाल दिखें तो जवाब दें।",
    resultKicker: "कचरा अलग करने का तरीका",
    emptyTitle: "जवाब यहाँ दिखेगा",
    emptyHint: "वस्तु की फोटो लें या नाम लिखें।",
    takeTo: "इस श्रेणी में रखें",
    differentMaterial: "क्या वस्तु का प्रकार अलग है?",
    prepTitle: "पहले यह जाँचें",
    emptyQuestion: "क्या वस्तु खाली है?",
    cleanQuestion: "क्या इस पर खाना या तरल नहीं लगा है?",
    yes: "हाँ",
    noUnsure: "नहीं / पता नहीं",
    prepWait: "कचरा अलग करने से पहले इन सवालों का जवाब दें।",
    prepReady: "अब नीचे दिए गए निर्देश देखें।",
    prepFix: "यदि संभव हो तो इसे खाली और साफ करें। नहीं कर सकते तो स्थानीय नियम देखें।",
    prepPaper: "खाने से गंदे कागज़ या गत्ते के लिए स्थानीय नियम देखें।",
    prepCaveat: "BinWise छिपे हुए खाने या तरल की जाँच नहीं कर सकता। स्थानीय नियम मानें।",
    listen: "निर्देश सुनें",
    stop: "सुनना बंद करें",
    speechUnavailable: "इस ब्राउज़र में आवाज़ उपलब्ध नहीं है।",
    officialSource: "आधिकारिक नियम देखें",
    changePhoto: "फोटो बदलें",
    scanButton: "वस्तु जाँचें",
    scanning: "वस्तु देखी जा रही है",
    chooseItem: "शुरू करने के लिए वस्तु चुनें।",
    ready: "फोटो तैयार है।",
    analysing: "फोटो जाँची जा रही है…",
    scanComplete: "वस्तु पहचानी गई। रखने से पहले तैयारी जाँचें।",
    confirmMaterial: "कृपया वस्तु का प्रकार जाँचें।",
    unsupportedStatus: "अपने आप सलाह नहीं दी गई। वस्तु और स्थानीय नियम देखें।",
    locationChanged: "निर्देश का क्षेत्र बदला। वस्तु फिर चुनें।",
    invalidFile: "JPEG, PNG या WebP फोटो चुनें।",
    largeFile: "10 MB से छोटी फोटो चुनें।",
    noFile: "पहले फोटो चुनें।",
    scanFailed: "फोटो की जाँच नहीं हो सकी।",
    loadFailed: "निर्देश नहीं खुल सके। पेज फिर खोलें।",
    guidanceFailed: "निर्देश नहीं मिल सके।",
    qualityTitle: "फोटो दोबारा लें",
    too_small: "फोटो बहुत छोटी है। पास जाकर फिर लें।",
    too_dark: "फोटो बहुत अँधेरी है। रोशनी बढ़ाकर फिर लें।",
    too_blurry: "फोटो धुँधली है। स्थिर रहकर एक वस्तु साफ दिखाएँ।",
    photoSuggestion: "फोटो से सुझाव",
    needsCheck: "जाँच ज़रूरी",
    noAuto: "अपने आप सलाह नहीं",
    selectedByYou: "आपने चुना",
    confirmedByYou: "आपने पुष्टि की",
    noBin: "डिब्बे की सलाह नहीं",
    somethingElse: "कुछ और",
    outsideScope: "इस वस्तु के लिए विशेष व्यवस्था हो सकती है। नीचे प्रकार चुनें या स्थानीय निर्देश देखें।",
    tentative: "वस्तु स्पष्ट नहीं है। नीचे सही प्रकार चुनें।",
    recognised: "वस्तु जाँचें और नीचे दिए तैयारी के सवालों का जवाब दें।",
    textSelected: "आपने सूची से यह वस्तु चुनी है।",
    manualSelected: "आपने इस सामग्री की पुष्टि की है।",
    checkYourself: "कृपया वस्तु खुद जाँचें।",
    helpCheck: "इसे जाँचने में मदद करें।",
    unsupportedHelp: "नीचे सही प्रकार चुनें, या कुछ और चुनकर स्थानीय नियम देखें।",
    confirmHelp: "निर्देश देखने से पहले सही सामग्री चुनें।",
    otherIntro: "BinWise इस वस्तु की श्रेणी नहीं बता सकता। स्थानीय निर्देश देखें या कचरा संग्रह सेवा से पूछें।",
    otherDisclaimer: "बैटरी, ई-कचरा, सैनिटरी या अनजानी वस्तु केवल फोटो के अनुमान से सामान्य डिब्बे में न डालें।",
    noSuggestion: "इस वस्तु के लिए अपने आप डिब्बे की सलाह नहीं दी गई।",
    guidanceUpdated: "निर्देश बदल गए।",
    qrOpen: "इस गाइड का QR कोड देखें",
    qrTitle: "यह गाइड साझा करें",
    qrLinkLabel: "QR कोड में दिया गया लिंक",
    qrLocalWarning: "यह पूर्वावलोकन लिंक केवल इसी कंप्यूटर पर खुलेगा। QR कार्ड प्रिंट करने से पहले BinWise का साझा लिंक खोलें।",
    qrCopy: "लिंक कॉपी करें",
    qrDownload: "QR डाउनलोड करें",
    qrPrint: "कार्ड प्रिंट करें",
    qrCopied: "लिंक कॉपी हो गया।",
    qrCopyFailed: "ऊपर दिया लिंक चुनकर कॉपी करें।",
    qrFailed: "QR कोड नहीं बन सका।",
    feedbackTitle: "क्या यह सलाह सही थी?",
    feedbackPrivacy: "गलती बताने में मदद करें। प्रतिक्रिया के साथ फोटो या नाम नहीं रखा जाता।",
    feedbackCorrect: "हाँ, सही थी",
    feedbackMaterial: "वस्तु का प्रकार गलत",
    feedbackRule: "स्थानीय नियम अलग है",
    feedbackChoose: "सही प्रकार क्या है?",
    feedbackSend: "सुधार भेजें",
    feedbackSelect: "सुधार भेजने के लिए अलग प्रकार चुनें।",
    feedbackSaved: "धन्यवाद। आपकी प्रतिक्रिया सुरक्षित हो गई।",
    feedbackFailed: "प्रतिक्रिया सुरक्षित नहीं हो सकी। फिर प्रयास करें।",
    howEyebrow: "आसान तरीका",
    howTitle: "BinWise कैसे उपयोग करें",
    howOneTitle: "एक वस्तु चुनें",
    howOneBody: "साफ फोटो लें या सूची से सामान्य वस्तु चुनें।",
    howTwoTitle: "उसकी हालत जाँचें",
    howTwoBody: "बताएँ कि वस्तु खाली है और उस पर खाना या तरल नहीं लगा है।",
    howThreeTitle: "निर्देश मानें",
    howThreeBody: "कचरा अलग करने का तरीका देखें, फिर स्थानीय संग्रह नियम जाँचें।",
    noteEyebrow: "सावधानी से अलग करें",
    noteTitle: "स्थानीय नियम पहले देखें।",
    noteBody: "BinWise भारत-व्यापी कचरा अलग करने के निर्देश देता है। यह आपके खास डिब्बे या संग्रह स्थान को नहीं बताता। छिपे हुए खाने या तरल की जाँच नहीं कर सकता। स्थानीय निकाय के निर्देश मानें।",
    noteBodySample: "यह केवल उदाहरण का स्थान है। कचरा डालने से पहले अपने असली संग्रह स्थान के संकेत देखें।",
    footerNote: "कचरा डालने से पहले स्थानीय निर्देश देखें।",
  },
};

const materialLabels = {
  cardboard: { en: "Cardboard", hi: "गत्ता" },
  glass: { en: "Glass", hi: "काँच" },
  metal: { en: "Metal", hi: "धातु" },
  paper: { en: "Paper", hi: "कागज़" },
  plastic: { en: "Plastic", hi: "प्लास्टिक" },
  trash: { en: "Other waste", hi: "अन्य कचरा" },
};

const catalog = [
  { material: "cardboard", en: "cardboard box", hi: "गत्ते का डिब्बा", aliases: ["cardboard", "cardboard box", "carton box", "गत्ता", "गत्ते का डिब्बा"] },
  { material: "paper", en: "paper or newspaper", hi: "कागज़ या अख़बार", aliases: ["paper", "newspaper", "paper sheet", "paper or newspaper", "कागज़", "अख़बार", "कागज़ या अख़बार"] },
  { material: "plastic", en: "plastic bottle", hi: "प्लास्टिक बोतल", aliases: ["plastic", "plastic bottle", "plastic container", "plastic bottles", "प्लास्टिक", "प्लास्टिक बोतल"] },
  { material: "metal", en: "metal can", hi: "धातु का डिब्बा", aliases: ["metal", "metal can", "aluminium can", "tin can", "धातु", "धातु का डिब्बा"] },
  { material: "glass", en: "glass jar", hi: "काँच का जार", aliases: ["glass", "glass jar", "glass bottle", "काँच", "काँच का जार", "काँच की बोतल"] },
  { material: "food_organics", en: "food scraps", hi: "बचा हुआ खाना", aliases: ["food scraps", "food waste", "fruit peel", "vegetable scraps", "leftovers", "बचा हुआ खाना", "फल का छिलका", "खाना"] },
  { material: "sanitary", en: "used diaper", hi: "इस्तेमाल किया डायपर", aliases: ["used diaper", "sanitary pad", "sanitary waste", "इस्तेमाल किया डायपर", "सैनिटरी कचरा"] },
  { material: "special_care", en: "used battery", hi: "पुरानी बैटरी", aliases: ["battery", "used battery", "expired medicine", "पुरानी बैटरी", "बैटरी", "समाप्त दवा"] },
];

const state = {
  locations: [],
  language: localStorage.getItem("binwise-language") === "hi" ? "hi" : "en",
  view: { kind: "empty" },
  prep: { empty: null, clean: null },
  scanning: false,
  speaking: false,
  statusKey: "chooseItem",
  textStatusKey: null,
  qrData: null,
  qrObjectUrl: null,
  qrStatusKey: null,
  feedback: { submitted: false, pending: false, editing: false, statusKey: null },
};

function t(key) {
  return copy[state.language][key] || copy.en[key] || key;
}

function setStatus(key, error = false) {
  state.statusKey = copy.en[key] ? key : null;
  statusLine.textContent = state.statusKey ? t(key) : key;
  statusLine.classList.toggle("error", error);
}

function setTextStatus(key, error = false) {
  state.textStatusKey = copy.en[key] ? key : null;
  textStatus.textContent = key ? t(key) : "";
  textStatus.classList.toggle("error", error);
}

function currentLocation() {
  return state.locations.find((item) => item.id === locationSelect.value);
}

function labelFor(material) {
  if (materialLabels[material]) return materialLabels[material][state.language];
  const extra = currentLocation()?.manual_materials.find((item) => item.id === material);
  return state.language === "hi" && extra?.name_hi ? extra.name_hi : extra?.name || material;
}

function localized(guidance, englishKey, hindiKey) {
  return state.language === "hi" && guidance[hindiKey]
    ? guidance[hindiKey]
    : guidance[englishKey];
}

function displayLocation(selectedId = locationSelect.value) {
  locationSelect.replaceChildren(
    ...state.locations.map((location) => {
      const option = document.createElement("option");
      option.value = location.id;
      option.textContent = state.language === "hi" && location.name_hi ? location.name_hi : location.name;
      return option;
    }),
  );
  locationSelect.value = state.locations.some((item) => item.id === selectedId)
    ? selectedId
    : state.locations[0]?.id;
  const selected = currentLocation();
  locationSelect.hidden = state.locations.length <= 1;
  $("#location-static").hidden = state.locations.length !== 1;
  $("#location-static").textContent =
    state.language === "hi" && selected?.name_hi ? selected.name_hi : selected?.name || "";
  $("#note-body").textContent = t(selected?.sample ? "noteBodySample" : "noteBody");
  locationDescription.textContent =
    state.language === "hi" && selected?.description_hi
      ? selected.description_hi
      : selected?.description || "";
  locationSource.hidden = !selected?.source;
  qrOpen.hidden = !selected?.qr_shareable;
  if (selected?.source) {
    locationSource.href = selected.source.url;
    locationSource.textContent = `${t("officialSource")} ↗`;
    locationSource.title = selected.source.title;
  } else {
    locationSource.removeAttribute("href");
    locationSource.removeAttribute("title");
    locationSource.textContent = "";
  }
}

function setQrStatus(key, error = false) {
  state.qrStatusKey = key;
  $("#qr-status").textContent = key ? t(key) : "";
  $("#qr-status").classList.toggle("error", error);
}

function closeQr() {
  qrPanel.hidden = true;
  state.qrData = null;
  if (state.qrObjectUrl) URL.revokeObjectURL(state.qrObjectUrl);
  state.qrObjectUrl = null;
  qrImage.removeAttribute("src");
  qrUrl.value = "";
  setQrStatus("");
}

function renderQr() {
  const data = state.qrData;
  if (!data) return;
  $("#qr-profile").textContent =
    state.language === "hi" && data.location_hi ? data.location_hi : data.location;
  $("#qr-note").textContent =
    state.language === "hi" && data.note_hi ? data.note_hi : data.note;
  if (state.qrStatusKey) $("#qr-status").textContent = t(state.qrStatusKey);
}

async function openQr() {
  if (!qrPanel.hidden) {
    closeQr();
    return;
  }
  const selectedId = locationSelect.value;
  qrOpen.disabled = true;
  try {
    const response = await fetch(`/api/qr/${encodeURIComponent(selectedId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || t("qrFailed"));
    if (selectedId !== locationSelect.value) return;
    closeQr();
    state.qrData = data;
    state.qrObjectUrl = URL.createObjectURL(
      new Blob([data.svg], { type: "image/svg+xml" }),
    );
    qrImage.src = state.qrObjectUrl;
    qrImage.alt = `${t("qrTitle")}: ${data.location}`;
    qrUrl.value = data.share_url;
    $("#qr-print-url").textContent = data.share_url;
    $("#qr-download").href = state.qrObjectUrl;
    const isLocal = ["localhost", "127.0.0.1", "::1", "[::1]"].includes(
      new URL(data.share_url).hostname,
    );
    $("#qr-local-warning").hidden = !isLocal;
    $("#qr-download").hidden = isLocal;
    $("#qr-print").disabled = isLocal;
    renderQr();
    qrPanel.hidden = false;
  } catch (error) {
    closeQr();
    setStatus("qrFailed", true);
  } finally {
    qrOpen.disabled = false;
  }
}

function updateCatalogSuggestions() {
  const allowed = new Set([
    ...Object.keys(materialLabels),
    ...(currentLocation()?.manual_materials || []).map((item) => item.id),
  ]);
  $("#item-suggestions").replaceChildren(
    ...catalog
      .filter((item) => allowed.has(item.material))
      .map((item) => {
        const option = document.createElement("option");
        option.value = item[state.language];
        return option;
      }),
  );
  quickItems.replaceChildren(
    ...["plastic", "cardboard", "food_organics", "special_care"]
      .map((material) => catalog.find((item) => item.material === material))
      .filter((item) => item && allowed.has(item.material))
      .map((item) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = item[state.language];
        button.addEventListener("click", () => lookupCatalogItem(item));
        return button;
      }),
  );
}

function updateStaticText() {
  document.documentElement.lang = state.language === "hi" ? "hi" : "en";
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  textInput.placeholder = t("textPlaceholder");
  uploadZone.dataset.changeLabel = t("changePhoto");
  scanButton.innerHTML = state.scanning
    ? `${t("scanning")} <span aria-hidden="true">…</span>`
    : `${t("scanButton")} <span aria-hidden="true">↗</span>`;
  languageSelect.value = state.language;
  languageSelect.setAttribute("aria-label", t("languageLabel"));
  locationSelect.setAttribute("aria-label", t("locationLabel"));
  if (state.statusKey) statusLine.textContent = t(state.statusKey);
  if (state.textStatusKey) textStatus.textContent = t(state.textStatusKey);
  if (state.qrStatusKey) $("#qr-status").textContent = t(state.qrStatusKey);
  listenButton.querySelector("[data-i18n]").textContent = t(
    state.speaking ? "stop" : "listen",
  );
}

function resetPrep() {
  state.prep = { empty: null, clean: null };
  state.feedback = { submitted: false, pending: false, editing: false, statusKey: null };
  $("#feedback-status").textContent = "";
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  state.speaking = false;
}

function clearResult() {
  state.view = { kind: "empty" };
  resetPrep();
  renderView();
}

function selectFile(file) {
  if (!file) return;
  if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
    setStatus("invalidFile", true);
    return;
  }
  if (file.size > 10 * 1024 * 1024) {
    setStatus("largeFile", true);
    return;
  }
  const imageURL = URL.createObjectURL(file);
  preview.onload = () => URL.revokeObjectURL(imageURL);
  preview.src = imageURL;
  preview.hidden = false;
  uploadZone.classList.add("has-image");
  scanButton.disabled = false;
  clearResult();
  setTextStatus("");
  setStatus("ready");
}

function cleanImageSelection() {
  fileInput.value = "";
  preview.removeAttribute("src");
  preview.hidden = true;
  uploadZone.classList.remove("has-image");
  scanButton.disabled = true;
}

async function scan() {
  const file = fileInput.files?.[0];
  if (!file) {
    setStatus("noFile", true);
    return;
  }
  const form = new FormData();
  form.append("file", file);
  form.append("location_id", locationSelect.value);
  state.scanning = true;
  scanButton.disabled = true;
  updateStaticText();
  setStatus("analysing");
  try {
    const response = await fetch("/api/predict", { method: "POST", body: form });
    const result = await response.json();
    if (!response.ok) {
      if (response.status === 422 && result.detail?.code) {
        state.view = { kind: "quality", code: result.detail.code };
        renderView();
        setStatus(result.detail.code, true);
        return;
      }
      throw new Error(t("scanFailed"));
    }
    state.view = { kind: "model", result };
    resetPrep();
    renderView();
    setStatus(
      result.unsupported_item
        ? "unsupportedStatus"
        : result.needs_confirmation
          ? "confirmMaterial"
          : "scanComplete",
    );
  } catch {
    setStatus("scanFailed", true);
  } finally {
    state.scanning = false;
    scanButton.disabled = false;
    updateStaticText();
    renderView();
  }
}

function populateChoices(selected) {
  const choices = [
    ...Object.keys(materialLabels),
    ...(currentLocation()?.manual_materials || []).map((item) => item.id),
    "unsupported",
  ];
  $("#material-options").replaceChildren(
    ...choices.map((material) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = material === "unsupported" ? t("somethingElse") : labelFor(material);
      button.classList.toggle("selected", material === selected);
      button.addEventListener("click", () => chooseMaterial(material));
      return button;
    }),
  );
}

function viewGuidance() {
  const view = state.view;
  if (view.kind === "model" && !view.result.needs_confirmation)
    return view.result.guidance;
  if (view.kind === "manual" || view.kind === "text") return view.guidance;
  return null;
}

function viewMaterial() {
  const view = state.view;
  return view.kind === "model" ? view.result.material : view.material;
}

function needsPrep(guidance, material) {
  return (
    ["cardboard", "paper", "plastic", "metal", "glass"].includes(material) &&
    ["dry", "recycling", "glass"].includes(guidance.bin)
  );
}

function populateCorrectionOptions() {
  const selected = $("#feedback-material").value;
  const choices = [
    ...Object.keys(materialLabels),
    ...(currentLocation()?.manual_materials || []).map((item) => item.id),
    "unsupported",
  ].filter((material) => material !== viewMaterial());
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = t("feedbackChoose");
  $("#feedback-material").replaceChildren(
    placeholder,
    ...choices.map((material) => {
      const option = document.createElement("option");
      option.value = material;
      option.textContent = material === "unsupported" ? t("somethingElse") : labelFor(material);
      return option;
    }),
  );
  if (choices.includes(selected)) $("#feedback-material").value = selected;
}

function renderFeedback() {
  feedbackBox.hidden = !viewGuidance() || $("#bin-box").hidden;
  if (feedbackBox.hidden) return;
  const feedback = state.feedback;
  $("#feedback-actions").hidden = feedback.submitted;
  $("#feedback-correction").hidden = !feedback.editing || feedback.submitted;
  if (feedback.editing && !feedback.submitted) populateCorrectionOptions();
  feedbackBox.querySelectorAll("button").forEach((button) => {
    button.disabled = feedback.pending;
  });
  $("#feedback-status").textContent = feedback.statusKey ? t(feedback.statusKey) : "";
  $("#feedback-status").classList.toggle("error", feedback.statusKey === "feedbackFailed");
}

async function submitFeedback(rating) {
  const feedback = state.feedback;
  if (feedback.pending || feedback.submitted || $("#bin-box").hidden) return;
  if (rating === "wrong_material" && !$("#feedback-material").value) {
    feedback.statusKey = "feedbackSelect";
    renderFeedback();
    return;
  }
  const payload = {
    location_id: locationSelect.value,
    shown_material: viewMaterial(),
    channel: state.view.kind === "model" ? "model" : state.view.kind === "text" ? "text" : "manual",
    rating,
    corrected_material:
      rating === "wrong_material" ? $("#feedback-material").value : null,
  };
  feedback.pending = true;
  renderFeedback();
  try {
    const response = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) throw new Error("feedbackFailed");
    if (state.feedback === feedback) {
      feedback.submitted = true;
      feedback.statusKey = "feedbackSaved";
    }
  } catch {
    if (state.feedback === feedback) feedback.statusKey = "feedbackFailed";
  } finally {
    feedback.pending = false;
    if (state.feedback === feedback) renderFeedback();
  }
}

function hideGuidance() {
  $("#bin-box").hidden = true;
  $("#instruction").textContent = "";
  $("#result-disclaimer").textContent = "";
  listenButton.hidden = true;
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  state.speaking = false;
  feedbackBox.hidden = true;
}

function renderGuidance(guidance) {
  const box = $("#bin-box");
  box.hidden = false;
  box.style.borderLeftColor = guidance.bin_color;
  $("#bin-icon").textContent = guidance.bin_icon;
  $("#bin-icon").style.color = guidance.bin_color;
  $("#bin-name").textContent = localized(guidance, "bin_name", "bin_name_hi");
  $("#instruction").textContent = localized(guidance, "instruction", "instruction_hi");
  $("#result-disclaimer").textContent = localized(guidance, "disclaimer", "disclaimer_hi");
  listenButton.hidden = !("speechSynthesis" in window && "SpeechSynthesisUtterance" in window);
  renderFeedback();
}

function updatePrepGate() {
  const guidance = viewGuidance();
  const material = viewMaterial();
  if (!guidance) {
    prepBox.hidden = true;
    hideGuidance();
    return;
  }
  if (!needsPrep(guidance, material)) {
    prepBox.hidden = true;
    renderGuidance(guidance);
    return;
  }
  prepBox.hidden = false;
  const needsEmpty = ["plastic", "metal", "glass"].includes(material);
  $("#prep-empty-row").hidden = !needsEmpty;
  document.querySelectorAll("[data-prep]").forEach((button) => {
    button.setAttribute(
      "aria-pressed",
      String(state.prep[button.dataset.prep] === button.dataset.answer),
    );
  });
  const ready = state.prep.clean === "yes" && (!needsEmpty || state.prep.empty === "yes");
  if (ready) {
    $("#prep-note").textContent = t("prepReady");
    renderGuidance(guidance);
  } else {
    hideGuidance();
    const negative = state.prep.clean === "no" || (needsEmpty && state.prep.empty === "no");
    $("#prep-note").textContent = negative
      ? ["paper", "cardboard"].includes(material) && state.prep.clean === "no"
        ? t("prepPaper")
        : t("prepFix")
      : t("prepWait");
    $("#result-disclaimer").textContent = t("prepCaveat");
  }
}

function renderView() {
  const view = state.view;
  if (view.kind === "empty" || view.kind === "quality") {
    resultEmpty.hidden = false;
    resultContent.hidden = true;
    $("#result-empty h3").textContent =
      view.kind === "quality" ? t("qualityTitle") : t("emptyTitle");
    $("#result-empty p").textContent =
      view.kind === "quality" ? t(view.code) : t("emptyHint");
    return;
  }
  resultEmpty.hidden = true;
  resultContent.hidden = false;
  const isModel = view.kind === "model";
  const unsupported = isModel && view.result.unsupported_item;
  const tentative = isModel && view.result.needs_confirmation;
  $("#material-name").textContent =
    unsupported || view.kind === "other" ? t("somethingElse") : labelFor(viewMaterial());
  $("#confidence-label").textContent =
    view.kind === "other"
      ? t("noBin")
      : view.kind === "text"
        ? t("selectedByYou")
        : view.kind === "manual"
          ? t("confirmedByYou")
          : unsupported
            ? t("noAuto")
            : tentative
              ? t("needsCheck")
              : t("photoSuggestion");
  $("#result-intro").textContent =
    view.kind === "other"
      ? t("otherIntro")
      : view.kind === "text"
        ? t("textSelected")
        : view.kind === "manual"
          ? t("manualSelected")
          : unsupported
            ? t("outsideScope")
            : tentative
              ? t("tentative")
              : t("recognised");
  $("#uncertain-box").hidden = !tentative;
  $("#uncertain-title").textContent = unsupported ? t("checkYourself") : t("helpCheck");
  $("#uncertain-description").textContent = unsupported ? t("unsupportedHelp") : t("confirmHelp");
  populateChoices(view.kind === "manual" || view.kind === "other" ? view.material : null);
  if (view.kind === "other") {
    prepBox.hidden = true;
    hideGuidance();
    $("#result-disclaimer").textContent = t("otherDisclaimer");
  } else {
    updatePrepGate();
  }
}

async function chooseMaterial(material) {
  if (material === "unsupported") {
    state.view = { kind: "other", material };
    resetPrep();
    renderView();
    setStatus("noSuggestion");
    return;
  }
  try {
    const response = await fetch(
      `/api/guidance/${encodeURIComponent(locationSelect.value)}/${encodeURIComponent(material)}`,
    );
    const guidance = await response.json();
    if (!response.ok) throw new Error(t("guidanceFailed"));
    state.view = { kind: "manual", material, guidance };
    resetPrep();
    renderView();
    setStatus("guidanceUpdated");
  } catch {
    setStatus("guidanceFailed", true);
  }
}

function normalize(value) {
  return value.toLocaleLowerCase().trim().replace(/[\s\-_/]+/g, " ");
}

async function lookupText(event) {
  event.preventDefault();
  const query = normalize(textInput.value);
  const matches = catalog.filter((item) =>
    item.aliases.some((alias) => normalize(alias) === query),
  );
  if (matches.length !== 1) {
    setTextStatus("textNoMatch", true);
    return;
  }
  await lookupCatalogItem(matches[0]);
}

async function lookupCatalogItem(item) {
  const material = item.material;
  const allowed = new Set([
    ...Object.keys(materialLabels),
    ...(currentLocation()?.manual_materials || []).map((item) => item.id),
  ]);
  if (!allowed.has(material)) {
    setTextStatus("textUnavailable", true);
    return;
  }
  textInput.value = item[state.language];
  setTextStatus("");
  try {
    const response = await fetch(
      `/api/guidance/${encodeURIComponent(locationSelect.value)}/${encodeURIComponent(material)}`,
    );
    const guidance = await response.json();
    if (!response.ok) throw new Error(t("guidanceFailed"));
    cleanImageSelection();
    state.view = { kind: "text", material, guidance };
    resetPrep();
    renderView();
    setTextStatus("textReady");
    setStatus("");
    $("#result-card").scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch {
    setTextStatus("guidanceFailed", true);
  }
}

function readAloud() {
  if (!("speechSynthesis" in window && "SpeechSynthesisUtterance" in window)) {
    setStatus("speechUnavailable", true);
    return;
  }
  if (state.speaking) {
    window.speechSynthesis.cancel();
    state.speaking = false;
    updateStaticText();
    return;
  }
  const guidance = viewGuidance();
  if (!guidance || $("#bin-box").hidden) return;
  const hasHindi = state.language === "hi" && Boolean(guidance.instruction_hi);
  const text = [
    localized(guidance, "bin_name", "bin_name_hi"),
    localized(guidance, "instruction", "instruction_hi"),
    localized(guidance, "disclaimer", "disclaimer_hi"),
  ].join(". ");
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = hasHindi ? "hi-IN" : "en-IN";
  utterance.rate = 0.92;
  const voice = window.speechSynthesis
    .getVoices()
    .find((item) => item.lang.toLowerCase().startsWith(hasHindi ? "hi" : "en"));
  if (voice) utterance.voice = voice;
  utterance.onend = () => {
    state.speaking = false;
    updateStaticText();
  };
  utterance.onerror = (event) => {
    state.speaking = false;
    updateStaticText();
    if (!["canceled", "interrupted"].includes(event.error))
      setStatus("speechUnavailable", true);
  };
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
  state.speaking = true;
  updateStaticText();
}

async function init() {
  updateStaticText();
  try {
    const response = await fetch("/api/locations");
    if (!response.ok) throw new Error(t("loadFailed"));
    const availableLocations = await response.json();
    state.locations = availableLocations.filter((site) => demoMode || !site.sample);
    const requested = new URLSearchParams(location.search).get("site");
    const first = state.locations[0]?.id;
    displayLocation(
      state.locations.some((item) => item.id === requested) ? requested : first,
    );
    updateCatalogSuggestions();
    renderView();
  } catch {
    setStatus("loadFailed", true);
  }
}

locationSelect.addEventListener("change", () => {
  const selected = locationSelect.value;
  closeQr();
  displayLocation(selected);
  updateCatalogSuggestions();
  clearResult();
  setTextStatus("");
  setStatus("locationChanged");
});
languageSelect.addEventListener("change", () => {
  const selected = locationSelect.value;
  state.language = languageSelect.value;
  localStorage.setItem("binwise-language", state.language);
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
  state.speaking = false;
  updateStaticText();
  displayLocation(selected);
  renderQr();
  updateCatalogSuggestions();
  renderView();
});
qrOpen.addEventListener("click", openQr);
$("#qr-copy").addEventListener("click", async () => {
  if (!state.qrData) return;
  try {
    await navigator.clipboard.writeText(state.qrData.share_url);
    setQrStatus("qrCopied");
  } catch {
    qrUrl.select();
    setQrStatus("qrCopyFailed", true);
  }
});
$("#qr-print").addEventListener("click", () => {
  if (state.qrData && !$("#qr-print").disabled) window.print();
});
document.querySelectorAll("[data-feedback]").forEach((button) => {
  button.addEventListener("click", () => {
    const rating = button.dataset.feedback;
    if (rating === "wrong_material") {
      state.feedback.editing = true;
      state.feedback.statusKey = "feedbackSelect";
      renderFeedback();
    } else {
      submitFeedback(rating);
    }
  });
});
$("#feedback-send").addEventListener("click", () => submitFeedback("wrong_material"));
fileInput.addEventListener("change", () => selectFile(fileInput.files?.[0]));
scanButton.addEventListener("click", scan);
textForm.addEventListener("submit", lookupText);
listenButton.addEventListener("click", readAloud);
document.querySelectorAll("[data-prep]").forEach((button) => {
  button.addEventListener("click", () => {
    state.prep[button.dataset.prep] = button.dataset.answer;
    updatePrepGate();
  });
});
uploadZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  uploadZone.classList.add("dragover");
});
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("dragover"));
uploadZone.addEventListener("drop", (event) => {
  event.preventDefault();
  uploadZone.classList.remove("dragover");
  const file = event.dataTransfer.files?.[0];
  if (!file) return;
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  selectFile(file);
});
init();
