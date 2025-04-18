function validateForm() {
    const password = document.getElementById("password").value;
    const confirmPassword = document.getElementById("confirmPassword").value;
    const email = document.getElementById("email").value;
    const dob = document.getElementById("dob").value;
  
    // Verificar si las contraseñas coinciden
    if (password !== confirmPassword) {
      alert("Las contraseñas no coinciden.");
      return false;
    }
  
    // Verificar la longitud de la contraseña y los caracteres
    const passwordRegex = /^(?=.*[A-Z])(?=.*\d).{6,18}$/;
    if (!passwordRegex.test(password)) {
      alert("La contraseña debe tener al menos un número y una letra mayúscula, y debe tener entre 6 y 18 caracteres.");
      return false;
    }
  
    // Verificar edad (mínimo 13 años)
    const birthDate = new Date(dob);
    const age = new Date().getFullYear() - birthDate.getFullYear();
    if (age < 13) {
      alert("Debes tener al menos 13 años para registrarte.");
      return false;
    }
  
    return true;
  }
  $(document).ready(function () {
    $('#id_region').change(function () {
      var regionId = $(this).val();
  
      if (regionId) {
        $.ajax({
          url: '/obtener-comunas/', // esta URL la defines en urls.py
          data: {
            'region_id': regionId
          },
          success: function (data) {
            var comunaSelect = $('#id_comuna');
            comunaSelect.empty();
            comunaSelect.append('<option value="">Seleccione una comuna</option>');
            data.forEach(function (comuna) {
              comunaSelect.append(`<option value="${comuna.id}">${comuna.nombre}</option>`);
            });
          }
        });
      } else {
        $('#id_comuna').empty();
        $('#id_comuna').append('<option value="">Seleccione una comuna</option>');
      }
    });
  });