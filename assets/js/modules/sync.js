import { runSync } from '../services/syncService.js';
import { state } from '../state.js';

export async function renderSync(container) {
  container.innerHTML = `<div class="stack"><h2>Sincronização</h2><div class="card"><p id="sync-step">Pronto para iniciar.</p><div class="progress"><span id="sync-progress" style="width:0%"></span></div><br><button id="sync-btn" class="btn primary">Executar atualização</button></div></div>`;
  container.querySelector('#sync-btn').onclick = async () => {
    state.sync.running = true;
    await runSync(({ step, progress }) => {
      state.sync.step = step;
      state.sync.progress = progress;
      container.querySelector('#sync-step').textContent = `${step} (${progress}%)`;
      container.querySelector('#sync-progress').style.width = `${progress}%`;
    });
    state.sync.running = false;
  };
}
