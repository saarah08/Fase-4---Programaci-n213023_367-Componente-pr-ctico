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

  
