# Proyecto 2 – Integración LDAP + Kerberos

**Autor:** Juan Flores
**Script principal:** `FloresJ-Proyecto2.sh`
**Sistema operativo:** Ubuntu (probado en Ubuntu Server con WSL)

---

## 📌 Descripción general

Este proyecto tiene como objetivo **instalar, configurar e integrar LDAP (OpenLDAP) con Kerberos** para lograr autenticación centralizada mediante **GSSAPI**. Además, se habilita el acceso gráfico a LDAP mediante **phpLDAPadmin** desde un navegador web.

El proceso completo se automatiza mediante un script Bash (`FloresJ-Proyecto2.sh`) y se valida con comandos de prueba.

---

## 🧩 Componentes utilizados

* **OpenLDAP (slapd)** – Servicio de directorio
* **Kerberos (MIT Kerberos)** – Autenticación segura
* **SASL / GSSAPI** – Integración LDAP–Kerberos
* **phpLDAPadmin** – Administración web de LDAP
* **Apache2** – Servidor web

---

## 🗂️ Estructura del proyecto

```
Proyecto2/
│
├── FloresJ-Proyecto2.sh   # Script de instalación y configuración
├── README.md              # Documentación del proyecto
└── capturas/              # (Opcional) Evidencias y screenshots
```

---

## ⚙️ Requisitos previos

* Ubuntu actualizado
* Usuario con privilegios `sudo`
* Conectividad de red correcta
* Nombre de host correctamente configurado

Ejemplo:

```
server.fis.epn.edu.ec
```

---

## 🔐 Dominio y Realm usados

* **Dominio LDAP:**

```
dc=fis,dc=epn,dc=edu,dc=ec
```

* **Realm Kerberos:**

```
FIS.EPN.EDU.EC
```

---

## 🚀 Instalación y configuración

La instalación se realiza ejecutando el script:

```bash
chmod +x FloresJ-Proyecto2.sh
sudo ./FloresJ-Proyecto2.sh
```

El script realiza automáticamente:

1. Instalación de paquetes necesarios
2. Configuración de Kerberos (KDC y cliente)
3. Configuración de OpenLDAP
4. Integración LDAP con GSSAPI
5. Creación del servicio `ldap/server.fis.epn.edu.ec`
6. Configuración de phpLDAPadmin
7. Reinicio y validación de servicios

---

## ✅ Pruebas y validación

### Obtener ticket Kerberos

```bash
kinit admin/admin
klist
```

Debe aparecer:

```
krbtgt/FIS.EPN.EDU.EC@FIS.EPN.EDU.EC
```

### Autenticación LDAP con GSSAPI

```bash
ldapwhoami -Y GSSAPI -H ldap://server.fis.epn.edu.ec
```

Resultado esperado:

```
dn:cn=admin,dc=fis,dc=epn,dc=edu,dc=ec
```

---

## 🌐 Acceso vía navegador (phpLDAPadmin)

Abrir en el navegador:

```
http://server.fis.epn.edu.ec/phpldapadmin
```

Credenciales:

* **DN:** `cn=admin,dc=fis,dc=epn,dc=edu,dc=ec`
* **Método:** Simple Bind

---

## ⚠️ Problemas conocidos

* Advertencia PHP:

```
Usage of ldap_connect with two arguments is deprecated
```

> No afecta el funcionamiento, es una advertencia de compatibilidad.

* GSSAPI solo funciona correctamente con el **hostname real**, no con `localhost`.

---

## 📌 Conclusiones

Este proyecto demuestra la correcta integración de **LDAP + Kerberos**, permitiendo autenticación centralizada, segura y escalable, tanto por consola como vía web.

---

## 📚 Referencias

* OpenLDAP Documentation
* MIT Kerberos Documentation
* phpLDAPadmin Official Docs

---

✅ **Proyecto funcional y validado**

