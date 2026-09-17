// Remplaces les deux lignes du haut de ton app.js par :
const isLocalFrontend = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const API_BASE = isLocalFrontend ? 'http://localhost:5102' : 'http://exp.s3.fsbm.ma:5102';
const CATALOG_URL = '/catalog/Books.csv';
const state = { books: [], loaded: false };

const elements = {
  form: document.querySelector('#prediction-form'),
  userId: document.querySelector('#user-id'),
  search: document.querySelector('#book-search'),
  select: document.querySelector('#book-select'),
  catalogStatus: document.querySelector('#catalog-status'),
  error: document.querySelector('#form-error'),
  result: document.querySelector('#result'),
  sections: document.querySelectorAll('.page-section'),
  navLinks: document.querySelectorAll('[data-route]')
};

function parseCsvLine(line) {
  const values = [];
  let value = '';
  let quoted = false;
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (character === '"') {
      if (quoted && line[index + 1] === '"') { value += '"'; index += 1; }
      else { quoted = !quoted; }
    } else if (character === ';' && !quoted) { values.push(value); value = ''; }
    else { value += character; }
  }
  values.push(value);
  return values;
}

function parseCatalog(csv) {
  return csv.split(/\r?\n/).slice(1).map(parseCsvLine)
    .filter((columns) => columns[0] && columns[1])
    .map(([isbn, title, author]) => ({ isbn: isbn.trim(), title: title.trim(), author: (author || '').trim() }));
}

function renderBooks(query = '') {
  const normalizedQuery = query.trim().toLowerCase();
  const matches = state.books.filter((book) => `${book.title} ${book.author} ${book.isbn}`.toLowerCase().includes(normalizedQuery)).slice(0, 100);
  elements.select.innerHTML = matches.length
    ? matches.map((book) => `<option value="${escapeHtml(book.isbn)}">${escapeHtml(book.title)} — ${escapeHtml(book.author || 'Auteur inconnu')} · ${escapeHtml(book.isbn)}</option>`).join('')
    : '<option value="">Aucun livre trouvé</option>';
  elements.catalogStatus.textContent = normalizedQuery ? `${matches.length} résultat(s) affiché(s)` : `${state.books.length.toLocaleString('fr-FR')} livres disponibles`;
}

function escapeHtml(value) {
  return value.replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
}

async function loadCatalog() {
  try {
    const response = await fetch(CATALOG_URL);
    if (!response.ok) throw new Error('Catalogue indisponible');
    state.books = parseCatalog(await response.text());
    state.loaded = true;
    renderBooks();
  } catch (error) {
    elements.select.innerHTML = '<option value="">Catalogue indisponible</option>';
    elements.catalogStatus.textContent = 'Le catalogue n’a pas pu être chargé. Saisissez un ISBN ci-dessous via la recherche.';
    showError('Impossible de charger le catalogue des livres.');
  }
}

function showError(message) { elements.error.textContent = message; elements.error.classList.remove('hidden'); }
function clearMessages() { elements.error.classList.add('hidden'); elements.result.classList.add('hidden'); }

async function predict(event) {
  event.preventDefault();
  clearMessages();
  const userId = Number(elements.userId.value);
  const isbn = elements.select.value;
  if (!Number.isInteger(userId) || userId < 1) return showError('Veuillez saisir un identifiant lecteur valide.');
  if (!isbn) return showError('Veuillez choisir un livre dans le catalogue.');

  const submitButton = elements.form.querySelector('[type="submit"]');
  submitButton.disabled = true;
  submitButton.innerHTML = 'Calcul en cours...';
  try {
    const response = await fetch(`${API_BASE}/predict`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_id: userId, isbn }) });
    const contentType = response.headers.get('content-type') || '';
    const payload = contentType.includes('application/json') ? await response.json() : null;
    if (!response.ok) throw new Error(payload?.detail || `Le service de prédiction a répondu avec le statut ${response.status}.`);
    if (!payload) throw new Error('Le service de prédiction n’a pas renvoyé une réponse JSON.');
    elements.result.innerHTML = `<div class="result-label">Note prédite pour ${escapeHtml(payload.isbn)}</div><div class="result-rating">${Number(payload.predicted_rating).toFixed(1)} <span class="text-base text-ink/60">/ 10</span></div>`;
    elements.result.classList.remove('hidden');
  } catch (error) { showError(error.message); }
  finally { submitButton.disabled = false; submitButton.innerHTML = 'Calculer la note <span aria-hidden="true">→</span>'; }
}

function route() {
  const routeName = window.location.hash === '#predict' ? 'predict' : 'home';
  elements.sections.forEach((section) => section.classList.toggle('hidden', section.id !== routeName));
  elements.navLinks.forEach((link) => link.classList.toggle('is-active', link.dataset.route === routeName));
  if (routeName === 'predict' && !state.loaded) loadCatalog();
}

elements.search.addEventListener('input', (event) => renderBooks(event.target.value));
elements.form.addEventListener('submit', predict);
elements.form.addEventListener('reset', () => { window.setTimeout(() => { elements.search.value = ''; renderBooks(); clearMessages(); }, 0); });
window.addEventListener('hashchange', route);
route();
