#!/bin/sh

echo "=== INICIO PRUEBAS LFSSHELL ==="

echo ""
echo "[SETUP] Creando entorno de pruebas"
mkdir pruebas
cd pruebas || exit 1

echo "Hola" > a.txt
echo "Mundo" > b.txt

echo ""
echo "[LS] Directorio con archivos"
ls

echo ""
echo "[LS] Directorio vacío"
mkdir vacio
ls vacio

echo ""
echo "[LS] Ruta relativa"
ls vacio

echo ""
echo "[LS] Ruta absoluta"
ls /

echo ""
echo "[LS] Directorio inexistente (error esperado)"
ls no_existe

echo ""
echo "[CD] cd a subdirectorio"
cd vacio
pwd

echo ""
echo "[CD] cd a .."
cd ..
pwd

echo ""
echo "[CD] cd a ruta inválida (error esperado)"
cd no_existe

echo ""
echo "[CD] cd sin argumentos (política definida por implementación)"
cd
pwd

echo ""
echo "[CP] Archivo a archivo"
cp a.txt a_copia.txt
ls
cat a_copia.txt

echo ""
echo "[CP] Archivo inexistente (error esperado)"
cp inexistente.txt copia.txt

echo ""
echo "[CP] Destino sin permisos (error esperado)"
mkdir sin_permiso
chmod 000 sin_permiso
cp a.txt sin_permiso/a.txt
chmod 755 sin_permiso

echo ""
echo "[RM] Archivo existente"
rm a_copia.txt
ls

echo ""
echo "[RM] Archivo inexistente (error esperado)"
rm no_existe.txt

echo ""
echo "[RM] Archivo sin permisos (error esperado)"
chmod 000 b.txt
rm b.txt
chmod 644 b.txt

echo ""
echo "[MKDIR] Directorio simple"
mkdir nuevo
ls

echo ""
echo "[MKDIR] Directorio ya existente (error esperado)"
mkdir nuevo

echo ""
echo "[MKDIR] Directorio anidado (según política de implementación)"
mkdir dir1/dir2

echo ""
echo "[ECHO] Texto simple"
echo Hola mundo

echo ""
echo "[ECHO] Texto con comillas"
echo "Hola mundo"

echo ""
echo "[CAT] Archivo existente"
cat a.txt

echo ""
echo "[CAT] Archivo inexistente (error esperado)"
cat no_existe.txt

echo ""
echo "[PWD] Verificación de ruta actual"
pwd

echo ""
echo "[EXIT] Cierre limpio de la shell"
exit
