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
      
