import * as mock from './data/mockData.js';

const db = structuredClone(mock);

const delay = (ms = 120) => new Promise((res) => setTimeout(res, ms));

export const api = {
  async list(resource) { await delay(); return structuredClone(db[resource]); },
  async update(resource, id, patch) {
    await delay();
    const arr = db[resource];
    const idx = arr.findIndex((x) => String(x.id) === String(id));
    if (idx >= 0) arr[idx] = { ...arr[idx], ...patch };
    return structuredClone(arr[idx]);
  },
  async create(resource, payload) {
    await delay();
    db[resource].push(payload);
    return structuredClone(payload);
  },
  async remove(resource, id) {
    await delay();
    db[resource] = db[resource].filter((x) => String(x.id) !== String(id));
    return true;
  },
};
