document.addEventListener('session-ready', ({ detail: user }) => {
  document.querySelector('#greeting').textContent = `Olá, ${user.name}`;
});
