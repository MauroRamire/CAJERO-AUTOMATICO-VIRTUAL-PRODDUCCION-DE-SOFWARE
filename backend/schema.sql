-- Tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nombre        VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE NOT NULL,
    documento     VARCHAR(50) UNIQUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla de cuentas
CREATE TABLE IF NOT EXISTS cuentas (
    id SERIAL PRIMARY KEY,
    numero_cuenta  VARCHAR(30) UNIQUE NOT NULL,
    cliente_id     INTEGER NOT NULL REFERENCES clientes(id),
    saldo          NUMERIC(15,2) NOT NULL DEFAULT 0,
    pin_hash       VARCHAR(200) NOT NULL,
    estado         VARCHAR(20) NOT NULL DEFAULT 'ACTIVA', -- ACTIVA / BLOQUEADA
    fecha_creacion TIMESTAMP DEFAULT NOW()
);

-- Tabla de movimientos
CREATE TABLE IF NOT EXISTS movimientos (
    id SERIAL PRIMARY KEY,
    cuenta_id      INTEGER NOT NULL REFERENCES cuentas(id),
    tipo           VARCHAR(20) NOT NULL, -- RETIRO, DEPOSITO, TRANSFERENCIA
    monto          NUMERIC(15,2) NOT NULL,
    fecha          TIMESTAMP DEFAULT NOW(),
    descripcion    VARCHAR(255),
    saldo_resultante NUMERIC(15,2) NOT NULL
);
