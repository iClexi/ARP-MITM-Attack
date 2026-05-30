# Mitigación contra ARP MitM

## Descripción

Esta mitigación se enfoca en proteger la red contra ataques **ARP MitM**, también conocidos como **ARP Spoofing** o **ARP Poisoning**.

En este tipo de ataque, una máquina atacante envía respuestas ARP falsas para engañar a la víctima y al gateway. El objetivo es que ambos dispositivos asocien direcciones IP legítimas con la dirección MAC del atacante.

Ejemplo del ataque:

```text
Gateway real: 20.25.8.45
Atacante:     20.25.8.46
Víctima:      20.25.8.47
```

El atacante puede enviar ARP falsos diciendo:

```text
20.25.8.45 está en la MAC del atacante
20.25.8.47 está en la MAC del atacante
```

Si el ataque funciona, la víctima cree que Kali es el gateway, y el gateway cree que Kali es la víctima. Esto coloca al atacante en medio de la comunicación.

---

## Contramedida seleccionada

Para este laboratorio se utiliza:

```text
Dynamic ARP Inspection + ARP ACL estática
```

Esta contramedida permite validar manualmente qué combinaciones **IP + MAC** son legítimas dentro de la VLAN.

Se seleccionó esta mitigación porque en esta práctica no se desea repetir las mismas defensas que se usarán en los ataques de DHCP Spoofing, DHCP Starvation, MAC Flooding o STP Claim Root Attack.

---

## Por qué no se usa DHCP Snooping como mitigación principal aquí

DHCP Snooping es una defensa muy útil y escalable, pero en este conjunto de prácticas se reserva para los ataques relacionados con DHCP, como:

```text
DHCP Spoofing
DHCP Starvation
```

Para este ataque ARP MitM se usa una alternativa diferente: **Dynamic ARP Inspection con ARP ACL estática**.

Esta solución es adecuada para laboratorios pequeños o redes con pocos dispositivos críticos, ya que permite definir manualmente qué IP corresponde a qué MAC.

---

## Topología de referencia

```text
                   +----------------+
                   |      R1        |
                   | 20.25.8.45     |
                   | Fa0/0          |
                   +-------+--------+
                           |
                           |
                    Gi0/0  |
                   +-------+--------+
                   |      SW-1      |
                   |    IOSvL2      |
                   +---+--------+---+
                       |        |
                 Gi0/1 |        | Gi0/2
                       |        |
              +--------+        +--------+
              |                          |
        +-----+-----+              +-----+-----+
        |   Kali    |              |    VPC    |
        |20.25.8.46 |              |20.25.8.47 |
        +-----------+              +-----------+
```

---

## Direccionamiento del laboratorio

| Dispositivo | Rol      |  Dirección IP | Descripción                            |
| ----------- | -------- | ------------: | -------------------------------------- |
| R1          | Gateway  | 20.25.8.45/24 | Router principal de la red             |
| Kali        | Atacante | 20.25.8.46/24 | Máquina que ejecuta el ataque ARP MitM |
| VPC         | Víctima  | 20.25.8.47/24 | Equipo afectado por el ataque          |
| SW-1        | Switch   |           N/A | Switch Cisco IOSvL2                    |

---

## Variables que debes cambiar

Antes de aplicar la configuración, reemplaza los valores entre `< >` según tu laboratorio.

| Variable                      | Significado                             | Ejemplo                  |
| ----------------------------- | --------------------------------------- | ------------------------ |
| `<VLAN_ID>`                   | VLAN donde están R1, Kali y la víctima  | `1`                      |
| `<TRUSTED_INTERFACE>`         | Puerto confiable hacia el gateway       | `gigabitEthernet0/0`     |
| `<UNTRUSTED_INTERFACE_RANGE>` | Puertos donde están Kali y la víctima   | `gigabitEthernet0/1 - 2` |
| `<GATEWAY_IP>`                | IP real del gateway                     | `20.25.8.45`             |
| `<GATEWAY_MAC>`               | MAC real del gateway en formato Cisco   | `cc01.0c14.0000`         |
| `<VICTIM_IP>`                 | IP real de la víctima                   | `20.25.8.47`             |
| `<VICTIM_MAC>`                | MAC real de la víctima en formato Cisco | `0050.7966.6800`         |

---

