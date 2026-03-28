import { api } from '../api.js';
export const shippingService = { list: () => api.list('shippingQuotes') };
