// Mostrar alerta personalizada
function mostrarAlerta() {
  alert("¡Hola! Este es un mensaje personalizado usando JavaScript.");
}

// Validación del formulario
document.getElementById("contactForm").addEventListener("submit", function (e) {
  e.preventDefault(); // Evita el envío real del formulario

  let nombre = document.getElementById("nombre");
  let correo = document.getElementById("correo");
  let mensaje = document.getElementById("mensaje");

  let esValido = true;

  // Validar nombre
  if (!nombre.value.trim()) {
    nombre.classList.add("is-invalid");
    esValido = false;
  } else {
    nombre.classList.remove("is-invalid");
  }

  // Validar correo
  if (!correo.value.trim() || !correo.value.includes("@")) {
    correo.classList.add("is-invalid");
    esValido = false;
  } else {
    correo.classList.remove("is-invalid");
  }

  // Validar mensaje
  if (!mensaje.value.trim()) {
    mensaje.classList.add("is-invalid");
    esValido = false;
  } else {
    mensaje.classList.remove("is-invalid");
  }

  if (esValido) {
    alert("Formulario enviado correctamente.");
    this.reset(); // Limpiar formulario
  }
});