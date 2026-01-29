#!/usr/bin/python3
from cd import cd #importamos a cd.py
import os #importo la libreria que da acceso al sistema operativo
import sys
import datetime #Para horario restringido y timestamp
import getpass #Para obtener usuario del sistema
import socket #Para obtener IP local

#---------------------------------------------------------------------------------------------

USUARIOS_PERMITIDOS = ["diana", "admin", "root", "mati"] #lista de usuarios permitidos
USUARIO_LOGUEADO = None #guarda el usuario que hizo login

LOG_DIR = "/var/log/shell" #direccion de logs
SHELL_LOG_PATH = os.path.join(LOG_DIR, "shell.log") #ruta shell.log
ERROR_LOG_PATH = os.path.join(LOG_DIR, "sistema_error.log") #ruta sistema_error.log


def ensure_log_dir(): #crea /var/log/shell si no existe
    try:
        os.makedirs(LOG_DIR, exist_ok=True) #crea directorio de logs
        return True 
    except PermissionError:
        print("No tengo permisos para crear /var/log/shell") #manejo permisos
        return False


def get_local_ip(): #obtiene IP local
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #socket UDP
        s.connect(("8.8.8.8", 80)) #no manda datos, solo fuerza IP local
        ip = s.getsockname()[0] #obtiene IP local usada
        s.close() #cierra socket
        return ip #devuelve IP
    except:
        return "127.0.0.1" #fallback


def log_action(comando, mensaje, resultado): # func log
    try:
        if not ensure_log_dir(): #verifica que exista /var/log/shell
            return #si no se pudo crear sale de la shell

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #timestamp (datetime)(tiempo actual)(strftime es para formatear en cierto formato)
        ip = get_local_ip() #consegumos IP local
        user_sistema = getpass.getuser() #nombre de laa compu
        user_shell = USUARIO_LOGUEADO if USUARIO_LOGUEADO else "-" #usuario del login del shell

        with open(SHELL_LOG_PATH, "a") as f: #usa /var/log/shell/shell.log
            f.write(f"[{ts}] ip={ip} user_shell={user_shell} user_sys={user_sistema} resultado={resultado} cmd={comando} msg={mensaje}\n") #parametros de informacion para log
    except PermissionError:
        print("No tengo permisos para escribir en /var/log/shell/shell.log") #caso de que no tenga permisos


def horario_restringido(): #bloquea comandos entre 00:00 y 06:00
    hora = datetime.datetime.now().hour #obtiene la hora actual
    return hora >= 0 and hora < 6 #retorna True si esta en rango restringido


def login(): #login solo los usuarios de la lista
    global USUARIO_LOGUEADO #para guardar el usuario logueado
    usuario = input("login: ").strip() #pide usuario
    if usuario in USUARIOS_PERMITIDOS: #valida esta en la lista
        USUARIO_LOGUEADO = usuario #guarda usuario
        log_action("login", f"Acceso permitido para {usuario}", "EXITO") #caso de exito que va al log
        return True #permite entrar a la shell
    else:
        print("Acceso denegado") #caso de que no este permitido
        log_action("login", f"Acceso denegado para {usuario}", "FRACASO") #caso de fracaso que va al log
        return False #no te deja entrar

#---------------------------------------------------------------------------------------------

def log_error(mensaje): #guarda errores en sistema_error.log
    try:
        if not ensure_log_dir(): #asegura que exista /var/log/shell
            return #devuelve cuando no se pudo crear

        with open(ERROR_LOG_PATH, "a") as f: #usa /var/log/shell/sistema_error.log
            f.write(mensaje + "\n") #agrega lo que este en mensaje al final de la linea y despues el salto de liena
    except PermissionError: #caso de error 
        print("No tengo permisos para escribir en /var/log/shell/sistema_error.log") #mensaje actualizado


