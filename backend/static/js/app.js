// ===============================================
// CONFIGURACIÓN
// ===============================================
const API_URL = window.location.origin;
// Para Azure solo cambias esta URL por la de tu backend.
let cuentaActual = null;

// ===============================================
// UTILIDADES DE UI
// ===============================================
function show(screenId) {
    document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
    document.getElementById(screenId).classList.add("active");
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text || "";
}

// ===============================================
// LOGIN (número de cuenta + PIN)
// ===============================================
document.getElementById("form-login").addEventListener("submit", async (e) => {
    e.preventDefault();
    setText("login-error", "");

    const numero_cuenta = document.getElementById("login-usuario").value.trim();
    const pin = document.getElementById("login-pin").value.trim();

    if (!numero_cuenta || !pin) {
        setText("login-error", "Debes ingresar usuario y PIN");
        return;
    }

    try {
        // El backend /login actualmente es un mock (email/password).
        // Mandamos numero_cuenta en email y pin en password solo para cumplir la firma.
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: numero_cuenta,
                password: pin
            })
        });

        if (!res.ok) {
            setText("login-error", "No se pudo iniciar sesión");
            return;
        }

        // Login ok → guardamos la cuenta actual y vamos al menú
        cuentaActual = numero_cuenta;
        setText("user-info", `Cuenta: ${cuentaActual}`);
        show("screen-menu");
        await cargarSaldo(); // opcional: cargar saldo de una vez
    } catch (err) {
        console.error(err);
        setText("login-error", "Error de red al iniciar sesión");
    }
});

// ===============================================
// CERRAR SESIÓN
// ===============================================
// ===============================================
// CERRAR SESIÓN
// ===============================================
document.getElementById("btn-logout").addEventListener("click", () => {
    cuentaActual = null;
    document.getElementById("user-info").textContent = "";
    showScreen("screen-login");
});


// ===============================================
// NAVEGACIÓN DESDE MENÚ
// ===============================================
document.querySelectorAll("[data-screen]").forEach(btn => {
    btn.addEventListener("click", async () => {
        const target = btn.dataset.screen;

        // hooks especiales
        if (target === "screen-saldo") {
            await cargarSaldo();
        } else if (target === "screen-historial") {
            await cargarHistorial();
        }

        show(target);
    });
});

// ===============================================
// CONSULTAR SALDO
// ===============================================
async function cargarSaldo() {
    if (!cuentaActual) return;

    try {
        const res = await fetch(
            `${API_URL}/saldo?numero_cuenta=${encodeURIComponent(cuentaActual)}`
        );
        const data = await res.json();

        if (!res.ok || data.status === "error") {
            setText("saldo-actual", "Error al consultar saldo");
            return;
        }

        const saldo = Number(data.saldo || 0);
        setText("saldo-actual", `$ ${saldo.toLocaleString("es-CO")}`);
    } catch (err) {
        console.error(err);
        setText("saldo-actual", "Error de red al consultar saldo");
    }
}

// ===============================================
// RETIRO
// ===============================================
document.getElementById("form-retiro").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!cuentaActual) return;

    const monto = Number(document.getElementById("retiro-monto").value);
    if (!monto || monto <= 0) {
        setText("retiro-msg", "Monto inválido");
        return;
    }

    const pin = prompt("Confirma tu PIN:");
    if (!pin) {
        setText("retiro-msg", "Operación cancelada");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/retiro`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                numero_cuenta: cuentaActual,
                monto,
                pin
            })
        });

        const data = await res.json();

        if (!res.ok) {
            setText("retiro-msg", data.detail || "Error al realizar el retiro");
            return;
        }

        const nuevoSaldo = Number(data.nuevo_saldo || 0);
        setText(
            "retiro-msg",
            `Retiro exitoso. Nuevo saldo: $ ${nuevoSaldo.toLocaleString("es-CO")}`
        );
        await cargarSaldo();
    } catch (err) {
        console.error(err);
        setText("retiro-msg", "Error de red al realizar el retiro");
    }
});

// ===============================================
// DEPÓSITO
// ===============================================
document.getElementById("form-deposito").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!cuentaActual) return;

    const monto = Number(document.getElementById("deposito-monto").value);
    if (!monto || monto <= 0) {
        setText("deposito-msg", "Monto inválido");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/deposito`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                numero_cuenta: cuentaActual,
                monto
            })
        });

        const data = await res.json();

        if (!res.ok) {
            setText("deposito-msg", data.detail || "Error al realizar el depósito");
            return;
        }

        const nuevoSaldo = Number(data.nuevo_saldo || 0);
        setText(
            "deposito-msg",
            `Depósito exitoso. Nuevo saldo: $ ${nuevoSaldo.toLocaleString("es-CO")}`
        );
        await cargarSaldo();
    } catch (err) {
        console.error(err);
        setText("deposito-msg", "Error de red al realizar el depósito");
    }
});

