
# ---------------------------------------------------------------------------
# CONSIGNA 1: datos de las columnas

# diccionario con {nombredelacolumna: {"tipo": str, "completitud": float (0-100)}}
COLUMNAS = {
    "PONDERA":    {"tipo": "int", "completitud": 100.0},
    "ESTADO":     {"tipo": "int", "completitud": 99.9},
    "CAT_OCUP":   {"tipo": "int", "completitud": 58.3},
    "EDAD":       {"tipo": "int", "completitud": 100.0},
    "REGION":     {"tipo": "int", "completitud": 100.0},
    "AGLOMERADO": {"tipo": "int", "completitud": 100.0},
    "MAS_500":    {"tipo": "str", "completitud": 97.5},
    "ANO4":       {"tipo": "int", "completitud": 100.0},
    "TRIMESTRE":  {"tipo": "int", "completitud": 100.0},
    "ITF":        {"tipo": "int", "completitud": 78.5},
    "GDECCFR":    {"tipo": "int", "completitud": 74.2},
    "CH04":       {"tipo": "int", "completitud": 95.0},
}

# ---------------------------------------------------------------------------
# CONSIGNA 2: roles
# diccionario {rol: configuración}. Claves de la configuración:
#   "columnas"        : list  -> columnas de interés
#   "criterio"        : str   -> "nombre" | "completitud"
#   "orden"           : str   -> "A" (ascendente) | "B" (descendente)
#   "min_completitud" : float -> OPCIONAL; si no está, no se filtra
ROLES = {
    "docente": {
        "columnas": ["EDAD", "ESTADO", "CAT_OCUP", "ANO4", "TRIMESTRE"],
        "criterio": "nombre",
        "orden": "A",
    },
    "investigador": {
        "columnas": ["PONDERA", "ESTADO", "CAT_OCUP", "EDAD", "REGION",
                     "AGLOMERADO", "ITF", "GDECCFR", "ANO4","CH04"],
        "criterio": "completitud",
        "orden": "B",
        "min_completitud": 70,
    },
    "analista": {
        "columnas": ["ITF", "GDECCFR", "MAS_500", "REGION", "AGLOMERADO",
                     "PONDERA"],
        "criterio": "completitud",
        "orden": "A",
        "min_completitud": 90,
    },
}

# Valores por defecto (informe sin rol: todas las columnas, por completitud
# de mayor a menor) y valores permitidos.
CRITERIO_DEFECTO = "completitud"
ORDEN_DEFECTO = "B"
CRITERIOS_VALIDOS = ("nombre", "completitud")
ORDENES_VALIDOS = ("A", "B")


# ---------------------------------------------------------------------------
# CONSIGNA 3 y 4: seleccion, orden y generación
def seleccionar_columnas(nombres, columnas, minimo=None):
    """Devuelve los nombres de columnas que existen y superan el umbral.

    Args:
        nombres (list[str]): nombres de columnas candidatas.
        columnas (dict): datos de las columnas (ver COLUMNAS).
        minimo (float | None): completitud mínima (>=). Si es None no se
            filtra por completitud.

    Returns:
        list[str]: nombres válidos, en el mismo orden en que llegaron.
    """
    inexistentes = [n for n in nombres if n not in columnas]
    if inexistentes:
        print(f"Aviso: columnas inexistentes ignoradas: {inexistentes}")

    validas = filter(lambda n: n in columnas, nombres)
    if minimo is not None:
        validas = filter(lambda n: columnas[n]["completitud"] >= minimo,
                         validas)
    return list(validas)


def ordenar_columnas(nombres, columnas, criterio=CRITERIO_DEFECTO,
                     orden=ORDEN_DEFECTO):
    """Ordena nombres de columnas por nombre o por completitud.

    Si el criterio o el orden no son válidos no falla: avisa y usa los
    valores por defecto (completitud, descendente).

    Args:
        nombres (list[str]): columnas a ordenar (deben existir en columnas).
        columnas (dict): datos de las columnas.
        criterio (str): "nombre" o "completitud".
        orden (str): "A" ascendente o "B" descendente.

    Returns:
        list[str]: nombres ordenados.
    """
    if criterio not in CRITERIOS_VALIDOS:
        print(f"Aviso: criterio '{criterio}' inválido. "
              f"Se usa '{CRITERIO_DEFECTO}'.")
        criterio = CRITERIO_DEFECTO
    if orden not in ORDENES_VALIDOS:
        print(f"Aviso: orden '{orden}' inválido. Se usa '{ORDEN_DEFECTO}'.")
        orden = ORDEN_DEFECTO

    if criterio == "nombre":
        clave = lambda n: n
    else:  # completitud; el nombre desempata para que el resultado sea estable
        clave = lambda n: (columnas[n]["completitud"], n)

    return sorted(nombres, key=clave, reverse=(orden == "B"))


def generar_informe(rol=None, columnas=COLUMNAS, roles=ROLES):
    """Genera el informe de columnas para un rol.

    Si rol es None se informan todas las columnas ordenadas por completitud
    de forma descendente. Si el rol tiene "min_completitud" solo se incluyen
    las columnas con completitud mayor o igual a ese valor.

    Args:
        rol (str | None): nombre del rol (clave de roles) o None.
        columnas (dict): datos de las columnas.
        roles (dict): configuración de roles.

    Returns:
        list[tuple]: tuplas (nombre, tipo, completitud) ya ordenadas.

    Raises:
        ValueError: si el rol pedido no existe en roles.
    """
    if rol is None:
        nombres = list(columnas)
        criterio, orden = CRITERIO_DEFECTO, ORDEN_DEFECTO
    elif rol in roles:
        config = roles[rol]
        nombres = seleccionar_columnas(config["columnas"], columnas,
                                       config.get("min_completitud"))
        criterio = config.get("criterio", CRITERIO_DEFECTO)
        orden = config.get("orden", ORDEN_DEFECTO)
    else:
        raise ValueError(f"Rol '{rol}' inexistente. "
                         f"Roles disponibles: {list(roles)}")

    ordenados = ordenar_columnas(nombres, columnas, criterio, orden)
    return list(map(lambda n: (n, columnas[n]["tipo"],
                               columnas[n]["completitud"]), ordenados))


def mostrar_informe(informe, titulo="Informe"):
    """Imprime por pantalla un informe generado por generar_informe.

    Args:
        informe (list[tuple]): tuplas (nombre, tipo, completitud).
        titulo (str): encabezado a mostrar.
    """
    print(f"\n=== {titulo} ===")
    print(f"{'COLUMNA':<12}{'TIPO':<8}{'COMPLETITUD':>12}")
    for nombre, tipo, completitud in informe:
        print(f"{nombre:<12}{tipo:<8}{completitud:>11.1f}%")
    if not informe:
        print("(sin columnas que cumplan el criterio)")


def informe_por_rol(rol=None):
    """Genera e imprime el informe de un rol (o el general si rol es None).

    Args:
        rol (str | None): nombre del rol o None.
    """
    titulo = f"Rol: {rol}" if rol else "Todas las columnas (sin rol)"
    mostrar_informe(generar_informe(rol), titulo)


if __name__ == "__main__":
    informe_por_rol()
    for nombre_rol in ROLES:
        informe_por_rol(nombre_rol)
