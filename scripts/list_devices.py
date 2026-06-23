#!/usr/bin/env python3
from __future__ import annotations

from quantum_compare.backends.ibm_superconducting import IBMBackend
from quantum_compare.backends.quantinuum_trapped_ion import QuantinuumBackend
from quantum_compare.backends.ideal import IdealBackend


if __name__ == "__main__":
    for backend in [IdealBackend(), IBMBackend(), QuantinuumBackend()]:
        print(backend.name, backend.provider, backend.architecture, backend.is_available())
