# =====================================================================
#  TP02 - Programacion I
#  Controlador de misiones
#
#  ESTE ES EL ARCHIVO DONDE ESCRIBIS TU PROGRAMA.
#
#  Antes de ejecutarlo:
#    1. Abri INICIAR_SIMULADOR (elegi G1 o Go2)
#    2. Espera a que aparezca la ventana con el robot
#    3. Recien ahi ejecuta este archivo
#
#  Nombre y apellido:  Kevin Maximiliano
#  Comision:           .....................................
# =====================================================================

from robot import ErrorDeSeguridad, Robot

from misiones import (
    MISION_BASICA,
    MISION_CON_ERRORES,
    MISION_CUADRADO,
    MISION_LARGA,
)

# Misiones adicionales (si no estan en el misiones.py del profesor/companero, se definen como respaldo)
try:
    from misiones import MISION_PATRULLA, MISION_ZIGZAG
except ImportError:
    MISION_ZIGZAG = [
        ("saludar",),
        ("avanzar", 0.2, 2.0),
        ("girar", 0.5, 1.57),
        ("avanzar", 0.15, 2.0),
        ("girar", -0.5, 3.14),
        ("avanzar", 0.15, 2.0),
        ("girar", 0.5, 1.57),
        ("avanzar", 0.2, 2.0),
        ("detenerse",),
    ]

    MISION_PATRULLA = [
        ("avanzar", 0.2, 3.0),
        ("saludar",),
        ("girar", 0.5, 6.28),
        ("girar", 0.5, 6.28),
        ("girar", -0.5, 6.28),
        ("avanzar", 0.2, 3.0),
        ("girar", 0.5, 6.28),
        ("saludar",),
        ("detenerse",),
    ]


# =====================================================================
#  FUNCIONES AUXILIARES
# =====================================================================
def _obtener_motivo_invalido(comando):
    """Devuelve un texto explicando por que un comando no es valido."""
    if not isinstance(comando, (tuple, list)):
        return "El comando debe ser una tupla o lista"
    if len(comando) == 0:
        return "El comando esta vacio"
    accion = comando[0]
    if accion not in ("avanzar", "girar", "detenerse", "saludar"):
        return f"Comando no reconocido o inexistente: '{accion}'"
    if accion in ("detenerse", "saludar"):
        if len(comando) != 1:
            return f"El comando '{accion}' no lleva parametros adicionales"
    elif accion in ("avanzar", "girar"):
        if len(comando) != 3:
            return f"El comando '{accion}' requiere exactamente 2 parametros (velocidad, tiempo)"
        velocidad, tiempo = comando[1], comando[2]
        if isinstance(velocidad, bool) or not isinstance(velocidad, (int, float)):
            return f"La velocidad debe ser un numero, no {type(velocidad).__name__}"
        if isinstance(tiempo, bool) or not isinstance(tiempo, (int, float)):
            return f"El tiempo debe ser un numero, no {type(tiempo).__name__}"
        if tiempo < 0:
            return f"El tiempo no puede ser negativo ({tiempo} s)"
    return "Comando invalido"


# =====================================================================
#  PARTE 1 - Validar un comando
# =====================================================================
def comando_es_valido(comando):
    """Decide si un comando se puede ejecutar. Devuelve True o False.

    Un comando es una tupla. El primer elemento dice que hacer:

        ("avanzar", velocidad, tiempo)    velocidad en m/s, tiempo en s
        ("girar", velocidad, tiempo)      velocidad en rad/s, tiempo en s
        ("detenerse",)
        ("saludar",)

    Cosas que conviene revisar:
      - que la tupla no este vacia
      - que el nombre del comando sea uno de los cuatro validos
      - que tenga la cantidad de datos que corresponde
        (avanzar y girar llevan dos; detenerse y saludar, ninguno)
      - que velocidad y tiempo sean numeros de verdad, no textos ni booleanos
      - que el tiempo no sea negativo
    """
    if not isinstance(comando, (tuple, list)) or len(comando) == 0:
        return False

    accion = comando[0]

    # Comandos sin parametros
    if accion in ("detenerse", "saludar"):
        return len(comando) == 1

    # Comandos con velocidad y tiempo
    if accion in ("avanzar", "girar"):
        if len(comando) != 3:
            return False
        velocidad = comando[1]
        tiempo = comando[2]

        # Validamos que sean numericos y no booleanos (en Python bool hereda de int)
        if isinstance(velocidad, bool) or not isinstance(velocidad, (int, float)):
            return False
        if isinstance(tiempo, bool) or not isinstance(tiempo, (int, float)):
            return False

        # El tiempo no puede ser negativo
        if tiempo < 0:
            return False

        return True

    return False


