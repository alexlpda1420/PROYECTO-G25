# Resumen Global de Datasets de Aurelion 📊

Este documento presenta un resumen detallado de los datasets utilizados en el sistema de ventas **Aurelion**, describiendo su estructura, tipos de datos y relaciones entre las tablas. 

---

## 📋 Resumen de Datasets

| **Dataset**          | **Descripción General**                                             | **Nº de Columnas** | **Tipo de Información Principal** | **Clave Primaria**    | **Claves Foráneas Relacionadas**             |
|----------------------|---------------------------------------------------------------------|--------------------|-----------------------------------|-----------------------|---------------------------------------------|
| `clientes.xlsx`       | Registro de clientes registrados en el sistema de ventas           | 5                  | Datos personales                 | `id_cliente`          | -                                           |
| `productos.xlsx`      | Catálogo de productos disponibles para la venta                     | 4                  | Información de inventario        | `id_producto`         | -                                           |
| `ventas.xlsx`         | Registro de transacciones comerciales realizadas                    | 6                  | Datos de ventas                  | `id_venta`            | `id_cliente` → `clientes.id_cliente`        |
| `detalle_ventas.xlsx` | Detalle línea por línea de los productos incluidos en cada venta    | 6                  | Desglose de cada transacción     | `id_detalle`          | `id_venta` → `ventas.id_venta`<br>`id_producto` → `productos.id_producto` |

---

## 📈 Dataset: `clientes.xlsx`

### 1. Fuente y Definición

| **Aspecto**  | **Descripción**                                                         |
|--------------|-------------------------------------------------------------------------|
| **Fuente**   | Registro interno de clientes en el sistema de ventas Aurelion           |
| **Definición** | Contiene la información básica de identificación de los clientes registrados |

### 2. Estructura del Dataset

| **Columna**  | **Descripción**                           | **Tipo de Dato** |
|--------------|-------------------------------------------|------------------|
| `id_cliente` | Identificador único del cliente          | Entero           |
| `nombre_cliente`     | Nombre completo del cliente               | Texto            |
| `ciudad`  | Dirección de domicilio del cliente       | Texto            |
| `fecha_alta`   | Fecha de alta de cliente           | Texto            |
| `email`      | Correo electrónico del cliente           | Texto            |

### 3. Tipo y Escala

| **Variable** | **Tipo**                | **Escala**               |
|--------------|-------------------------|--------------------------|
| `id_cliente` | Cuantitativa discreta    | Nominal (clave primaria) |
| `nombre_cliente`     | Cualitativa              | Nominal                  |
| `ciudad`  | Cualitativa              | Nominal                  |
| `fecha_alta`   | Cualitativa              | Nominal                  |
| `email`      | Cualitativa              | Nominal                  |

---

## 📦 Dataset: `productos.xlsx`

### 1. Fuente y Definición

| **Aspecto**  | **Descripción**                                                        |
|--------------|------------------------------------------------------------------------|
| **Fuente**   | Catálogo interno de productos del supermercado Aurelion                |
| **Definición** | Contiene el listado de productos disponibles para la venta             |

### 2. Estructura del Dataset

| **Columna**   | **Descripción**                                           | **Tipo de Dato** |
|---------------|-----------------------------------------------------------|------------------|
| `id_producto` | Identificador único del producto                         | Entero           |
| `nombre_producto`      | Nombre o descripción del producto                         | Texto            |
| `categoria`   | Categoría del producto (ej: bebidas, alimentos, limpieza) | Texto            |
| `precio_unitario`      | Precio unitario del producto                              | Decimal          |

### 3. Tipo y Escala

| **Variable**  | **Tipo**                | **Escala**               |
|---------------|-------------------------|--------------------------|
| `id_producto` | Cuantitativa discreta    | Nominal (clave primaria) |
| `nombre_producto`      | Cualitativa              | Nominal                  |
| `categoria`   | Cualitativa              | Nominal                  |
| `precio_unitario`      | Cuantitativa continua    | Razón                    |

---

## 💰 Dataset: `ventas.xlsx`

### 1. Fuente y Definición

| **Aspecto**  | **Descripción**                                                      |
|--------------|----------------------------------------------------------------------|
| **Fuente**   | Registro de transacciones comerciales                                |
| **Definición** | Contiene la información de cada venta realizada en Aurelion          |

### 2. Estructura del Dataset

| **Columna**   | **Descripción**                            | **Tipo de Dato** |
|---------------|--------------------------------------------|------------------|
| `id_venta`    | Identificador único de la venta            | Entero           |
| `fecha` | Fecha en la que se realizó la venta       | Fecha            |
| `id_cliente`  | Identificador del cliente asociado        | Entero           |
| `nombre_cliente`  | Nombre Identificador del cliente asociado        | Texto           |
| `email`      | Correo electrónico del cliente           | Texto            |
| `medio_pago`       | Informacion de medio de pago       | Texto          |

### 3. Tipo y Escala

| **Variable**  | **Tipo**                | **Escala**               |
|---------------|-------------------------|--------------------------|
| `id_venta`    | Cuantitativa discreta    | Nominal (clave primaria) |
| `fecha` | Cuantitativa discreta    | Intervalo                |
| `id_cliente`  | Cuantitativa discreta    | Nominal (clave foránea)  |
| `nombre_cliente`     | Cualitativa              | Nominal                  |
| `email`      | Cualitativa              | Nominal                  |
| `medio_pago`       | Cualitativa       | Nominal          |

---

## 🧾 Dataset: `detalle_ventas.xlsx`

### 1. Fuente y Definición

| **Aspecto**  | **Descripción**                                                        |
|--------------|------------------------------------------------------------------------|
| **Fuente**   | Registro asociado a cada ítem vendido en una transacción               |
| **Definición** | Contiene el detalle línea por línea de los productos incluidos en cada venta |

### 2. Estructura del Dataset

| **Columna**   | **Descripción**                                       | **Tipo de Dato** |
|---------------|-------------------------------------------------------|------------------|
| `id_detalle`  | Identificador único del detalle de venta             | Entero           |
| `id_venta`    | Identificador de la venta asociada                   | Entero           |
| `id_producto` | Identificador del producto vendido                   | Entero           |
| `nombre_producto`      | Nombre o descripción del producto                         | Texto            |
| `cantidad`    | Cantidad del producto en la venta                    | Entero           |
| `precio_unitario`    | Precio por unidad | Decimal          |
| `importe`    | Monto correspondiente a la línea (precio x cantidad) | Decimal          |

### 3. Tipo y Escala

| **Variable**  | **Tipo**                | **Escala**               |
|---------------|-------------------------|--------------------------|
| `id_detalle`  | Cuantitativa discreta    | Nominal (clave primaria) |
| `id_venta`    | Cuantitativa discreta    | Nominal (clave foránea)  |
| `id_producto` | Cuantitativa discreta    | Nominal (clave foránea)  |
| `nombre_producto`    | Cualitativa   | Nominal                    |
| `cantidad`    | Cuantitativa discreta    | Razón                    |
| `precio_unitario`    | Cuantitativa | Razón          |
| `importe`    | Cuantitativa | Razón          |

---

## 📚 Consideraciones Finales

Este documento resume las principales características y relaciones entre los datasets que forman parte del sistema de ventas **Aurelion**. A través de este análisis, se puede obtener una visión clara de la estructura de los datos y su utilidad para futuras consultas y análisis.

---
