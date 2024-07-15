import os
import shutil
import subprocess
import serial.tools.list_ports
from tqdm import tqdm
from colorama import init, Fore

def print_exylium_title():
    # Texto estático con diferentes colores
    title_lines = [
        Fore.RED + "▄▄▄▄▄▄▄▄▄▄▄  ▄       ▄  ▄         ▄  ▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄         ▄  ▄▄       ▄▄",
        Fore.GREEN + "▐░░░░░░░░░░░▌▐░▌     ▐░▌▐░▌       ▐░▌▐░▌          ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░░▌     ▐░░▌",
        Fore.YELLOW + "▐░█▀▀▀▀▀▀▀▀▀  ▐░▌   ▐░▌ ▐░▌       ▐░▌▐░▌           ▀▀▀▀█░█▀▀▀▀ ▐░▌       ▐░▌▐░▌░▌   ▐░▐░▌",
        Fore.RED + "▐░▌            ▐░▌ ▐░▌  ▐░▌       ▐░▌▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌▐░▌ ▐░▌▐░▌",
        Fore.GREEN + "▐░█▄▄▄▄▄▄▄▄▄    ▐░▐░▌   ▐░█▄▄▄▄▄▄▄█░▌▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌ ▐░▐░▌ ▐░▌",
        Fore.YELLOW + "▐░░░░░░░░░░░▌    ▐░▌    ▐░░░░░░░░░░░▌▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌  ▐░▌  ▐░▌",
        Fore.RED + "▐░█▀▀▀▀▀▀▀▀▀    ▐░▌░▌    ▀▀▀▀█░█▀▀▀▀ ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌   ▀   ▐░▌",
        Fore.GREEN + "▐░▌            ▐░▌ ▐░▌       ▐░▌     ▐░▌               ▐░▌     ▐░▌       ▐░▌▐░▌       ▐░▌",
        Fore.YELLOW + "▐░█▄▄▄▄▄▄▄▄▄  ▐░▌   ▐░▌      ▐░▌     ▐░█▄▄▄▄▄▄▄▄▄  ▄▄▄▄█░█▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌",
        Fore.RED + "▐░░░░░░░░░░░▌▐░▌     ▐░▌     ▐░▌     ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌",
        Fore.GREEN + " ▀▀▀▀▀▀▀▀▀▀▀  ▀       ▀       ▀       ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀ "
    ]

    # Obtener el tamaño actual de la consola
    columns, rows = shutil.get_terminal_size()

    # Calcular los espacios necesarios para centrar el texto verticalmente
    vertical_padding = (rows - len(title_lines)) // 2
    print("\n" * vertical_padding)

    # Imprimir cada línea del título centrada horizontalmente
    for line in title_lines:
        padding = ' ' * ((columns - len(line)) // 2)
        print(padding + line)

def cargar_codigo_esp8266():
    while True:
        try:
            # Pedir el directorio del archivo .bin
            directorio = input("Por favor, especifica el directorio del archivo .bin que deseas cargar a los ESP8266 (o 'q' para salir): ").strip()
            if directorio.lower() == 'q':
                break
            if not os.path.isfile(directorio):
                print(Fore.RED + "El archivo especificado no existe.")
                continue

            # Buscar los puertos seriales disponibles
            puertos = list(serial.tools.list_ports.comports())
            if not puertos:
                print(Fore.RED + "No se encontraron puertos seriales disponibles.")
                continue

            # Iterar sobre los puertos seriales encontrados
            for puerto in puertos:
                try:
                    print(Fore.GREEN + f"Cargando código en el puerto {puerto.device}...")

                    # Comando para cargar el código usando esptool.py
                    comando = f"python -m esptool --port {puerto.device} write_flash 0x00000 {directorio}"

                    # Obtener el tamaño del archivo .bin para la barra de carga
                    tamano_archivo = os.path.getsize(directorio)

                    # Usar tqdm para mostrar una barra de progreso
                    with tqdm(total=tamano_archivo, unit='B', unit_scale=True, desc=f'Cargando en {puerto.device}', position=0, leave=True, ncols=100) as progress:
                        # Iniciar el proceso para cargar el código
                        proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

                        # Leer la salida del proceso línea por línea para actualizar la barra de progreso
                        for line in proceso.stdout:
                            # Buscar el progreso en la línea
                            if "Writing at " in line:
                                percent_index = line.find("(")
                                if percent_index != -1:
                                    percent_str = line[percent_index+1:percent_index+3]
                                    try:
                                        percent = int(percent_str)
                                        progress.update(percent)
                                    except ValueError:
                                        pass

                        # Capturar cualquier error durante el proceso
                        stdout, stderr = proceso.communicate()
                        if proceso.returncode != 0:
                            print(Fore.RED + f"Error al cargar el código en {puerto.device}. Detalles:")
                            print(stderr.strip())
                        else:
                            progress.update(tamano_archivo - progress.n)  # Completar la barra de progreso si no se actualizó al 100%
                            print(f"\n{Fore.GREEN}Carga completada en {puerto.device}.")

                except Exception as e:
                    print(Fore.RED + f"Error al cargar el código en {puerto.device}: {e}")

        except Exception as e:
            print(Fore.RED + f"Ocurrió un error: {e}")

def mostrar_menu():
    print(Fore.CYAN + "Bienvenido a Exylium, recuerda que esto es un programada de codigo abierto desarollado por mindcreator9, mi discord es: mindcreator9.   por favor escoge una de las siguientes funciones a continuación:\n")
    print(Fore.LIGHTGREEN_EX + "A. Cargar código a los ESP8266 conectados en todos los puertos USB.")
    print(Fore.LIGHTRED_EX + "Q. Salir.")

    opcion = input(Fore.CYAN + "Selecciona una opción (A/Q): ").strip().upper()
    return opcion

def main():
    init(autoreset=True)
    print_exylium_title()
    
    while True:
        opcion = mostrar_menu()
        if opcion == 'A':
            cargar_codigo_esp8266()
        elif opcion == 'Q':
            print(Fore.LIGHTRED_EX + "Gracias por usar Exylium. ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
