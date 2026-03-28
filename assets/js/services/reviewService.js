import { api } from '../api.js';
export const reviewService = { list: () => api.list('reviews') };
