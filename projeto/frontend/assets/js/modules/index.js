import { dashboardModule } from './dashboard.js';
import { descriptionsModule } from './descriptions.js';
import { kitsModule } from './kits.js';
import { productsModule } from './products.js';
import { reviewsModule } from './reviews.js';
import { salesModule } from './sales.js';
import { settingsModule } from './settings.js';
import { shippingModule } from './shipping.js';
import { syncModule } from './sync.js';

export const modules = {
  dashboard: dashboardModule,
  products: productsModule,
  descriptions: descriptionsModule,
  kits: kitsModule,
  reviews: reviewsModule,
  sales: salesModule,
  shipping: shippingModule,
  sync: syncModule,
  settings: settingsModule,
};