# =====================================================================
#  PARTE 2 - Ejecutar un comando
# =====================================================================
def ejecutar_comando(robot, comando):
    """Ejecuta UN comando en el robot. Devuelve un texto con lo que paso.

    Ordenes que podes usar:

        robot.avanzar(velocidad=..., tiempo=...)
        robot.girar(velocidad=..., tiempo=...)
        robot.detenerse()
        robot.saludar()

    Ojo: aunque el comando parezca valido, el robot puede rechazarlo
    igual (por ejemplo, si la velocidad supera el limite de la materia).
    Eso llega como un ErrorDeSeguridad y conviene atraparlo.
    """
    accion = comando[0]

    try:
        if accion == "avanzar":
            velocidad = comando[1]
            tiempo = comando[2]
            robot.avanzar(velocidad=velocidad, tiempo=tiempo)
            return f"Avanzo a {velocidad} m/s durante {tiempo} s"

        elif accion == "girar":
            velocidad = comando[1]
            tiempo = comando[2]
            robot.girar(velocidad=velocidad, tiempo=tiempo)
            return f"Giro a {velocidad} rad/s durante {tiempo} s"

        elif accion == "detenerse":
            robot.detenerse()
            return "Robot detenido correctamente"

        elif accion == "saludar":
            robot.saludar()
            return "Robot saludo correctamente"

        else:
            return f"Comando no reconocido: '{accion}'"

    except ErrorDeSeguridad as error:
        return f"Rechazado por seguridad: {error}"


# =====================================================================
#  PARTE 3 - Recorrer la mision entera
# =====================================================================
def ejecutar_mision(robot, mision, historial):
    """Recorre la lista de comandos, uno por uno.

    Por cada comando:
      - si NO es valido, lo rechaza y sigue con el siguiente
      - si es valido, lo ejecuta
      - en los dos casos, guarda en 'historial' que fue lo que paso

    Un comando invalido NO tiene que cortar la mision.
    """
    for comando in mision:
        # Capa 1 de validacion: formato y datos basicos
        if not comando_es_valido(comando):
            motivo = _obtener_motivo_invalido(comando)
            print(f"[RECHAZADO] {comando} -> {motivo}")
            historial.append({
                "comando": comando,
                "estado": "rechazado",
                "motivo": motivo
            })
            continue

        # Capa 2 de validacion: ejecucion y limites del robot
        try:
            resultado = ejecutar_comando(robot, comando)
            if resultado.startswith("Rechazado"):
                print(f"[RECHAZADO] {comando} -> {resultado}")
                historial.append({
                    "comando": comando,
                    "estado": "rechazado",
                    "motivo": resultado
                })
            else:
                print(f"[EJECUTADO] {comando} -> {resultado}")
                historial.append({
                    "comando": comando,
                    "estado": "ejecutado",
                    "motivo": resultado
                })
        except ErrorDeSeguridad as error:
            motivo = f"Rechazado por seguridad: {error}"
            print(f"[RECHAZADO] {comando} -> {motivo}")
            historial.append({
                "comando": comando,
                "estado": "rechazado",
                "motivo": motivo
            })


