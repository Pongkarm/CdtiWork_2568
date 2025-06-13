from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# สร้างวงจรควอนตัม 1 qubit, 1 classical bit
qc = QuantumCircuit(1, 1)

# ใส่ Hadamard Gate เพื่อสร้าง Superposition
qc.h(0)

# วัด qubit ใส่ลงใน classical bit
qc.measure(0, 0)

# จำลองผลลัพธ์
simulator = Aer.get_backend('qasm_simulator')
job = execute(qc, simulator, shots=1000)
result = job.result()
counts = result.get_counts()

# แสดงผล
print("ผลลัพธ์จากการวัด:", counts)
plot_histogram(counts)
plt.show()
