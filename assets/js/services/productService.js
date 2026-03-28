import { api } from '../api.js';
export const productService = {
  list: () => api.list('products'),
  update: (id, patch) => api.update('products', id, patch),
  remove: (id) => api.remove('products', id),
};
