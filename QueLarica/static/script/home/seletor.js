function toggleDropdown() {
    document.getElementById("languageDropdown").classList.toggle("show");
  }

window.onclick = function(event) {
    if (!event.target.closest('.language-selector')) {
      document.getElementById("languageDropdown").classList.remove("show");
    }
  }

