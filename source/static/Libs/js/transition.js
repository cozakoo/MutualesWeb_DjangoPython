$(document).ready(function() {
    $('.dropdown-item').click(function(e) {
      e.preventDefault(); // Evitar el comportamiento predeterminado de los enlaces
      console.log("me active 2")
      var href = $(this).attr('href');
       // Obtener la URL de destino del enlace
       console.log(href)
      $('.cuadrado-background').addClass('animate__fadeOut'); // Agregar clase de animación de salida a un contenedor
      setTimeout(function() {
        window.location.href = href; // Redireccionar a la nueva URL después de la animación
      }, 500); // Ajustar este valor según la duración de la animación de salida
    });
  });
 
