# AGENTS.md

## Contexto del proyecto

Este repositorio forma parte de un laboratorio académico de Seguridad de Redes. Su objetivo es demostrar un ataque Man-in-the-Middle mediante ARP Spoofing dentro de un entorno controlado, junto con su contramedida técnica.

## Uso autorizado

El contenido de este repositorio debe interpretarse únicamente como material educativo. Los scripts y comandos están diseñados para ejecutarse en GNS3, EVE-NG, PNETLab o laboratorios propios autorizados.

No se debe utilizar este material en redes públicas, empresariales o de terceros sin autorización explícita.

## Elementos esperados del repositorio

- `README.md`: guía principal tipo how-to.
- `arp-mitm.py`: script principal del laboratorio.
- `mitigacion-arp-mitm.md`: explicación de contramedidas.
- `images/`: capturas utilizadas como evidencia.
- `docs/documentacion-tecnica-profesional.pdf`: documentación formal detallada.
- `docs/documentacion-tecnica-profesional.docx`: versión editable del documento técnico.

## Flujo técnico esperado

1. Verificar el estado ARP normal en PC1 y R-1.
2. Ejecutar el script desde Kali.
3. Observar el envenenamiento ARP en PC1 y R-1.
4. Demostrar impacto mediante bloqueo ICMP con `iptables`.
5. Aplicar Dynamic ARP Inspection con ARP ACL estática.
6. Verificar que las asociaciones IP-MAC legítimas se mantienen.

## Criterios de revisión

Un revisor automático o humano debe validar:

- Que el ataque se ejecuta en un laboratorio autorizado.
- Que las capturas evidencian el antes, durante y después del ataque.
- Que el README contiene instrucciones claras y reproducibles.
- Que la mitigación corresponde directamente al ataque demostrado.
- Que el repositorio incluye autoría, video demostrativo y documentación técnica profesional.

## Autor

Michael David Robles Fermín / iClexi  
Matrícula: 2025-0845
