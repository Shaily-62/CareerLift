
function toggleMenu() {
  document.querySelector("nav").classList.toggle("open");
}



  //login

  function openModal(id) {
    document.getElementById(id).style.display = 'flex'
  }

  function closeModal(id) {
    document.getElementById(id).style.display = 'none'
  }

  function switchModal(toLogin = false) {
    document.getElementById('loginModal').style.display = toLogin ? 'flex' : 'none',
    document.getElementById('signupModal').style.display = toLogin ? 'none' : 'flex'
  }


  //validation function
   function validateSignup() {
    const pwd = document.getElementById("password").value;
    const cpwd = document.getElementById("confirm_password").value;

    if (pwd !== cpwd) {
      alert("Passwords do not match!");
      return false;
    }
    return true;
  }

  // Close modal on click outside
  window.onclick = function(event) {
    ['loginModal', 'signupModal'].forEach(id => {
      const modal = document.getElementById(id);
      if (event.target === modal) modal.style.display = "none";
    });
  }


function toggleMenu() {
  document.getElementById("navbar").classList.toggle("active");
}

function openModal(modalId) {
  document.getElementById(modalId).style.display = "flex";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

function switchModal(toLogin = false) {
  closeModal(toLogin ? 'signupModal' : 'loginModal');
  openModal(toLogin ? 'loginModal' : 'signupModal');
}

function validateSignup() {
  const pw = document.getElementById("password").value;
  const cpw = document.getElementById("confirm_password").value;
  if (pw !== cpw) {
    alert("Passwords do not match!");
    return false;
  }
  return true;
}
