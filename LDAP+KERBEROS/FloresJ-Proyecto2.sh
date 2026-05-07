#!/bin/bash
# ==========================================================
# Proyecto 2 - LDAP + Kerberos + GSSAPI
# Autor: Juan Flores
# Archivo: FloresJ-Proyecto2.sh
# ==========================================================

# =========================
# VARIABLES GENERALES
# =========================
REALM="FIS.EPN.EDU.EC"
DOMAIN_DN="dc=fis,dc=epn,dc=edu,dc=ec"
HOSTNAME="server.fis.epn.edu.ec"
LDAP_URI="ldap://$HOSTNAME"
ADMIN_KRB="admin/admin@$REALM"

echo "=========================================="
echo " Instalación y configuración LDAP + Kerberos"
echo "=========================================="

# =========================
# 1. ACTUALIZAR SISTEMA
# =========================
echo "[1/9] Actualizando sistema..."
apt update && apt upgrade -y

# =========================
# 2. INSTALAR PAQUETES NECESARIOS
# =========================
echo "[2/9] Instalando paquetes..."
apt install -y \
slapd ldap-utils \
krb5-kdc krb5-admin-server krb5-user \
libsasl2-modules-gssapi-mit \
phpldapadmin apache2 php php-ldap

# =========================
# 3. CONFIGURAR HOSTNAME
# =========================
echo "[3/9] Configurando hostname..."
hostnamectl set-hostname "$HOSTNAME"

# =========================
# 4. CONFIGURAR KERBEROS
# =========================
echo "[4/9] Configurando Kerberos..."

cat > /etc/krb5.conf <<EOF
[libdefaults]
 default_realm = $REALM
 dns_lookup_realm = false
 dns_lookup_kdc = false

[realms]
 $REALM = {
  kdc = $HOSTNAME
  admin_server = $HOSTNAME
 }

[domain_realm]
 .$HOSTNAME = $REALM
 $HOSTNAME = $REALM
EOF

# =========================
# 5. REINICIAR SERVICIOS KERBEROS
# =========================
echo "[5/9] Reiniciando servicios Kerberos..."
systemctl restart krb5-kdc
systemctl restart krb5-admin-server

# =========================
# 6. CONFIGURAR LDAP PARA GSSAPI
# =========================
echo "[6/9] Configurando LDAP + SASL GSSAPI..."

cat > /etc/sasl2/slapd.conf <<EOF
pwcheck_method: saslauthd
mech_list: gssapi
EOF

systemctl restart slapd

# =========================
# 7. CREAR PRINCIPAL LDAP EN KERBEROS
# =========================
echo "[7/9] Creando principal LDAP en Kerberos..."

kadmin.local <<EOF
addprinc -randkey ldap/$HOSTNAME
ktadd -k /etc/krb5.keytab ldap/$HOSTNAME
quit
EOF

chown openldap:openldap /etc/krb5.keytab
chmod 600 /etc/krb5.keytab

systemctl restart slapd

# =========================
# 8. CONFIGURAR phpLDAPadmin
# =========================
echo "[8/9] Configurando phpLDAPadmin..."

sed -i "s|cn=Manager,dc=example,dc=com|cn=admin,$DOMAIN_DN|g" \
/etc/phpldapadmin/config.php

sed -i "s|secret|admin|g" \
/etc/phpldapadmin/config.php

systemctl restart apache2

# =========================
# 9. PRUEBAS BÁSICAS
# =========================
echo "[9/9] Pruebas finales..."

echo "→ Inicializando ticket Kerberos"
kinit $ADMIN_KRB

echo "→ Ticket activo:"
klist

echo "→ Probando autenticación LDAP con GSSAPI"
ldapwhoami -Y GSSAPI -H $LDAP_URI

echo "=========================================="
echo " Instalación finalizada"
echo " Accede a phpLDAPadmin:"
echo " http://$HOSTNAME/phpldapadmin"
echo "=========================================="

