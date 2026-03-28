import { state, setTheme } from '../state.js';
import { settingsService } from '../services/settingsService.js';
import { toast } from '../components/toast.js';

export function renderSettings(container) {
  container.innerHTML = `
    <div class="stack">
      <h2>Configurações</h2>
      <div class="card stack">
        <div class="form-group"><label>Tema</label><select id="pref-theme"><option value="dark">Escuro</option><option value="light">Claro</option></select></div>
        <div class="form-group"><label>Idioma</label><select id="pref-lang"><option value="pt-BR">Português (Brasil)</option><option value="en-US">English</option></select></div>
        <div class="form-group"><label>Integração futura (SQLite/API)</label><input id="pref-endpoint" class="input" placeholder="http://localhost:8000"/></div>
        <button id="save-pref" class="btn primary">Salvar preferências</button>
      </div>
    </div>`;
  container.querySelector('#pref-theme').value = state.theme;
  container.querySelector('#pref-lang').value = state.preferences.language;
  container.querySelector('#save-pref').onclick = () => {
    const theme = container.querySelector('#pref-theme').value;
    const language = container.querySelector('#pref-lang').value;
    const endpoint = container.querySelector('#pref-endpoint').value;
    setTheme(theme);
    settingsService.save({ language, endpoint });
    toast('Configurações salvas');
  };
}
