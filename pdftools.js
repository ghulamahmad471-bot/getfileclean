/* Shared helpers for the GetFileClean PDF tools. Everything runs in the browser; files are never uploaded. */
(function(){
'use strict';
const T = window.GFC = {};

function loadScript(src){
  return new Promise((res, rej) => {
    const s = document.createElement('script'); s.src = src;
    s.onload = res; s.onerror = () => { s.remove(); rej(new Error('Could not load ' + src)); };
    document.head.append(s);
  });
}

let pdfLibP = null, pdfJsP = null;
T.pdfLib = () => {
  if (globalThis.PDFLib) return Promise.resolve(globalThis.PDFLib);
  return pdfLibP ||= loadScript('pdf-lib.min.js').then(() => globalThis.PDFLib)
    .catch(e => { pdfLibP = null; throw new Error('Could not load the PDF tool. Check your connection and reload.'); });
};
T.pdfJs = () => {
  if (globalThis.pdfjsLib) return Promise.resolve(globalThis.pdfjsLib);
  return pdfJsP ||= loadScript('pdf.min.js').then(() => {
    const j = globalThis.pdfjsLib;
    j.GlobalWorkerOptions.workerSrc = 'pdf.worker.min.js';
    return j;
  }).catch(e => { pdfJsP = null; throw new Error('Could not load the PDF viewer. Check your connection and reload.'); });
};

/* Open a PDF for viewing. isEvalSupported:false blocks font-script execution (security hardening). */
T.openView = async (bytes) => {
  const j = await T.pdfJs();
  return j.getDocument({ data: bytes.slice(0), isEvalSupported: false, disableFontFace: false }).promise;
};

/* Open a PDF for editing with pdf-lib, with a friendly error for encrypted files. */
T.openEdit = async (bytes) => {
  const { PDFDocument } = await T.pdfLib();
  try { return await PDFDocument.load(bytes, { updateMetadata: false }); }
  catch (e) {
    if (/encrypt/i.test(e.message)) throw new Error('This PDF is password-protected. Remove the password first, then try again.');
    throw new Error('This file could not be read as a PDF.');
  }
};

/* Render one page into a canvas. */
T.renderPage = async (pdf, num, { width = 160, rotation, canvas } = {}) => {
  const page = await pdf.getPage(num);
  const rot = rotation ?? page.rotate;
  const v1 = page.getViewport({ scale: 1, rotation: rot });
  const scale = width / v1.width;
  const vp = page.getViewport({ scale, rotation: rot });
  const c = canvas || document.createElement('canvas');
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  c.width = Math.ceil(vp.width * dpr); c.height = Math.ceil(vp.height * dpr);
  const ctx = c.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, vp.width, vp.height);
  await page.render({ canvasContext: ctx, viewport: vp }).promise;
  return { canvas: c, page, viewport: vp, v1 };
};

/* Remove document-level metadata (author, title, producer, XMP) from a pdf-lib document. */
T.stripMeta = (doc) => {
  const { PDFName, PDFRef } = globalThis.PDFLib;
  const ctx = doc.context, info = ctx.trailerInfo.Info;
  if (info) { if (info instanceof PDFRef) ctx.delete(info); ctx.trailerInfo.Info = undefined; }
  const cat = doc.catalog, md = cat.get(PDFName.of('Metadata'));
  if (md) { if (md instanceof PDFRef) ctx.delete(md); cat.delete(PDFName.of('Metadata')); }
  cat.delete(PDFName.of('PieceInfo'));
};

T.save = async (doc, { clean = true } = {}) => {
  if (clean) T.stripMeta(doc);
  return doc.save({ updateFieldAppearances: false });
};

T.download = (bytes, name) => {
  const blob = bytes instanceof Blob ? bytes : new Blob([bytes], { type: 'application/pdf' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = name;
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 30000);
};

T.baseName = (n) => (n || 'document').replace(/\.[^.]+$/, '').replace(/[^\w\- ]+/g, '').trim().slice(0, 60) || 'document';
T.size = (b) => b < 1024 ? b + ' B' : b < 1048576 ? (b / 1024).toFixed(0) + ' KB' : (b / 1048576).toFixed(1) + ' MB';
T.readBytes = (f) => f.arrayBuffer().then(b => new Uint8Array(b));
T.isPdf = (f) => /\.pdf$/i.test(f.name) || f.type === 'application/pdf';

let toastT;
T.toast = (msg, ms = 3800) => {
  let t = document.querySelector('.toast');
  if (!t) { t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); document.body.append(t); }
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), ms);
};
T.busy = (msg) => {
  let b = document.querySelector('.busy');
  if (msg === false) { b && b.remove(); return; }
  if (!b) { b = document.createElement('div'); b.className = 'busy'; b.innerHTML = '<span></span>'; document.body.append(b); }
  b.firstChild.textContent = msg;
};

/* Wire a drop zone: element with an <input type=file> inside. */
T.dropZone = (el, onFiles) => {
  const inp = el.querySelector('input[type=file]');
  inp.addEventListener('change', () => { if (inp.files.length) onFiles([...inp.files]); inp.value = ''; });
  ['dragenter', 'dragover'].forEach(ev => el.addEventListener(ev, e => { e.preventDefault(); el.classList.add('on'); }));
  ['dragleave', 'drop'].forEach(ev => el.addEventListener(ev, e => { e.preventDefault(); el.classList.remove('on'); }));
  el.addEventListener('drop', e => { const f = [...(e.dataTransfer?.files || [])]; if (f.length) onFiles(f); });
};
})();