## Nota sobre la VLAN

Si no configuraste una VLAN específica en el switch, normalmente los puertos estarán en la VLAN por defecto:

```text
VLAN 1
```

En ese caso, usa:

```text
<VLAN_ID> = 1
```

Si tu laboratorio usa otra VLAN, reemplaza `<VLAN_ID>` por la VLAN correcta.

---

## Cómo obtener las MAC reales

### En R1

Para ver la MAC real de la interfaz del gateway:

```cisco
show interface fastEthernet0/0
```

También puedes revisar la tabla ARP:

```cisco
show arp
```

### En Kali

```bash
ip -br link
```

### En la VPC

```text
show arp
```

---

## Formato correcto de MAC para Cisco

Cisco IOS usa formato con puntos:

```text
00:0c:29:58:50:08  ->  000c.2958.5008
cc:01:0c:14:00:00  ->  cc01.0c14.0000
00:50:79:66:68:00  ->  0050.7966.6800
```

---

## Configuración genérica de mitigación

```cisco
enable
configure terminal

arp access-list ARP_VALIDOS
permit ip host <GATEWAY_IP> mac host <GATEWAY_MAC>
permit ip host <VICTIM_IP> mac host <VICTIM_MAC>

ip arp inspection vlan <VLAN_ID>
ip arp inspection filter ARP_VALIDOS vlan <VLAN_ID> static

interface <TRUSTED_INTERFACE>
description Puerto_confiable_hacia_gateway
ip arp inspection trust

interface range <UNTRUSTED_INTERFACE_RANGE>
description Puertos_no_confiables_de_usuario
no ip arp inspection trust

end
write memory
```

---

## Configuración aplicada al laboratorio

Reemplaza las MAC de ejemplo por las MAC reales de tu topología.

```cisco
enable
configure terminal

arp access-list ARP_VALIDOS
permit ip host 20.25.8.45 mac host <MAC_REAL_R1>
permit ip host 20.25.8.47 mac host <MAC_REAL_VPC>

ip arp inspection vlan 1
ip arp inspection filter ARP_VALIDOS vlan 1 static

interface gigabitEthernet0/0
description Puerto_confiable_hacia_R1
ip arp inspection trust

interface range gigabitEthernet0/1 - 2
description Puertos_no_confiables_Kali_y_VPC
no ip arp inspection trust

end
write memory
```

---

## Ejemplo con MACs de muestra

Este ejemplo es solo una referencia. Debes cambiar las MAC por las reales de tu laboratorio.

```cisco
enable
configure terminal

arp access-list ARP_VALIDOS
permit ip host 20.25.8.45 mac host cc01.0c14.0000
permit ip host 20.25.8.47 mac host 0050.7966.6800

ip arp inspection vlan 1
ip arp inspection filter ARP_VALIDOS vlan 1 static

interface gigabitEthernet0/0
description Puerto_confiable_hacia_R1
ip arp inspection trust

interface range gigabitEthernet0/1 - 2
description Puertos_no_confiables_Kali_y_VPC
no ip arp inspection trust

end
write memory
```

---

## Explicación de la configuración

### 1. Crear una ARP ACL

```cisco
arp access-list ARP_VALIDOS
permit ip host 20.25.8.45 mac host <MAC_REAL_R1>
permit ip host 20.25.8.47 mac host <MAC_REAL_VPC>
```

Esta lista define las asociaciones IP-MAC permitidas.

En este caso, se permite que:

```text
20.25.8.45 use solamente la MAC real de R1
20.25.8.47 use solamente la MAC real de la VPC
```

Si Kali intenta decir que su MAC corresponde al gateway o a la víctima, el switch detectará que esa asociación no está permitida.

---

### 2. Activar Dynamic ARP Inspection

```cisco
ip arp inspection vlan 1
```

Este comando activa la inspección ARP en la VLAN indicada.

Si tu laboratorio usa otra VLAN, cambia `1` por la VLAN correcta.

---

### 3. Aplicar la ARP ACL a la VLAN

```cisco
ip arp inspection filter ARP_VALIDOS vlan 1 static
```

Este comando le indica al switch que use la ACL `ARP_VALIDOS` para validar paquetes ARP dentro de la VLAN.

---

### 4. Marcar como confiable el puerto hacia R1

```cisco
interface gigabitEthernet0/0
ip arp inspection trust
```

