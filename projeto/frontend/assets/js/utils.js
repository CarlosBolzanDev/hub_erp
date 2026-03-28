export const el = (html) => {
  const t = document.createElement('template');
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
};

export const pretty = (v) => (v === null || v === undefined ? '-' : String(v));
