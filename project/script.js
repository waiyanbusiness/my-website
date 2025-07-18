document.getElementById("contactForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const message = document.getElementById("message").value.trim();

  if (name && email && message) {
    document.getElementById("responseMessage").textContent = `Thanks, ${name}! We'll get back to you soon.`;
    this.reset();
  } else {
    document.getElementById("responseMessage").textContent = `Please fill in all fields.`;
  }
});