# =====================================================================
#  PARTE 4 - El reporte final
# =====================================================================
def generar_reporte(historial):
    """Muestra por pantalla un resumen de la mision.

    Tiene que decir, como minimo:
      - cuantos comandos se ejecutaron bien
      - cuantos se rechazaron
      - cual fue el motivo de cada rechazo
    """
    total = len(historial)
    ejecutados = sum(1 for item in historial if item.get("estado") == "ejecutado")
    rechazados = sum(1 for item in historial if item.get("estado") == "rechazado")

    print("\n" + "=" * 60)
    print("                REPORTE FINAL DE MISION")
    print("=" * 60)
    print(f"Total de comandos procesados : {total}")
    print(f"Comandos ejecutados con exito: {ejecutados}")
    print(f"Comandos rechazados          : {rechazados}")
    print("-" * 60)

    if rechazados > 0:
        print("Detalle de motivos de cada rechazo:")
        num = 1
        for item in historial:
            if item.get("estado") == "rechazado":
                cmd = item.get("comando")
                motivo = item.get("motivo")
                print(f"  {num}. Comando: {cmd}")
                print(f"     Motivo : {motivo}")
                num += 1
    else:
        print("Todos los comandos se ejecutaron exitosamente.")
    print("=" * 60 + "\n")


# =====================================================================
#  PROGRAMA PRINCIPAL
# =====================================================================
def main():
    robot = Robot()
    robot.conectar()

    try:
        # Menu interactivo para probar las distintas misiones del TP
        print("\n" + "=" * 60)
        print("          SELECCIONE LA MISION A EJECUTAR")
        print("=" * 60)
        print("  1 - MISION_BASICA")
        print("  2 - MISION_CUADRADO")
        print("  3 - MISION_CON_ERRORES (pruebas de validacion)")
        print("  4 - MISION_LARGA")
        print("  5 - MISION_ZIGZAG")
        print("  6 - MISION_PATRULLA")
        print("  7 - Ejecutar TODAS en secuencia")
        print("=" * 60)

        opcion = "1"
        try:
            entrada = input("Elija una opcion [1-7] (Enter para MISION_BASICA): ").strip()
            if entrada in ("1", "2", "3", "4", "5", "6", "7"):
                opcion = entrada
        except (EOFError, KeyboardInterrupt):
            opcion = "1"

        misiones_a_ejecutar = []
        if opcion == "1":
            misiones_a_ejecutar.append(("MISION_BASICA", MISION_BASICA))
        elif opcion == "2":
            misiones_a_ejecutar.append(("MISION_CUADRADO", MISION_CUADRADO))
        elif opcion == "3":
            misiones_a_ejecutar.append(("MISION_CON_ERRORES", MISION_CON_ERRORES))
        elif opcion == "4":
            misiones_a_ejecutar.append(("MISION_LARGA", MISION_LARGA))
        elif opcion == "5":
            misiones_a_ejecutar.append(("MISION_ZIGZAG", MISION_ZIGZAG))
        elif opcion == "6":
            misiones_a_ejecutar.append(("MISION_PATRULLA", MISION_PATRULLA))
        elif opcion == "7":
            misiones_a_ejecutar = [
                ("MISION_BASICA", MISION_BASICA),
                ("MISION_CUADRADO", MISION_CUADRADO),
                ("MISION_CON_ERRORES", MISION_CON_ERRORES),
                ("MISION_LARGA", MISION_LARGA),
                ("MISION_ZIGZAG", MISION_ZIGZAG),
                ("MISION_PATRULLA", MISION_PATRULLA),
            ]

        for nombre_mision, mision in misiones_a_ejecutar:
            print(f"\n>>> INICIANDO: {nombre_mision} <<<")
            historial = []
            ejecutar_mision(robot, mision, historial)
            generar_reporte(historial)

    finally:
        robot.detenerse()
        robot.desconectar()


if __name__ == "__main__":
    main()
