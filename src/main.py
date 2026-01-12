from cd import cd #importamos a cd.py
import os #importo la libreria que da acceso al sistema operativo
import sys


def log_error(mensaje):  # guarda errores en sistema_error.log
    try:
        with open("sistema_error.log", "a") as f:
            f.write(mensaje + "\n")
    except PermissionError:
        print("No tengo permisos para escribir en sistema_error.log")


def execute_command(cmd): #verfico el comando que quiere ejecutar(parametro el primer dato del vector)       caso 1
    if cmd[0] == "cd": #caso de que sea cd
        if len(cmd) == 2: #verifico que el vector tenga solo 2 elementos
            cd(cmd[1]) 
        else:
            print("Usa cd bien") #Mensaje de error

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "pwd": #caso pwd(saber donde estas)               caso 2
        if len(cmd) == 1: #si la longitud del vector es 1
            print(os.getcwd()) #Imprime donde estas
        else:
            print("Error: muchos argumentos") #Mensaje de error sin hay mas de 3 palabras

#/////////////////////////////////////////////////////////////////////////////////////////////////////////
    #hacer lindo
    elif cmd[0] == "ls": #Caso LS ()                                   caso 3
        if len(cmd) == 1:
            print(os.listdir())
        elif len(cmd) == 2:
            try: 
                print(os.listdir(cmd[1]))
            except FileNotFoundError:
                print("No se encontro el path", cmd[1])
        else:
            print("Error al usar el comando LS")

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
                except PermissionError: #caso de eeror especifico
                    print("echo: permiso denegado:", archivo)
            else:
                for i in range(1, len(cmd)): #imprime despues del 0
                    print(cmd[i], end=" ") #borra lo del final
                print("") #salto de linea

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "mkdir":   # Caso Mkdir (Crea un directorio)                   caso 5
        if len(cmd) > 1: 
            for folder in cmd[1:]: #for de folder desde la posi 1 hasta el final de la cadena
                try:
                    os.mkdir(folder)
                except FileExistsError:
                    print("Ya existe esa carpeta:", folder)
        else:
            print("Uso incorrecto, ejemplo: mkdir <ARCHIVO>")

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
                            return #devuelve sin salir

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

            except FileNotFoundError: #caso error
                print("cp: archivo no encontrado")
            except PermissionError: #caso error
                print("cp: permiso denegado")
        else:
            print("Comando cp mal utilizado debe ser: cp <origen> <destino>")


#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "cat":  #caso cat (muestra el contenido de un archivo)
        if len(cmd) == 2:  #verifica que se pase un archivo
            try:
                with open(cmd[1], "r") as f: #abre en modo letura y el f es para que lea linea por linea
                    for linea in f:      #lee linea por linea
                        print(linea, end="")  #end=" " para no agregar saltos extra
            except FileNotFoundError:
                print("cat: archivo no encontrado:", cmd[1]) #caso de error especifico
            except PermissionError:
                print("cat: permiso denegado:", cmd[1]) #caso de error especifico
        else:
            print("Comando cat mal utilizado debe ser: cat <archivo>")

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    elif cmd[0] == "exit": #caso exit (tiene que salir de la shell).        caso 7
        if len(cmd) == 1: #verifico el tamaño del vector
            print("Hasta Luego :)") #Mensaje de Despedida
            sys.exit(0) #sale de la shell (parametro de que termino)
        else:
            print("El comando de Exit tiene mas de un argumento: comando invalido") #Manejo de errores
            #sys.exit(1)

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
                    else:
                        print("Operacion cancelada") #caso ponga n
            except FileNotFoundError: #caso si el archivo no existe
                print("rm: archivo no encontrado:", cmd[1]) #muestra error si no encuentra
                log_error(f"rm: archivo inexistente -> {cmd[1]}") #registra el error en sistema-error.log
            except PermissionError: #caso de que no tenga permisos
                print("rm: permiso denegado:", cmd[1]) #muestra error de permisos
        else:
            print("Comando rm mal utilizado deberia ser: rm <archivo>") #muestra uso correcto

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

    else:
        print("Comando no encontrado") #Menja de error si no existe el comando

#/////////////////////////////////////////////////////////////////////////////////////////////////////////

def limpiar_input(input): #se le pasa el input
    input = input.split() #pone en un vector las palabras sin los espacios
    return input #devuelve el input limpio

def main():
    while True: #para que se ejecute siempre
        current_path = os.getcwd().split("/")[-1] # carpeta donde estoy
        u_input = input(f"[SHELL SO]{current_path} % ")
        command = limpiar_input(u_input) #retorna lista
        if not command:
            print("Porfavor ingresa algo") #mensaje de error
        else:
            execute_command(command)

main()
