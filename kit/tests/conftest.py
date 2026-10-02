"""Permite ejecutar las pruebas desde la raíz del repositorio (pytest kit/tests) o desde kit/."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
