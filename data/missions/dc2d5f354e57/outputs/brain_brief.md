<!-- brain_brief ts=2026-03-27T16:26:41.018119+00:00 -->

# Brief Doctoral: Mitigación de Memorización en LLMs (BalancedSubnet)

## 1. Contexto Académico
El paper **2410.02159** (Sakarvadia et al., 2024) aborda un problema crítico: la **memorización no deseada** de datos de entrenamiento. La técnica propuesta, **BalancedSubnet**, utiliza *machine unlearning* para identificar y ajustar sub-redes responsables de esta memorización sin causar una degradación catastrófica del rendimiento general.

## 2. El Método: BalancedSubnet
Se basa en el descubrimiento de sub-redes (estilo Ramanujan) con una función de pérdida que penaliza la modificación de pesos esenciales para tareas generales. Esto permite un 'borrado' selectivo de información sensible o repetitiva.

## 3. Hipótesis Estructuradas en la Misión
- **H_SCALABILITY**: Evalúa si la polisemia neuronal en modelos grandes (Pythia/Llama) diluye la efectividad de las máscaras binarias comparado con modelos pequeños.
- **H_EFFICIENCY**: Propone que BalancedSubnet supera a la regularización tradicional (Weight Decay) en un 40% en reducción de memorización.
- **H_SATURATION**: Investiga el límite de 'Data Poisoning' tras el cual el método ya no puede aislar la sub-red de memorización.

## 4. Estrategia de Replicación
Utilizaremos `sshleifer/tiny-gpt2` sobre `wikitext-2-raw-v1` inyectando secuencias sintéticas para calcular el **Memorization Score** (prefix matching) vs. **Perplejidad**.
