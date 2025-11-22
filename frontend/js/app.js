// ===============================================
// CONFIGURACIÓN
// ===============================================
const API = "http://127.0.0.1:8000";

let cuentaActual = null;

// ===============================================
// MOSTRAR PANTALLAS
// ===============================================
function show(screenId) {
    document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
    document.getElementById(screenId).classList.add("active");
}

// ===============================================
// LOGIN
// ===============================================
document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();

    const usuario = document.getElementById("login-usuario").value;
    const pin = document.getElementById("login-pin").value;

    const res = await fetch(`${API}/cuentas/${usuario}`);
    if (!res.ok) {
        document.getElementById("login-error").textContent = "Cuenta no encontrada";
        return;
    }

    const data = await res.json();

    if (data.pin != pin) {
        document.getElementById("login-error").textContent = "PIN incorrecto";
        return;
    }

    cuentaActual = usuario;
    document.getElementById("user-info").textContent = "Usuario: " + data.nombre;

    show("screen-menu");
});


// ===============================================
// CERRAR SESIÓN
// ===============================================
document.getElementById("btn-logout").addEventListener("click", () => {
    console.log("Click en Cerrar sesión");   // para ver en la Consola

    // “Cerrar sesión” en el front
    cuentaActual = null;

    // limpiar campos de login por si acaso
    const userInput = document.getElementById("login-usuario");
    const pinInput  = document.getElementById("login-pin");
    if (userInput) userInput.value = "";
    if (pinInput)  pinInput.value  = "";

    // volver a la pantalla de login
    show("screen-login");
});


// ===============================================
// NAVEGACIÓN DESDE MENÚ
// ===============================================
document.querySelectorAll("[data-screen]").forEach(btn => {
    btn.addEventListener("click", () => {
        show(btn.dataset.screen);
    });
});

// ===============================================
// CONSULTAR SALDO
// ===============================================
async function cargarSaldo() {
    const res = await fetch(`${API}/cuentas/${cuentaActual}`);
    const data = await res.json();
    document.getElementById("saldo-actual").textContent = "$" + data.saldo.toLocaleString();
}

document.querySelector("button[data-screen='screen-saldo']")
    .addEventListener("click", cargarSaldo);

// ===============================================
// RETIRO
// ===============================================
document.getElementById("form-retiro").addEventListener("submit", async (e) => {
    e.preventDefault();

    const monto = Number(document.getElementById("retiro-monto").value);

    const res = await fetch(`${API}/retiro/${cuentaActual}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ monto })
    });

    const data = await res.json();
    document.getElementById("retiro-msg").textContent = data.mensaje;

    cargarSaldo();
});

// ===============================================
// DEPÓSITO
// ===============================================
document.getElementById("form-deposito").addEventListener("submit", async (e) => {
    e.preventDefault();

    const monto = Number(document.getElementById("deposito-monto").value);

    const res = await fetch(`${API}/deposito/${cuentaActual}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ monto })
    });

    const data = await res.json();
    document.getElementById("deposito-msg").textContent = data.mensaje;

    cargarSaldo();
});

// ===============================================
// TRANSFERENCIA
// ===============================================
document.getElementById("form-transferencia").addEventListener("submit", async (e) => {
    e.preventDefault();

    const destino = document.getElementById("transfer-destino").value.trim();
    const monto   = Number(document.getElementById("transfer-monto").value);
    const msgEl   = document.getElementById("transfer-msg");

    msgEl.textContent = "";
    msgEl.style.color = "red";

    // Validación de cuenta: 9 dígitos
    if (!/^\d{9}$/.test(destino)) {
        msgEl.textContent = "Cuenta inválida: debe contener exactamente 9 dígitos.";
        return;
    }

    if (!monto || monto <= 0) {
        msgEl.textContent = "Monto inválido.";
        return;
    }

    const res = await fetch(`${API}/transferencia`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            origen: cuentaActual,
            destino,
            monto
        })
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
        msgEl.textContent = data?.detail || "Error en la transferencia.";
        return;
    }

    msgEl.style.color = "lightgreen";
    msgEl.textContent = data.mensaje || "Transferencia exitosa";

    await cargarSaldo();
});


// ===============================================
// HISTORIAL
// ===============================================
document.querySelector("button[data-screen='screen-historial']")
    .addEventListener("click", async () => {

        const res = await fetch(`${API}/historial/${cuentaActual}`);
        const movimientos = res.ok ? await res.json() : [];

        const tbody = document.getElementById("historial-body");
        tbody.innerHTML = "";

        movimientos.forEach(m => {
            const row = `
                <tr>
                    <td>${m.fecha}</td>
                    <td>${m.tipo}</td>
                    <td>${m.monto}</td>
                </tr>`;
            tbody.innerHTML += row;
        });
    });

// ===============================================
// CAMBIAR PIN
// ===============================================
document.getElementById("form-cambiar-pin").addEventListener("submit", async (e) => {
    e.preventDefault();

    const actual = document.getElementById("pin-actual").value;
    const nuevo  = document.getElementById("pin-nuevo").value;
    const msgEl  = document.getElementById("pin-msg");

    msgEl.textContent = "";
    msgEl.style.color = "red";

    if (!actual || !nuevo) {
        msgEl.textContent = "Debes ingresar el PIN actual y el nuevo.";
        return;
    }

    // Llamar al backend para cambiar el PIN de la cuenta actual
    const res = await fetch(`${API}/cambiar_pin/${cuentaActual}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actual, nuevo })
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
        msgEl.textContent = data?.detail || "Error al cambiar PIN";
        return;
    }

    // Éxito
    msgEl.style.color = "lightgreen";
    msgEl.textContent = data.mensaje || "PIN actualizado correctamente";

    // Opcional: cerrar sesión y volver al login
    cuentaActual = null;
    document.getElementById("login-usuario").value = "";
    document.getElementById("login-pin").value = "";
    show("screen-login");
});



// ===============================================
// BLOQUEAR CUENTA
// ===============================================
document.getElementById("btn-bloquear-confirm").addEventListener("click", async () => {
    const res = await fetch(`${API}/bloquear/${cuentaActual}`, { method: "POST" });
    const data = await res.json();
    document.getElementById("bloquear-msg").textContent = data.mensaje;
});

// ===============================================
// COMPROBANTE
// ===============================================
document.getElementById("form-comprobante").addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("comp-id").value;

    const res = await fetch(`${API}/comprobante/${id}`);

    const data = res.ok ? await res.json() : { mensaje: "No encontrado" };

    document.getElementById("comp-detalle").textContent = JSON.stringify(data, null, 2);
});

// ===============================================
// BOTONES "VOLVER" (excepto Cerrar sesión)
// ===============================================
document.querySelectorAll(".btn-secondary").forEach(btn => {
    btn.addEventListener("click", () => {
        // Si NO es el botón de cerrar sesión, vuelve al menú
        if (btn.id !== "btn-logout") {
            show("screen-menu");
        }
    });
});

