function getCookie(name) {
  let value = "; " + document.cookie;
  let parts = value.split("; " + name + "=");
  if (parts.length == 2) {
    return parts.pop().split(";").shift();
  }
}

function goToLogin() {
  window.location.href = `/accounts/login?next=${window.location.pathname}`;
}

const backend = localStorage.getItem("backend");
const keycloakEnabled = localStorage.getItem("keycloak_enabled");
if (window.location.pathname != "/accounts/login") {
  if (keycloakEnabled) {
    let accessToken = localStorage.getItem("accessToken");
    if (accessToken === null) {
      toToLogin();
    }
  } else {
    fetch(`${backend}/accounts/account-profile`, {
      method: "GET",
      credentials: "include",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
      }
    })
    .then(response => {
      const url = new URL(response.url);
      if (response.status == 301 || url.pathname.startsWith('/accounts/login')) {
        goToLogin();
      }
    });
  }
}
  
