from cd import cd #importamos a cd.py
import os #importo la libreria que da acceso al sistema operativo
import sys
import datetime #Para horario restringido y timestamp
import getpass #Para obtener usuario del sistema
import socket #Para obtener IP local

#---------------------------------------------------------------------------------------------

USUARIOS_PERMITIDOS = ["diana", "admin", "root"] #lista de usuarios permitidos
USUARIO_LOGUEADO = None #guarda el usuario que hizo login


def get_local_ip(): #obtiene IP local (si falla, devuelve 127.0.0.1)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  #socket UDP
        s.connect(("8.8.8.8", 80)) #no manda datos, solo fuerza IP local
        ip = s.getsockname()[0] #obtiene IP local usada
        s.close() #cierra socket
        return ip #devuelve IP
    except:
        return "127.0.0.1" #fallback


def log_action(comando, mensaje, nivel="INFO"): #log detallado: IP, usuario, nivel, timestamp
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") #timestamp (datetime)(tiempo actual)(strftime es para formatear en cierto formato)
        ip = get_local_ip() #consegumos IP local
        user_sistema = getpass.getuser() #Nombre del sistema
        user_shell = USUARIO_LOGUEADO if USUARIO_LOGUEADO else "-" #usuario del login del shell
        with open("shell.log", "a") as f: #archivo de acciones
            f.write(f"[{ts}] ip={ip} user_shell={user_shell} user_sys={user_sistema} level={nivel} cmd={comando} msg={mensaje}\n") #linea de log
    except PermissionError:
        print("No tengo permisos para escribir en shell.log") #manejo de error de permisos


def horario_restringido(): #bloquea comandos entre 00:00 y 06:00
    hora = datetime.datetime.now().hour #obtiene hora actual
    return hora >= 0 and hora < 6 #retorna True si esta en rango restringido


def login(): #login simple (solo los usuarios de la lista)
    global USUARIO_LOGUEADO #para guardar el usuario logueado
    usuario = input("login: ").strip() #pide usuario
    #caso de que este en la lista
    if usuario in USUARIOS_PERMITIDOS: #valida usuario permitido
        USUARIO_LOGUEADO = usuario #guarda usuario
        log_action("login", f"Acceso permitido para {usuario}", "INFO") #log de login ok
        return True #permite entrar al shell
    else:
        print("Acceso denegado") #mensaje de bloqueo
        log_action("login", f"Acceso denegado para {usuario}", "WARN") #log de login fallido
        return False #no permite entrar

#---------------------------------------------------------------------------------------------

def log_error(mensaje):  # guarda errores en sistema_error.log
    try:
        with open("sistema_error.log", "a") as f: #abre el archivo y escribe al final
            f.write(mensaje + "\n") #añade lo que este en mensaje al final de la linea y despues el salto de liena
    except PermissionError: #casi de error 
        print("No tengo permisos para escribir en sistema_error.log") #caso de que no tenga permisos


