const statuses = ['active', 'paused', 'draft'];
export const products = Array.from({ length: 18 }).map((_, i) => ({
  id: 1000 + i,
  sku: `SKU-${1000 + i}`,
  name: `Produto ${i + 1}`,
  status: statuses[i % 3],
  condition: i % 2 ? 'new' : 'used',
  freeShipping: i % 3 === 0,
  logistics: i % 2 ? 'fulfillment' : 'cross-docking',
  price: +(29.9 + i * 3.17).toFixed(2),
  stock: 10 + i,
  category: i % 2 ? 'Eletrônicos' : 'Casa',
  permalink: `https://loja.local/produto-${i + 1}`,
  tags: ['destaque', i % 2 ? 'premium' : 'base'],
  description: `Descrição rica do Produto ${i + 1}.`,
}));

export const kits = [
  { id: 1, name: 'Kit Starter', items: [products[0], products[1]] },
  { id: 2, name: 'Kit Casa', items: [products[2], products[3], products[4]] },
];

export const reviews = Array.from({ length: 15 }).map((_, i) => ({
  id: i + 1,
  productId: products[i % products.length].id,
  rating: (i % 5) + 1,
  date: `2026-03-${String((i % 28) + 1).padStart(2, '0')}`,
  comment: `Comentário ${i + 1} sobre o produto.`,
}));

export const sales = Array.from({ length: 12 }).map((_, i) => ({
  id: `PED-${3000 + i}`,
  buyer: `Comprador ${i + 1}`,
  date: `2026-03-${String((i % 25) + 1).padStart(2, '0')}`,
  paymentStatus: i % 3 ? 'approved' : 'pending',
  status: i % 2 ? 'sent' : 'processing',
  total: +(120 + i * 18.5).toFixed(2),
  items: [products[i % products.length], products[(i + 1) % products.length]],
}));

export const shippingQuotes = products.slice(0, 10).map((p, i) => ({
  productId: p.id,
  cep: '01310-100',
  method: i % 2 ? 'PAC' : 'SEDEX',
  logistics: p.logistics,
  cost: +(18 + i * 1.7).toFixed(2),
  days: 2 + (i % 6),
}));

export const syncLogs = [];
