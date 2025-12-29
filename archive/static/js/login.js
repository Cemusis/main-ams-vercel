// password visibility
document.getElementById("togglePassword").onclick = function() {
    const input = document.getElementById("password");
    const icon = this;
    
    if (input.type === "password") {
        input.type = "text";
        this.textContent = "HIDE";
    } else {
        input.type = "password";
        this.textContent = "SHOW";
    }
};

document.getElementById("loginForm").addEventListener("submit", function(e) {
    const email = document.querySelector('input[name="email"]');
    const password = document.querySelector('input[name="password"]');
    
    // client-side validation
    if (!email.value || !password.value) {
        e.preventDefault();
        alert("Please fill in all fields");
        return false;
    }
    
    if (password.value.length < 8) {
        e.preventDefault();
        alert("Password must be at least 8 characters");
        return false;
    }
});