El puerto hacia el gateway se marca como confiable porque conecta con la infraestructura legítima de la red.

---

### 5. Mantener los puertos de usuario como no confiables

```cisco
interface range gigabitEthernet0/1 - 2
no ip arp inspection trust
```

Los puertos hacia Kali y la VPC quedan como no confiables.

Esto permite que el switch inspeccione los paquetes ARP que entran por esos puertos y bloquee los ARP falsificados.

---

## Por qué no es necesario poner la MAC de Kali como válida

En este laboratorio, Kali es la máquina atacante.

La protección busca evitar que Kali falsifique identidades como:

```text
20.25.8.45 -> MAC de Kali
20.25.8.47 -> MAC de Kali
```

Por eso, la ACL debe proteger principalmente las asociaciones legítimas del gateway y la víctima.

Si se desea permitir que Kali use su IP real para pruebas normales, se puede agregar también:

```cisco
permit ip host 20.25.8.46 mac host <MAC_REAL_KALI>
```

Pero para demostrar la mitigación del ataque ARP MitM, lo más importante es proteger:

```text
Gateway real
Víctima real
```

---

## Verificación antes del ataque

En la víctima:

```text
show arp
```

En R1:

```cisco
show arp
```

La víctima debe mostrar la MAC real del gateway, no la MAC de Kali.

---

## Verificación durante el ataque

Ejecutar el script ARP MitM desde Kali:

```bash
sudo python3 arp-mitm.py
```

El script solicitará:

```text
Interfaz atacante
IP de la víctima
IP del gateway
```

Para esta topología:

```text
Interfaz atacante: eth0 o eth1
IP de la víctima: 20.25.8.47
IP del gateway: 20.25.8.45
```

---

## Verificación de la mitigación

Después de aplicar la mitigación, ejecutar:

```cisco
show ip arp inspection
show ip arp inspection statistics
show arp access-list
```

Resultado esperado:

```text
El switch debe bloquear los paquetes ARP falsificados.
La víctima debe mantener la MAC real del gateway.
R1 debe mantener la MAC real de la víctima.
Kali no debe poder colocarse en medio.
```

---

## Validación en la víctima

En la VPC:

```text
show arp
ping 20.25.8.45
show arp
```

La IP del gateway debe seguir asociada a su MAC real, no a la MAC de Kali.

---

## Validación en R1

En R1:

```cisco
show arp
```

La IP de la víctima debe seguir asociada a su MAC real, no a la MAC de Kali.

---

## Resultado esperado

Después de aplicar la mitigación:

* Kali no puede falsificar la identidad del gateway.
* Kali no puede falsificar la identidad de la víctima.
* La víctima mantiene la asociación ARP correcta.
* El router mantiene la asociación ARP correcta.
* El switch registra paquetes ARP bloqueados en las estadísticas de DAI.

---

## Prueba recomendada para el video

1. Mostrar la tabla ARP normal de la víctima.
2. Mostrar la tabla ARP normal de R1.
3. Ejecutar el ataque ARP MitM desde Kali.
4. Mostrar que la víctima asocia el gateway con la MAC de Kali.
5. Mostrar que R1 asocia la víctima con la MAC de Kali.
6. Detener el ataque y restaurar ARP.
7. Aplicar la mitigación con DAI + ARP ACL.
8. Ejecutar nuevamente el ataque.
9. Mostrar que la tabla ARP ya no cambia hacia la MAC de Kali.
10. Mostrar las estadísticas de ARP Inspection bloqueando paquetes falsos.

---

## Mitigación alternativa

Si se desea una solución más escalable en una red real, se recomienda usar:

```text
DHCP Snooping + Dynamic ARP Inspection
```

Sin embargo, en esta práctica se seleccionó **ARP ACL estática** para no repetir las mismas contramedidas que serán usadas en los ataques de DHCP Spoofing y DHCP Starvation.

---

## Recomendación final

Para este laboratorio, la mitigación principal contra ARP MitM es:

```text
Dynamic ARP Inspection + ARP ACL estática
```

Esta solución permite bloquear respuestas ARP falsificadas sin depender de DHCP Snooping.

Aunque no es la opción más escalable para redes grandes, funciona correctamente en laboratorios controlados y redes pequeñas con IPs conocidas.
