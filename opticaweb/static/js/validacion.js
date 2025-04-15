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