import socket

objetivo = "192.168.0.175"

puertos_abiertos = []

print("Escaneando todos los puertos...\n")

for puerto in range(1, 65536):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)

    resultado = sock.connect_ex((objetivo, puerto))

    if resultado == 0:
        print(f"🟢 Puerto {puerto} ABIERTO")
        puertos_abiertos.append(puerto)

    sock.close()

print("\nResumen:")
print("Puertos abiertos:", puertos_abiertos)
print("Total:", len(puertos_abiertos))