def execute_command(cmd): #verfico el comando que quiere ejecutar             caso 1
    log_action(' '.join(cmd), "<- comando recibido", "EXITO") #log del comando exito
    if cmd[0] == "cd": #caso de que sea cd
        if len(cmd) == 2: #verifico que el vector tenga solo 2 elementos
            try: #manejo de errores para cd
                cd(cmd[1]) 
                log_action(cmd[0], f"Se movio al directorio {cmd[1]}", "EXITO") #log de exito
            except Exception as e: #por si cd() falla
                print("Error al cambiar de directorio") 
                log_error(f"cd: error -> {cmd[1]} ({e})") #registra el error
                log_action(cmd[0], f"Fallo cd hacia {cmd[1]}", "FRACASO") #manda al log fracaso
        else:
            print("Usa cd bien") #Mensaje de error
            log_action(cmd[0], f"Uso de CD erroneo", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "pwd": #caso pwd(saber donde estas)               caso 2
        if len(cmd) == 1: #si la longitud del vector es 1
            print(os.getcwd()) #Imprime donde estas
            log_action(cmd[0], f"Mostro el directorio actual", "EXITO") #manda al log exito
        else:
            print("Error: muchos argumentos") #Mensaje de error sin hay mas de 3 palabras
            log_action(cmd[0], f"Comando PWD mal utilizado", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "ls": #Caso LS ()                                   caso 3
        if len(cmd) == 1:
            for elem in os.listdir(): #recorre el directorio actual
                if os.path.isdir(elem): #verifica si es un directorio
                    print(f"|-| {elem}") #directorios
                else:
                    print(f"- {elem}") #archivos
            log_action(cmd[0], f"Lectura de la carpeta realizado", "EXITO") #manda al log exit

        elif len(cmd) == 2:
            try: 
                for elem in os.listdir(cmd[1]): #recorre el path indicado
                    ruta = os.path.join(cmd[1], elem) #arma la ruta completa
                    if os.path.isdir(ruta): #verifica si es directorio
                        print(f"|_| {elem}") #muestra directorio con formato especial
                    else:
                        print(f"- {elem}") #muestra archivo con formato especial
                log_action(cmd[0], f"Lectura de carpetas {cmd[1]}", "EXITO") #manda al log exito

            except FileNotFoundError: #caso de error especifico y despues lo agrega a log
                print("No se encontro el path", cmd[1])
                log_error(f"ls: path inexistente -> {cmd[1]}") #------ registra en sistema_error.log
                log_action(cmd[0], f"Error al encontrar el path {cmd[1]}", "FRACASO") #manda al log fracaso
        else:
            print("Error al usar el comando LS") #caso de que use mal LS
            log_action(cmd[0], f"Comando mal utilizado", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "echo": #Caso echo (imprime texto y redirige a archivo)
        if len(cmd) > 1:       #verifica que haya algo despues del echo
            if ">" in cmd: 
                pos = cmd.index(">") #posicion del >
                if pos + 1 >= len(cmd): #valida que exista archivo despues de >
                    print("echo: falta el archivo despues de >") #mensaje de error
                    log_action(cmd[0], "Falta archivo despues de >", "FRACASO") #manda al log fracaso
                    return #corta en caso de que falle
                texto = " ".join(cmd[1:pos])  #texto que se va escribir
                archivo = cmd[pos + 1] #nombre del archivo
                try:
                    with open(archivo, "w") as f: #abre el archivo en modo escritura
                        f.write(texto + "\n") #escribe 
                    log_action(cmd[0], f"Redireccion a {archivo}", "EXITO") #manda al log exito
                except PermissionError: #caso de eeror especifico
                    print("echo: permiso denegado:", archivo)
                    log_error(f"echo: permiso denegado -> {archivo}") #manda sistema_error.log
                    log_action(cmd[0], f"Permiso denegado {archivo}", "FRACASO") #manda al log fracaso
            else:
                for i in range(1, len(cmd)): #imprime despues del 0
                    print(cmd[i], end=" ") #borra lo del final
                print("") #salto de linea
                log_action(cmd[0], f"Aplico un ECHO", "EXITO") #manda al log exito
        else:
            print("echo: falta texto") #mensaje de aviso
            log_action(cmd[0], "Falta texto", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "mkdir":   # Caso Mkdir (Crea un directorio)                   caso 5
        if len(cmd) > 1: 
            for folder in cmd[1:]: #for de folder desde la posi 1 hasta el final de la cadena
                try:
                    os.mkdir(folder)
                    log_action(cmd[0], f"Creo un directorio de nombre {folder}", "EXITO") #manda al log exito
                except FileExistsError:
                    print("Ya existe esa carpeta:", folder)
                    log_action(cmd[0], f"Ya existe {folder}", "FRACASO") #manda al log fracaso
                except PermissionError:
                    print("mkdir: permiso denegado:", folder) #mensaje  si tiene error de permisos
                    log_error(f"mkdir: permiso denegado -> {folder}") #manda al sistema_error fracaso
                    log_action(cmd[0], f"Permiso denegado {folder}", "FRACASO") #manda al log fracaso
        else:
            print("Uso incorrecto, ejemplo: mkdir <ARCHIVO>")
            log_action(cmd[0], f"No utilizo el comando con todos los argumentos", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "cp": #Caso cp (copia un archivo)
        if len(cmd) == 3: #verifica origen y destino
            try: #maneja errores
                if os.path.isdir(cmd[1]): #caso de que se seleccione un directorio en el origen
                    print("cp: el origen es un directorio:", cmd[1])
                    log_action("cp", f"Origen es directorio {cmd[1]}", "FRACASO") #manda al log fracaso
                else:
                    if os.path.exists(cmd[2]): #confirmacion si el destino ya existe (sobrescritura)
                        confirmacion = input(f"El archivo {cmd[2]} ya existe. ¿Deseas sobrescribirlo? (s/n): ") #si deseas reescribir
                        if confirmacion.lower() != "s": #en el caso de que sea no
                            print("Operacion cancelada") #mesaje de cancelacion
                            log_action("cp", f"Cancelado sobrescribir {cmd[2]}", "EXITO") #manda exito en caso de que cancele
                            return #devuelve sin salir

                    # Copia manual haciendo llamadas a SO
                    fd_origen = os.open(cmd[1], os.O_RDONLY)
                    fd_destino = os.open(cmd[2], os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o666)

                    try: #asegura que cierre aunque falle el while
                        while True:
                            bloque = os.read(fd_origen, 4096) #lee por bloques
                            if not bloque:
                                break
                            os.write(fd_destino, bloque) #escribe en destino
                    finally: #cierra los archivos
                        os.close(fd_origen)
                        os.close(fd_destino)

                    log_action("cp", f"Copio {cmd[1]} -> {cmd[2]}", "EXITO") #manda al log exito

            except FileNotFoundError: #caso error
                print("cp: archivo no encontrado")
                log_error(f"cp: archivo inexistente -> {cmd[1]}") #manda sistema_error.log
                log_action("cp", "Archivo no encontrado", "FRACASO") #manda al log fracaso
            except PermissionError: #caso error
                print("cp: permiso denegado")
                log_error(f"cp: permiso denegado -> {cmd[1]} o {cmd[2]}") #manda a sistema_error.log
                log_action("cp", "Permiso denegado", "FRACASO") #manda al log fracaso
        else:
            print("Comando cp mal utilizado debe ser: cp <origen> <destino>")
            log_action("cp", "Uso incorrecto", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "cat":  #caso cat (muestra el contenido de un archivo)
        if len(cmd) == 2:  #verifica que se pase un archivo
            try:
                with open(cmd[1], "r") as f: #abre en modo letura y el f es para que lea linea por linea
                    for linea in f:      #lee linea por linea
                        print(linea, end="")  #end=" " para no agregar saltos extra
                log_action(cmd[0], f"Mostro el contenido de {cmd[1]}", "EXITO") #manda al log exito
            except FileNotFoundError:
                print("cat: archivo no encontrado:", cmd[1]) #caso de error especifico
                log_error(f"cat: archivo inexistente -> {cmd[1]}") #manda a sistema_error.log
                log_action(cmd[0], f"Archivo inexistente {cmd[1]}", "FRACASO") #manda al log fracaso
            except PermissionError:
                print("cat: permiso denegado:", cmd[1]) #caso de error especifico
                log_error(f"cat: permiso denegado -> {cmd[1]}") #manda sistema_error.log
                log_action(cmd[0], f"Permiso denegado {cmd[1]}", "FRACASO") #manda al log fracaso
        else:
            print("Comando cat mal utilizado debe ser: cat <archivo>") #mensaje de error
            log_action(cmd[0], "Uso incorrecto: falta (cat <archivo>)", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "exit": #caso exit (tiene que salir de la shell).        caso 7
        if len(cmd) == 1: #verifico el tamaño del vector
            print("Hasta Luego :)") #Mensaje de Despedida
            log_action("exit", "Salida del shell", "EXITO") #manda al log exito
            sys.exit(0) #sale de la shell (parametro de que termino)
        else:
            print("El comando de Exit tiene mas de un argumento: comando invalido") #Manejo de errores
            log_action(cmd[0], f"Intento fallido de salir del sistema", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "rm":  #Caso rm (elimina un archivo)
        if len(cmd) == 2: #verifica que  el vector tenga 2 comp
            try:
                if os.path.isdir(cmd[1]): #verifica si el argumento es un directorio
                    print("No se puede borrar un directorio", cmd[1]) #muestra error si es directorio
                    log_action("rm", f"Intento borrar directorio {cmd[1]}", "FRACASO") #manda al log fracaso
                else:
                    confirmacion = input(f"¿Seguro que deseas borrar {cmd[1]}? (s/n): ") #pide confirmacion
                    if confirmacion.lower() == "s": #verifica si el usuario confirma (s)
                        os.remove(cmd[1]) #elimina el archivo manualmente
                        log_action("rm", f"Borro {cmd[1]}", "EXITO")  #manda al log exito si borro
                    else:
                        print("Operacion cancelada") #caso ponga n
                        log_action("rm", f"Cancelado borrar {cmd[1]}", "EXITO") #manda al log exito si cancela
            except FileNotFoundError: #caso si el archivo no existe
                print("rm: archivo no encontrado:", cmd[1]) #muestra error si no encuentra
                log_error(f"rm: archivo inexistente -> {cmd[1]}") #registra el error en sistema-error.log
                log_action("rm", f"Archivo inexistente {cmd[1]}", "FRACASO") #manda al log fracaso
            except PermissionError: #caso de que no tenga permisos
                print("rm: permiso denegado:", cmd[1]) #muestra error de permisos
                log_error(f"rm: permiso denegado -> {cmd[1]}") #registra el error en sistema_error.log
                log_action("rm", f"Permiso denegado {cmd[1]}", "FRACASO") #manda al log fracaso
        else:
            print("Comando rm mal utilizado deberia ser: rm <archivo>") #muestra uso correcto
            log_action("rm", "Uso incorrecto", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    else: #Para que pueda ejecutar comandos externos
        try:
            pid = os.fork() #crea un proceso 
            if pid == 0: #ejecuta el comando externo
                try: #try para capturar fallo de execvp
                    os.execvp(cmd[0], cmd) #ejecuta el comando externo
                except FileNotFoundError:
                    print("Comando no encontrado") 
                    log_action(cmd[0], "Comando externo no encontrado", "FRACASO") #manda al log fracaso
                    os._exit(1) #termina si falla
                except PermissionError:
                    print("Permiso denegado") 
                    log_action(cmd[0], "Permiso denegado al ejecutar comando externo", "FRACASO") #manda al log fracaso
                    os._exit(1) #termina si falla
                except OSError as e:
                    print("Error al ejecutar comando") 
                    log_action(cmd[0], f"Error OS al ejecutar externo: {e}", "FRACASO") #manda al log fracaso
                    os._exit(1) #termina si falla
            else:
                os.waitpid(pid, 0) #sincroniza
                log_action(cmd[0], "Comando externo ejecutado (o finalizado)", "EXITO") #manda al log exito si termina
        except OSError as e:
            print("Error al crear proceso")
            log_action(cmd[0], f"Error OS al forkar: {e}", "FRACASO") #manda al log fracaso

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

def limpiar_input(input): #se le pasa el input
    input = input.split() #pone en un vector las palabras sin los espacios
    return input #devuelve el input limpio

def main():
    if not login(): #obliga login antes de entrar al shell
        sys.exit(1) #si falla login sale

    while True: #para que se ejecute siempre
        current_path = os.getcwd().split("/")[-1] #carpeta donde estoy
        try: #detecta el ctrl c y ctrl d para que no se cierre la shell
            u_input = input(f"[SHELL SO]{current_path} % ")
        except KeyboardInterrupt: #caso ctrl c
            print("\nintento de salida detectada si quiere salir use el comando exit") 
            log_action("Ctrl+C", "Intento de salida con Ctrl+C", "FRACASO") #manda al log fracaso
            continue
        except EOFError: #Caso ctrl d
            print("\nintento de salida detectada si quiere salir use el comando exit") #mensaje para el usuario
            log_action("Ctrl+D", "Intento de salida con Ctrl+D", "FRACASO") #manda al log fracaso
            continue

        command = limpiar_input(u_input) #retorna lista
        if not command:
            print("Porfavor ingresa algun comando") #mensaje de error
        else:
            if horario_restringido() and command[0] != "exit": #No entra si esta en horario restringido
                print("Horario restringido: no se permite ejecutar comandos entre las 00:00 y 06:00") #mensaje de bloqueo
                log_action(command[0], "Bloqueado por horario No perimitido", "FRACASO") #manda al log fracaso
            else:
                execute_command(command) #funcion principal

main()