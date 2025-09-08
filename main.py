from math import pi, sqrt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

def build_oracle(n: int, marked: str) -> QuantumCircuit:
    print(f"[Oracle] Construyendo oráculo para marcar el estado |{marked}> con {n} qubits")
    qc = QuantumCircuit(n, name="Oracle")

    # Paso 1
    print(f"[Oracle] Aplicando compuertas X en qubits con '0' en el patrón objetivo")
    for i, b in enumerate(marked):
        if b == '0':
            qc.x(i)

    # Paso 2
    print("[Oracle] Implementando multi-controlled Z (con H-MCX-H)")
    controls = list(range(n-1))
    target = n-1
    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)

    # Paso 3
    print("[Oracle] Revirtiendo las X iniciales")
    for i, b in enumerate(marked):
        if b == '0':
            qc.x(i)

    print("[Oracle] Oráculo listo\n")
    return qc

def build_diffuser(n: int) -> QuantumCircuit:
    print(f"[Diffuser] Construyendo difusor para {n} qubits")
    qc = QuantumCircuit(n, name="Diffuser")

    print("[Diffuser] Aplicando H en todos los qubits")
    qc.h(range(n))
    print("[Diffuser] Aplicando X en todos los qubits")
    qc.x(range(n))

    print("[Diffuser] Implementando multi-controlled Z (con H-MCX-H)")
    controls = list(range(n-1))
    target = n-1
    qc.h(target)
    qc.mcx(controls, target)
    qc.h(target)

    print("[Diffuser] Revirtiendo X y aplicando H finales")
    qc.x(range(n))
    qc.h(range(n))

    print("[Diffuser] Difusor listo\n")
    return qc

def grover_search(n: int, marked: str, shots: int = 2000):
    N = 2**n
    r = int(round(pi/4 * sqrt(N)))
    print(f"[Grover] Iniciando búsqueda de |{marked}> con {n} qubits")
    print(f"[Grover] Número estimado de iteraciones: {r}\n")

    qc = QuantumCircuit(n, n)

    # Estado uniforme
    print("[Grover] Preparando estado inicial uniforme con Hadamards")
    qc.h(range(n))

    # Construcción de oráculo y difusor
    oracle = build_oracle(n, marked)
    diffuser = build_diffuser(n)

    # Iteraciones de Grover
    for i in range(r):
        print(f"[Grover] Iteración {i+1}/{r}: aplicando Oráculo y Difusor")
        qc.compose(oracle, qubits=range(n), inplace=True)
        qc.compose(diffuser, qubits=range(n), inplace=True)

    print("[Grover] Añadiendo mediciones en todos los qubits\n")
    qc.measure(range(n), range(n))

    # Simulación
    sim = AerSimulator()
    tqc = transpile(qc, sim, optimization_level=1)
    print("[Grover] Ejecutando simulación en AerSimulator...")
    job = sim.run(tqc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    print("[Grover] Simulación completada\n")

    return qc, counts, r

if __name__ == "__main__":
    n = 3
    objetivo = "111"
    qc, counts, r = grover_search(n, objetivo, shots=1024)

    print(f"Iteraciones de Grover usadas: {r}")
    print("Distribución de resultados (cuentas):")
    for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
        print(f"{k}: {v}")
