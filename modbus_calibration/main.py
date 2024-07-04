import os
import platform
import time
import struct
from datetime import datetime
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

TIMEOUT = 60

def clear_terminal():
    system = platform.system()
    
    if system == 'Windows':
        os.system('cls')  # Windows
    else:
        os.system('clear')  # macOS et Linux

def write_register_and_wait(client, register, value, slave_address):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"{now[:-3]} Register [{register}] value [{value}]")
    
    # Check if the value exceeds the allowed range for a 16-bit unsigned integer
    if value > 65535:
        print("Value exceeds the allowed range for a 16-bit unsigned integer.")
        return
    
    # Use 'H' for a 16-bit unsigned integer
    encoded_value = struct.pack(">H", value)
    
    # Write the register with the encoded value
    response = client.write_register(register, struct.unpack(">H", encoded_value)[0], slave_address)
    
    if response.isError():
        print(f"Error writing to register {register}: {response}")

def get_input(prompt, default=None, type_func=str):
    """Utility function to get user input with a specific type."""
    while True:
        try:
            user_input = input(prompt)
            if not user_input and default is not None:
                return default
            return type_func(user_input)
        except ValueError:
            print(f"Please enter a valid value of type {type_func.__name__}.")

def main():
    try:
        # Ask the user for the Modbus server IP address, port, and slave address
        clear_terminal()
        SERVER_HOST = get_input("Enter the Modbus server IP address (e.g., 192.168.33.177): ", '192.168.33.177')
        SERVER_PORT = get_input("Enter the Modbus server port (e.g., 502): ", 502, int)
        SLAVE_ADDRESS = get_input("Enter the Modbus slave address (e.g., 1): ", 1, int)

        client = ModbusTcpClient(SERVER_HOST, SERVER_PORT)
        client.connect()

        while True:
            try:
                clear_terminal()
                wavelength = int(input("Enter the wavelength to calibrate (1 to 3) or Ctrl-C to quit: "))
                
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
                        print("Please enter a number between 1 and 4.")
                        continue
                
                oldSensitivity = oldSensitivity_response.registers[0] if oldSensitivity_response else 0
                oldSensitivityDivided = oldSensitivity / 100

                # Read the measured value as a float
                try:
                    measured_value = float(input("Enter the measured value from the calibration device: "))
                    # Apply the factor of 100 and convert to integer
                    value_to_write = int(measured_value * 100)
                except ValueError:
                    print("Please enter a valid numeric value.")
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
                        print("Error.")
                        continue

                newSensitivity = newSensitivity_response.registers[0] if newSensitivity_response else 0
                newSensitivityDivided = newSensitivity / 100

                print(f"Calibration complete: old value {oldSensitivityDivided:.2f} new sensitivity value: {newSensitivityDivided:.2f}")
            except ValueError:
                print("Please enter valid integer numbers.")

    except ConnectionException as e:
        print(f"Unable to connect to Modbus server: {e}")

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        client.close()

if __name__ == '__main__':
    main()
