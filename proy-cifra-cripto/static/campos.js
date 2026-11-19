// Muestra solo los bloques [data-metodos] que corresponden al método elegido.
(function () {
  var metodo = document.getElementById('metodo');
  if (!metodo) return;
  function mostrarCampos() {
    document.querySelectorAll('[data-metodos]').forEach(function (el) {
      el.hidden = el.dataset.metodos.split(' ').indexOf(metodo.value) === -1;
    });
  }
  metodo.addEventListener('change', mostrarCampos);
  mostrarCampos();
})();