// ===============================================
// TRANSFERENCIA
// ===============================================
document.getElementById("form-transferencia").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!cuentaActual) return;

    const cuenta_destino = document.getElementById("transfer-destino").value.trim();
    const monto = Number(document.getElementById("transfer-monto").value);
    const pin = prompt("PIN para confirmar la transferencia:");

    if (!cuenta_destino || !monto || monto <= 0 || !pin) {
        setText("transfer-msg", "Datos de transferencia incompletos");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/transferencia`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                cuenta_origen: cuentaActual,
                cuenta_destino,
                monto,
                pin
            })
        });

        const data = await res.json();

        if (!res.ok) {
            setText("transfer-msg", data.detail || "Error al realizar la transferencia");
            return;
        }

        const saldoOrigen = Number(data.nuevo_saldo_origen || 0);
        setText(
            "transfer-msg",
            `Transferencia realizada. Nuevo saldo cuenta origen: $ ${saldoOrigen.toLocaleString("es-CO")}`
        );
        await cargarSaldo();
    } catch (err) {
        console.error(err);
        setText("transfer-msg", "Error de red al realizar la transferencia");
    }
});

// ===============================================
// HISTORIAL
// ===============================================
async function cargarHistorial() {
    if (!cuentaActual) return;

    try {
        const res = await fetch(
            `${API_URL}/historial?numero_cuenta=${encodeURIComponent(cuentaActual)}&limite=10`
        );
        const data = await res.json();

        const movimientos = data.movimientos || [];

        const tbody = document.getElementById("historial-body");
        tbody.innerHTML = "";

        movimientos.forEach(m => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${m.fecha || ""}</td>
                <td>${m.tipo || ""}</td>
                <td>$ ${(Number(m.monto || 0)).toLocaleString("es-CO")}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error(err);
        const tbody = document.getElementById("historial-body");
        tbody.innerHTML = `<tr><td colspan="3">Error al cargar historial</td></tr>`;
    }
}

// ===============================================
// CAMBIAR PIN
// ===============================================
document.getElementById("form-cambiar-pin").addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!cuentaActual) return;

    const pin_actual = document.getElementById("pin-actual").value.trim();
    const pin_nuevo = document.getElementById("pin-nuevo").value.trim();

    if (!pin_actual || !pin_nuevo) {
        setText("pin-msg", "Debes ingresar PIN actual y nuevo");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/cambiarPIN`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                numero_cuenta: cuentaActual,
                pin_actual,
                pin_nuevo
            })
        });

        const data = await res.json();

        if (!res.ok) {
            setText("pin-msg", data.detail || "Error al cambiar PIN");
            return;
        }

        setText("pin-msg", data.message || "PIN cambiado correctamente");
        document.getElementById("pin-actual").value = "";
        document.getElementById("pin-nuevo").value = "";
    } catch (err) {
        console.error(err);
        setText("pin-msg", "Error de red al cambiar PIN");
    }
});

// ===============================================
// BLOQUEAR CUENTA
// ===============================================
document.getElementById("btn-bloquear-confirm").addEventListener("click", async () => {
    if (!cuentaActual) return;

    const motivo = prompt("Motivo del bloqueo:");
    if (!motivo) {
        setText("bloquear-msg", "Operación cancelada");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/bloquearCuenta`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                numero_cuenta: cuentaActual,
                motivo
            })
        });

        const data = await res.json();

        if (!res.ok) {
            setText("bloquear-msg", data.detail || "Error al bloquear la cuenta");
            return;
        }

        setText("bloquear-msg", data.message || "Cuenta bloqueada correctamente");
    } catch (err) {
        console.error(err);
        setText("bloquear-msg", "Error de red al bloquear la cuenta");
    }
});

// ===============================================
// COMPROBANTE
// ===============================================
document.getElementById("form-comprobante").addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("comp-id").value.trim();
    if (!id) return;

    try {
        const res = await fetch(
            `${API_URL}/comprobante?id_transaccion=${encodeURIComponent(id)}`
        );
        const data = await res.json();

        document.getElementById("comp-detalle").textContent =
            JSON.stringify(data, null, 2);
    } catch (err) {
        console.error(err);
        document.getElementById("comp-detalle").textContent =
            "Error al consultar el comprobante";
    }
});

// ===============================================
// BOTONES "VOLVER" → menú principal
// ===============================================
document.querySelectorAll(".btn-secondary").forEach(btn => {
    btn.addEventListener("click", () => show("screen-menu"));
});

document.addEventListener("DOMContentLoaded", () => {
    const logoutBtn = document.getElementById("btn-logout");

    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {

            // 🔵 limpiar sesión en memoria
            cuentaActual = null;

            // 🔵 limpiar textos visibles
            document.getElementById("user-info").textContent = "";
            document.getElementById("saldo-actual").textContent = "";
            document.getElementById("retiro-msg").textContent = "";
            document.getElementById("deposito-msg").textContent = "";
            document.getElementById("transfer-msg").textContent = "";
            document.getElementById("pin-msg").textContent = "";
            document.getElementById("bloquear-msg").textContent = "";
            document.getElementById("comp-detalle").textContent = "";

            // 🔵 limpiar campos de formularios
            document.getElementById("form-login").reset();
            document.getElementById("form-retiro").reset();
            document.getElementById("form-deposito").reset();
            document.getElementById("form-transferencia").reset();
            document.getElementById("form-cambiar-pin").reset();
            document.getElementById("form-comprobante").reset();

            // 🔵 limpiar historial
            document.getElementById("historial-body").innerHTML = "";

            // 🔵 volver al login
            show("screen-login");
        });
    }
});

// 🔵 limpiar clases de error/éxito
document.querySelectorAll(".error-msg, .info-msg, .success-msg").forEach(el => {
    el.textContent = "";
    el.classList.remove("error-msg", "info-msg", "success-msg");
});

// 🔵 limpiar inputs manualmente por si algún formulario no respondió a reset()
document.querySelectorAll("input").forEach(i => i.value = "");

// 🔵 borrar cualquier highlight, borde rojo, borde verde
document.querySelectorAll(".error, .ok").forEach(el => {
    el.classList.remove("error", "ok");
});

// 🔵 impedir volver al menú usando botón del navegador
history.pushState(null, null, location.href);
window.onpopstate = function () {
    history.go(1); // bloquea la navegación hacia atrás
};





