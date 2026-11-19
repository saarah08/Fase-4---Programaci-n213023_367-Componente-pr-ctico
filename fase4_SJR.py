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
      