def execute_command(cmd): #verfico el comando que quiere ejecutar(parametro el primer dato del vector)       caso 1
    log_action(' '.join(cmd), "<- comando ejecutado", "INFO") #join es junta cada argumento del vector y sepra por un espacio
    if cmd[0] == "cd": #caso de que sea cd
        if len(cmd) == 2: #verifico que el vector tenga solo 2 elementos
            cd(cmd[1]) 
            log_action(cmd[0], f"Se movio al directorio {cmd[1]}", "INFO")
        else:
            print("Usa cd bien") #Mensaje de error
            log_action(cmd[0], f"Uso de CD erroneo", "ERROR")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "pwd": #caso pwd(saber donde estas)               caso 2
        if len(cmd) == 1: #si la longitud del vector es 1
            print(os.getcwd()) #Imprime donde estas
            log_action(cmd[0], f"Se ubico donde estaba {cmd[0]}", "INFO")
        else:
            print("Error: muchos argumentos") #Mensaje de error sin hay mas de 3 palabras
            log_action(cmd[0], f"Comando PWD mal utilizado", "INFO")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "ls": #Caso LS ()                                   caso 3
        if len(cmd) == 1:
            print(os.listdir())
            log_action(cmd[0], f"Lectura de la carpeta realizado", "INFO")
        elif len(cmd) == 2:
            try: 
                print(os.listdir(cmd[1]))
                log_action(cmd[0], f"Lectura de carpetas {cmd[1]}", "INFO")
            except FileNotFoundError:
                print("No se encontro el path", cmd[1])
                log_action(cmd[0], f"Error al econtrar el archivo {cmd[1]}", "ERROR")
        else:
            print("Error al usar el comando LS")
            log_action(cmd[0], f"Comando mal utilizado", "ERROR")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "echo": #Caso echo (imprime texto y redirige a archivo)
        if len(cmd) > 1:       #verifica que haya algo despues del echo
            if ">" in cmd: 
                pos = cmd.index(">") #posicion del >
                texto = " ".join(cmd[1:pos])  #texto que se va escribir
                archivo = cmd[pos + 1] #nombre del archivo
                try:
                    with open(archivo, "w") as f: #abre el archivo en modo escritura
                        f.write(texto + "\n") #ecribe 
                        log_action(cmd[0], f"Creo un archivo de nombre", "INFO")
                except PermissionError: #caso de eeror especifico
                    print("echo: permiso denegado:", archivo)
                    log_action(cmd[0], f"Error al de permisos al utilizar Echo", "ERROR")
            else:
                for i in range(1, len(cmd)): #imprime despues del 0
                    print(cmd[i], end=" ") #borra lo del final
                log_action(cmd[0], f"Aplico un ECHO de una palabra", "INFO")
                print("") #salto de linea

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "mkdir":   # Caso Mkdir (Crea un directorio)                   caso 5
        if len(cmd) > 1: 
            for folder in cmd[1:]: #for de folder desde la posi 1 hasta el final de la cadena
                try:
                    os.mkdir(folder)
                    log_action(cmd[0], f"Creo un directorio de nombre {cmd[1]}", "INFO")
                except FileExistsError:
                    print("Ya existe esa carpeta:", folder)
                    log_action(cmd[0], f"Error al utilizar el comando MKDIR", "ERROR")
        else:
            print("Uso incorrecto, ejemplo: mkdir <ARCHIVO>")
            log_action(cmd[0], f"No utilizo el comando con todos los argumentos", "ERROR")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "cp": #Caso cp (copia un archivo)
        if len(cmd) == 3: #verifica origen y destino
            try: #maneja errores
                if os.path.isdir(cmd[1]): #caso de que se seleccione un directorio en el origen
                    print("cp: el origen es un directorio:", cmd[1])
                else:
                    if os.path.exists(cmd[2]): #confirmacion si el destino ya existe (sobrescritura)
                        confirmacion = input(f"El archivo {cmd[2]} ya existe. ¿Deseas sobrescribirlo? (s/n): ") #si deseas reescribir
                        if confirmacion.lower() != "s": #en el caso de que sea no
                            print("Operacion cancelada") #mesaje de cancelacion
                            log_action("cp", f"Cancelado sobrescribir {cmd[2]}", "INFO")  # ---- log de cancelacion
                            return #devuelve sin salir
                        log_action("cp", f"Sobrescritura confirmada {cmd[2]}", "CRITICAL")  # ---- log destructivo

                    # Copia manual usando llamadas del SO (open/read/write)
                    fd_origen = os.open(cmd[1], os.O_RDONLY)
                    fd_destino = os.open(cmd[2], os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o666)

                    while True:
                        bloque = os.read(fd_origen, 4096) #lee por bloques
                        if not bloque:
                            break
                        os.write(fd_destino, bloque) #escribe en destino

                    os.close(fd_origen)
                    os.close(fd_destino)

                    log_action("cp", f"Copio {cmd[1]} -> {cmd[2]}", "INFO") # ---- log de copia ok

            except FileNotFoundError: #caso error
                print("cp: archivo no encontrado")
                log_error(f"cp: archivo inexistente -> {cmd[1]}") # ---- registra en sistema_error.log
                log_action("cp", "Archivo no encontrado", "ERROR") # ---- log detallado
            except PermissionError: #caso error
                print("cp: permiso denegado")
                log_error(f"cp: permiso denegado -> {cmd[1]} o {cmd[2]}") # ---- registra en sistema_error.log
                log_action("cp", "Permiso denegado", "ERROR") # ---- log detallado
        else:
            print("Comando cp mal utilizado debe ser: cp <origen> <destino>")


