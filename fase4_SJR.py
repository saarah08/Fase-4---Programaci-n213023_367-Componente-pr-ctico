#Nombre: Sara J. Ruiz
#Grupo: 213023_367
#Codigo Fuente: Autoria Propia
#Ejercicio 1: Sistema Integral de Gestión de Clientes, Servicios y Reservas
import logging
import re
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import messagebox, ttk
from tkinter.scrolledtext import ScrolledText
logging.basicConfig(handlers=[logging.FileHandler("eventos.log", encoding="utf-8")], level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

class ErrorFJ(Exception): pass
class DatoInvalidoError(ErrorFJ): pass
class ServicioNoDisponibleError(ErrorFJ): pass
class OperacionNoPermitidaError(ErrorFJ): pass
class CalculoError(ErrorFJ): pass
class ReservaError(ErrorFJ): pass

class Entidad(ABC):
    _total = 0

    def __init__(self):
        Entidad._total += 1
        self._id = Entidad._total

    id = property(lambda self: self._id)

    @abstractmethod
    def describir(self): ...

class Cliente(Entidad):
    def __init__(self, nombre, correo, telefono):
        if not nombre or not nombre.replace(" ", "").isalpha():
            raise DatoInvalidoError(f"Nombre inválido o vacío: {nombre!r}")
        if not re.fullmatch(r"[\w.\-]+@[\w\-]+\.[\w.\-]+", correo or ""):
            raise DatoInvalidoError(f"Correo inválido: {correo!r}")
        if not (telefono or "").isdigit() or not 7 <= len(telefono) <= 10:
            raise DatoInvalidoError(f"Teléfono inválido: {telefono!r}")
        super().__init__()
        self._nombre, self._correo, self._telefono = nombre.strip(), correo, telefono

    nombre = property(lambda self: self._nombre)
    correo = property(lambda self: self._correo)
    telefono = property(lambda self: self._telefono)

    def describir(self):
        return f"Cliente #{self.id}: {self.nombre} | {self.correo} | {self.telefono}"
      class Servicio(Entidad):
    UNIDAD, MAXIMO = "horas", 1

    def __init__(self, nombre, tarifa, detalle, disponible=True):
        if not nombre or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        if isinstance(tarifa, bool) or not isinstance(tarifa, (int, float)) or tarifa <= 0:
            raise DatoInvalidoError(f"Tarifa inválida: {tarifa!r}")
        self.validar_detalle(detalle)
        super().__init__()
        self._nombre, self._tarifa, self._detalle, self.disponible = nombre.strip(), tarifa, detalle, disponible

    nombre = property(lambda self: self._nombre)
    tarifa = property(lambda self: self._tarifa)

    @abstractmethod
    def validar_detalle(self, detalle): ...
      
    @abstractmethod
    def costo(self, duracion): ...

    def validar_duracion(self, d):
        if isinstance(d, bool) or not isinstance(d, (int, float)) or not 1 <= d <= self.MAXIMO:
            raise DatoInvalidoError(f"Duración inválida ({d!r}): debe estar entre 1 y {self.MAXIMO} {self.UNIDAD}.")

    def total(self, duracion, impuesto=0.0, descuento=0.0):
        self.validar_duracion(duracion)
        if not (0 <= impuesto <= 1 and 0 <= descuento <= 1):
            raise CalculoError(f"Impuesto ({impuesto}) y descuento ({descuento}) deben estar entre 0 y 1.")
        return round(self.costo(duracion) * (1 - descuento) * (1 + impuesto), 2)

class ReservaSala(Servicio):
    UNIDAD, MAXIMO = "horas", 12

    def validar_detalle(self, detalle):
        if not str(detalle).isdigit() or int(detalle) <= 0:
            raise DatoInvalidoError(f"Capacidad inválida: {detalle!r}")

    def costo(self, duracion):
        return self.tarifa * duracion

    def describir(self):
        return f"Sala '{self.nombre}' (capacidad {self._detalle}) - ${self.tarifa:,.0f}/hora"

class AlquilerEquipo(Servicio):
    UNIDAD, MAXIMO = "días", 30

    def validar_detalle(self, detalle):
        if not detalle or not str(detalle).strip():
            raise DatoInvalidoError("Falta el tipo de equipo.")

    def costo(self, duracion):
        return self.tarifa * duracion + 10000

    def describir(self):
        return f"Equipo '{self.nombre}' ({self._detalle}) - ${self.tarifa:,.0f}/día + $10,000 de transporte"

class Asesoria(Servicio):
    UNIDAD, MAXIMO = "horas", 8

    def validar_detalle(self, detalle):
        if detalle not in ("junior", "senior"):
            raise DatoInvalidoError(f"Nivel inválido: {detalle!r} (use junior o senior)")

    def costo(self, duracion):
        return self.tarifa * duracion * (1.5 if self._detalle == "senior" else 1)

    def describir(self):
        return f"Asesoría '{self.nombre}' ({self._detalle}) - ${self.tarifa:,.0f}/hora"

class Reserva(Entidad):
    def __init__(self, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaError("La reserva necesita un Cliente y un Servicio válidos.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"'{servicio.nombre}' no está disponible.")
        servicio.validar_duracion(duracion)
        super().__init__()
        self._cliente, self._servicio, self._duracion = cliente, servicio, duracion
        self.estado, self.costo = "PENDIENTE", None

    cliente = property(lambda self: self._cliente)
    servicio = property(lambda self: self._servicio)
    duracion = property(lambda self: self._duracion)

    def confirmar(self):
        if self.estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"Reserva #{self.id}: no se puede confirmar, está {self.estado}.")
        self.estado = "CONFIRMADA"

    def cancelar(self):
        if self.estado in ("CANCELADA", "PROCESADA"):
            raise OperacionNoPermitidaError(f"Reserva #{self.id}: no se puede cancelar, está {self.estado}.")
        self.estado = "CANCELADA"

    def procesar(self, impuesto=0.19, descuento=0.0):
        if self.estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(f"Reserva #{self.id}: solo se procesan las CONFIRMADAS (está {self.estado}).")
        try:
            costo = self._servicio.total(self._duracion, impuesto, descuento)
        except ErrorFJ as origen:
            raise ReservaError(f"No se pudo procesar la reserva #{self.id}.") from origen
        else:
            self.costo, self.estado = costo, "PROCESADA"
            return costo
        finally:
            logging.info(f"Intento de procesar la reserva #{self.id} finalizado.")

    def describir(self):
        costo = f"${self.costo:,.2f}" if self.costo is not None else "sin calcular"
        return f"Reserva #{self.id} | {self.cliente.nombre} | {self._servicio.nombre} | {self._duracion} | {self.estado} | {costo}"

def intentar(num, desc, funcion, salida):
    salida(f"[{num}] {desc}")
    try:
        resultado = funcion()
    except ErrorFJ as e:
        causa = f" (causa: {e.__cause__})" if e.__cause__ else ""
        salida(f"    ERROR controlado: {e}{causa}")
        logging.error(f"Operación {num} falló: {e}{causa}")
    except Exception as e:
        salida(f"    ERROR inesperado: {type(e).__name__}: {e}")
        logging.error(f"Operación {num} error inesperado: {type(e).__name__}: {e}")
    else:
        salida(f"    OK: {resultado}")
        logging.info(f"Operación {num} exitosa: {resultado}")
    finally:
        logging.info(f"Operación {num} finalizada.")

def simular(salida):
    c, s, r = [], [], []

    def add(lista, obj):
        lista.append(obj)
        return obj.describir()

operaciones = [
        ("Cliente válido (Elain Archeron)", lambda: add(c, Cliente("Elain Archeron", "flowergirl@velaris.com", "3001234567"))),
        ("Cliente con correo inválido", lambda: add(c, Cliente("Dorian Havilliard", "malo@correo.com", "3109876543"))),
        ("Cliente válido (Manon Blackbeak)", lambda: add(c, Cliente("Manon Blackbeak", "whitedemonwitch@kingofashes.com", "3205551234"))),
        ("Cliente sin nombre", lambda: add(c, Cliente(None, "x@correo.com", "3001112233"))),
        ("Sala válida", lambda: add(s, ReservaSala("Sala Andes", 50000, 10))),
        ("Sala con tarifa negativa", lambda: add(s, ReservaSala("Sala Rota", -100, 5))),
        ("Equipo válido", lambda: add(s, AlquilerEquipo("Portátil Pro", 30000, "Portátil"))),
        ("Asesoría con nivel inválido", lambda: add(s, Asesoria("Asesoría X", 60000, "experto"))),
        ("Asesoría senior válida", lambda: add(s, Asesoria("Asesoría Cloud", 80000, "senior"))),
        ("Reserva exitosa: Elain reserva la sala 3 horas", lambda: add(r, Reserva(c[0], s[0], 3))),
        ("Reserva con duración 0", lambda: add(r, Reserva(c[0], s[0], 0))),
        ("Reserva de servicio no disponible", lambda: add(r, Reserva(c[1], AlquilerEquipo("Proyector", 40000, "Proyector", False), 2))),
        ("Confirmar y procesar (impuesto 19%, descuento 10%)",
         lambda: f"costo ${(r[0].confirmar(), r[0].procesar(0.19, 0.10))[1]:,.2f}"),
        ("Cancelar una reserva ya procesada", lambda: r[0].cancelar()),
        ("Procesar con descuento de 150% (error encadenado)",
         lambda: (r.append(Reserva(c[1], s[2], 2)), r[1].confirmar(), r[1].procesar(0.19, 1.5))),
        ("Error inesperado de Python (1/0)", lambda: 1 / 0),
    ]

logging.info("===== INICIO DE LA SIMULACIÓN =====")
    for i, (desc, f) in enumerate(operaciones, 1):
        intentar(i, desc, f, salida)
    salida(f"\nResumen: {len(c)} clientes, {len(s)} servicios, {len(r)} reservas. El programa NO se cayó.")
    logging.info("===== FIN DE LA SIMULACIÓN =====")

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Software FJ - Gestión de Clientes, Servicios y Reservas")
        self.root.geometry("980x600")
        self.c, self.s, self.r, self.n = [], [], [], 0
        self.estado = tk.StringVar(value="Listo.")
        self.barra = ttk.Label(self.root, textvariable=self.estado, anchor="w", padding=4)
        self.barra.pack(side="bottom", fill="x")
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=8, pady=8)
        self.armar_clientes()
        self.armar_servicios()
        self.armar_reservas()
        self.armar_simulacion()
        self.armar_log()
        self.refrescar()
  
    def pestana(self, nombre):
        marco = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(marco, text=nombre)
        return marco

    def campos(self, marco, lista):
        widgets = []
        for i, (texto, valores) in enumerate(lista):
            ttk.Label(marco, text=texto).grid(row=i, column=0, sticky="w", padx=4, pady=3)
            if valores is None:
                w = ttk.Entry(marco, width=36)
            else:
                w = ttk.Combobox(marco, values=valores, state="readonly", width=33)
            w.grid(row=i, column=1, sticky="w", padx=4, pady=3)
            widgets.append(w)
        return widgets
  
def tabla(self, marco, columnas, anchos):
        contenedor = ttk.Frame(marco)
        contenedor.pack(fill="both", expand=True, pady=(10, 0))
        arbol = ttk.Treeview(contenedor, columns=columnas, show="headings", height=9)
        for columna, ancho in zip(columnas, anchos):
            arbol.heading(columna, text=columna.capitalize())
            arbol.column(columna, width=ancho, anchor="w")
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=arbol.yview)
        arbol.configure(yscrollcommand=barra.set)
        arbol.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return arbol

    def armar_clientes(self):
        marco = self.pestana("Clientes")
        form = ttk.LabelFrame(marco, text="Nuevo cliente", padding=8)
        form.pack(fill="x")
        self.f_cli = self.campos(form, [("Nombre", None), ("Correo", None), ("Teléfono", None)])
        ttk.Button(form, text="Registrar cliente", command=self.nuevo_cliente).grid(row=3, column=1, sticky="w", pady=4)
        self.t_cli = self.tabla(marco, ("id", "nombre", "correo", "telefono"), (60, 220, 280, 140))

    def armar_servicios(self):
        marco = self.pestana("Servicios")
        form = ttk.LabelFrame(marco, text="Nuevo servicio", padding=8)
        form.pack(fill="x")
        self.f_srv = self.campos(form, [("Tipo", ["Sala", "Equipo", "Asesoría"]), ("Nombre", None),
                                        ("Tarifa (por hora)", None), ("Capacidad", None)])
        self.f_srv[0].current(0)
        self.f_srv[0].bind("<<ComboboxSelected>>", self.cambiar_tipo)
        self.disp = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Disponible", variable=self.disp).grid(row=4, column=1, sticky="w", padx=4)
        ttk.Button(form, text="Crear servicio", command=self.nuevo_servicio).grid(row=5, column=1, sticky="w", pady=4)
        self.t_srv = self.tabla(marco, ("id", "tipo", "descripcion", "disponible"), (60, 160, 580, 100))

    def cambiar_tipo(self, _evento=None):
        textos = {"Sala": "Capacidad", "Equipo": "Tipo de equipo", "Asesoría": "Nivel (junior / senior)"}
        form = self.f_srv[3].master
        for w in form.grid_slaves(row=3, column=0):
            w.configure(text=textos.get(self.f_srv[0].get(), "Detalle"))

    def armar_reservas(self):
        marco = self.pestana("Reservas")
        form = ttk.LabelFrame(marco, text="Nueva reserva", padding=8)
        form.pack(fill="x")
        self.f_res = self.campos(form, [("Cliente", []), ("Servicio", []), ("Duración (horas)", None)])
        ttk.Button(form, text="Crear reserva", command=self.nueva_reserva).grid(row=3, column=1, sticky="w", pady=4)
        acciones = ttk.LabelFrame(marco, text="Acciones sobre la reserva seleccionada", padding=8)
        acciones.pack(fill="x", pady=(8, 0))
        ttk.Label(acciones, text="Impuesto (0 a 1)").grid(row=0, column=0, padx=4)
        self.impuesto = ttk.Entry(acciones, width=7)
        self.impuesto.insert(0, "0.19")
        self.impuesto.grid(row=0, column=1, padx=4)
        ttk.Label(acciones, text="Descuento (0 a 1)").grid(row=0, column=2, padx=4)
        self.descuento = ttk.Entry(acciones, width=7)
        self.descuento.insert(0, "0")
        self.descuento.grid(row=0, column=3, padx=4)
        for i, (texto, comando) in enumerate([("Confirmar", self.confirmar), ("Procesar", self.procesar),
                                              ("Cancelar", self.cancelar)]):
            ttk.Button(acciones, text=texto, command=comando).grid(row=0, column=4 + i, padx=6)
        self.t_res = self.tabla(marco, ("id", "cliente", "servicio", "duracion", "estado", "costo"),
                                (50, 200, 240, 90, 110, 140))

  def armar_simulacion(self):
        marco = self.pestana("Simulación")
        ttk.Button(marco, text="Ejecutar simulación de 16 operaciones", command=self.correr_simulacion).pack(anchor="w")
        self.txt_sim = ScrolledText(marco, wrap="word", font=("Consolas", 10))
        self.txt_sim.pack(fill="both", expand=True, pady=(10, 0))

    def armar_log(self):
        marco = self.pestana("Registro (logs)")
        ttk.Button(marco, text="Actualizar", command=self.cargar_log).pack(anchor="w")
        self.txt_log = ScrolledText(marco, wrap="none", font=("Consolas", 9))
        self.txt_log.pack(fill="both", expand=True, pady=(10, 0))

    def correr_simulacion(self):
        self.txt_sim.delete("1.0", "end")

        def salida(texto):
            self.txt_sim.insert("end", texto + "\n")
            self.txt_sim.see("end")
            self.root.update_idletasks()

        simular(salida)
        self.cargar_log()

    def cargar_log(self):
        try:
            with open("eventos.log", encoding="utf-8") as archivo:
                contenido = archivo.read()
        except OSError as error:
            contenido = f"No se pudo leer el archivo de logs: {error}"
        self.txt_log.delete("1.0", "end")
        self.txt_log.insert("end", contenido)
        self.txt_log.see("end")

    def accion(self, desc, funcion):
        self.n += 1
        previa = self.t_res.selection()
        lineas = []
        intentar(self.n, desc, funcion, lineas.append)
        texto = " ".join(linea.strip() for linea in lineas[1:])
        error = texto.startswith("ERROR")
        self.estado.set(texto)
        self.barra.configure(foreground="red" if error else "green")
        self.refrescar()
        if previa:
            self.t_res.selection_set(previa)
        if error:
            messagebox.showerror(texto.split(":", 1)[0].capitalize(), texto.split(": ", 1)[1])
          
