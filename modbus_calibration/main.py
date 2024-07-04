import time
import struct
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

TIMEOUT = 60

def write_register_and_wait(client, register, value, slave_address):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"{now[:-3]} Registre [{register}] valeur [{value}]")
    
    # Vérifier si la valeur dépasse la plage autorisée pour un entier non signé de 16 bits
    if value > 65535:
        print("La valeur dépasse la plage autorisée pour un entier non signé de 16 bits.")
        return
    
    # Utiliser 'H' pour un entier non signé de 16 bits
    encoded_value = struct.pack(">H", value)
    
    # Écrire le registre avec la valeur encodée
    response = client.write_register(register, struct.unpack(">H", encoded_value)[0], slave_address)
    
    if response.isError():
        print(f"Erreur lors de l'écriture du registre {register}: {response}")

def get_input(prompt, default=None, type_func=str):
    """Fonction utilitaire pour obtenir une entrée utilisateur avec un type spécifique."""
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
            return type_func(user_input)
        except ValueError:
            print(f"Veuillez entrer une valeur valide de type {type_func.__name__}.")

def main():
    try:
        # Demander à l'utilisateur l'adresse IP, le port et l'adresse de l'esclave
        SERVER_HOST = get_input("Entrez l'adresse IP du serveur Modbus (par exemple, 192.168.33.177) : ", '192.168.33.177')
        SERVER_PORT = get_input("Entrez le port du serveur Modbus (par exemple, 502) : ", 502, int)
        SLAVE_ADDRESS = get_input("Entrez l'adresse de l'esclave Modbus (par exemple, 1) : ", 1, int)

        client = ModbusTcpClient(SERVER_HOST, SERVER_PORT)
        client.connect()

        while True:
            try:
                wavelength = int(input("Entrez le wavelength à calibrer 1 à 4 : "))
                
                oldSensitivity = 0

                match wavelength:
                    case 1:
                        client.write_register(0, 300, SLAVE_ADDRESS)
                        oldSensitivity_response = client.read_holding_registers(26, 1, SLAVE_ADDRESS)
                    case 2:
                        client.write_register(0, 301, SLAVE_ADDRESS)
                        oldSensitivity_response = client.read_holding_registers(27, 1, SLAVE_ADDRESS)
                    case 3:
                        client.write_register(0, 302, SLAVE_ADDRESS)
                        oldSensitivity_response = client.read_holding_registers(28, 1, SLAVE_ADDRESS)
                    case 4:
                        client.write_register(0, 303, SLAVE_ADDRESS)
                        oldSensitivity_response = client.read_holding_registers(29, 1, SLAVE_ADDRESS)
                    case _:
                        print("Veuillez entrer un chiffre entre 1 et 4.")
                        continue
                
                oldSensitivity = oldSensitivity_response.registers[0] if oldSensitivity_response else 0
                oldSensitivityDivided = oldSensitivity / 100

                # Lire la valeur mesurée en tant que float
                try:
                    measured_value = float(input("Entrez la valeur mesurée sur l'appareil de calibration : "))
                    # Appliquer le facteur 100 et convertir en entier
                    value_to_write = int(measured_value * 100)
                except ValueError:
                    print("Veuillez entrer une valeur numérique valide.")
                    continue

                write_register_and_wait(client, 128, value_to_write, SLAVE_ADDRESS)
                write_register_and_wait(client, 0, 310, SLAVE_ADDRESS)
                
                time.sleep(1)

                newSensitivity = 0

                match wavelength:
                    case 1:
                        newSensitivity_response = client.read_holding_registers(26, 1, SLAVE_ADDRESS)
                    case 2:
                        newSensitivity_response = client.read_holding_registers(27, 1, SLAVE_ADDRESS)
                    case 3:
                        newSensitivity_response = client.read_holding_registers(28, 1, SLAVE_ADDRESS)
                    case 4:
                        newSensitivity_response = client.read_holding_registers(29, 1, SLAVE_ADDRESS)
                    case _:
                        print("Erreur.")
                        continue

                newSensitivity = newSensitivity_response.registers[0] if newSensitivity_response else 0
                newSensitivityDivided = newSensitivity / 100

                print(f"Calibration terminée : ancienne valeur {oldSensitivityDivided:.2f} nouvelle valeur pour la sensibilité : {newSensitivityDivided:.2f}")
            except ValueError:
                print("Veuillez entrer des nombres entiers valides.")

    except ConnectionException as e:
        print(f"Impossible de se connecter au serveur Modbus : {e}")

    except KeyboardInterrupt:
        print("Interruption par l'utilisateur.")
    finally:
        client.close()

if __name__ == '__main__':
    main()