#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "cat":  #caso cat (muestra el contenido de un archivo)
        if len(cmd) == 2:  #verifica que se pase un archivo
            try:
                with open(cmd[1], "r") as f: #abre en modo letura y el f es para que lea linea por linea
                    for linea in f:      #lee linea por linea
                        print(linea, end="")  #end=" " para no agregar saltos extra
                        log_action(cmd[0], f"Utilizo el comando {cmd[0]}", "INFO")
            except FileNotFoundError:
                print("cat: archivo no encontrado:", cmd[1]) #caso de error especifico
                log_action(cmd[0], f"Error al encontrar el archivo {cmd[1]}", "ERROR")
            except PermissionError:
                print("cat: permiso denegado:", cmd[1]) #caso de error especifico
                log_action(cmd[0], f"Error de permisos {cmd[1]}", "ERROR")
        else:
            print("Comando cat mal utilizado debe ser: cat <archivo>")
            log_action(cmd[0], f"Error al leer el archivo {cmd[1]}", "ERROR")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "exit": #caso exit (tiene que salir de la shell).        caso 7
        if len(cmd) == 1: #verifico el tamaño del vector
            print("Hasta Luego :)") #Mensaje de Despedida
            log_action("exit", "Salida del shell", "INFO")  # ---- log de salida
            sys.exit(0) #sale de la shell (parametro de que termino)
        else:
            print("El comando de Exit tiene mas de un argumento: comando invalido") #Manejo de errores
            log_action(cmd[0], f"Intento fallido de salir del sistema", "ERROR")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "rm":  #Caso rm (elimina un archivo)
        if len(cmd) == 2: #verifica que  el vector tenga 2 comp
            try:
                if os.path.isdir(cmd[1]): #verifica si el argumento es un directorio
                    print("No se puede borrar un directorio", cmd[1]) #muestra error si es directorio
                else:
                    confirmacion = input(f"¿Seguro que deseas borrar {cmd[1]}? (s/n): ") #pide confirmacion
                    if confirmacion.lower() == "s": #verifica si el usuario confirma (s)
                        os.remove(cmd[1]) #elimina el archivo manualmente
                        log_action("rm", f"Borro {cmd[1]}", "CRITICAL")  # ---- log destructivo
                    else:
                        print("Operacion cancelada") #caso ponga n
                        log_action("rm", f"Cancelado borrar {cmd[1]}", "INFO")  # ---- log de cancelacion
            except FileNotFoundError: #caso si el archivo no existe
                print("rm: archivo no encontrado:", cmd[1]) #muestra error si no encuentra
                log_error(f"rm: archivo inexistente -> {cmd[1]}") #registra el error en sistema-error.log
                log_action("rm", f"Archivo inexistente {cmd[1]}", "ERROR")  # ---- log detallado
            except PermissionError: #caso de que no tenga permisos
                print("rm: permiso denegado:", cmd[1]) #muestra error de permisos
                log_error(f"rm: permiso denegado -> {cmd[1]}")  # ---- registra en sistema_error.log
                log_action("rm", f"Permiso denegado {cmd[1]}", "ERROR")  # ----log detallado
        else:
            print("Comando rm mal utilizado deberia ser: rm <archivo>") #muestra uso correcto

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    else:
        print("Comando no encontrado") #Menja de error si no existe el comando
        log_action(cmd[0], "Comando no encontrado", "WARN") #log de comando invalido

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

def limpiar_input(input): #se le pasa el input
    input = input.split() #pone en un vector las palabras sin los espacios
    return input #devuelve el input limpio

def main():
    if not login():  # ---- obliga login antes de entrar al shell
        sys.exit(1)  # ---- si falla login, sale

    while True: #para que se ejecute siempre
        current_path = os.getcwd().split("/")[-1] # carpeta donde estoy
        u_input = input(f"[SHELL SO]{current_path} % ")
        command = limpiar_input(u_input) #retorna lista
        if not command:
            print("Porfavor ingresa algo") #mensaje de error
        else:
            if horario_restringido() and command[0] != "exit":  # ---- bloquea por horario restringido
                print("Horario restringido: no se permite ejecutar comandos entre 00:00 y 06:00")  # ---- mensaje de bloqueo
                log_action(command[0], "Bloqueado por horario restringido", "WARN")  # ---- log de bloqueo
            else:
                execute_command(command)

main()
