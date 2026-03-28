import { api } from '../api.js';
export const kitService = {
  list: () => api.list('kits'),
  create: (payload) => api.create('kits', payload),
  update: (id, patch) => api.update('kits', id, patch),
  remove: (id) => api.remove('kits', id),
};
