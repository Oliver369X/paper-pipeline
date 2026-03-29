<!-- brain_brief ts=2026-03-29T06:09:31.008313+00:00 -->

# Plan de Investigación: Réplica de arXiv:2510.24256

Este brief detalla la estrategia para replicar el trabajo **“From Memorization to Reasoning in the Spectrum of Loss Curvature”** (Merullo et al., 2025). La investigación se centra en la relación entre la geometría del loss landscape (curvatura) y la naturaleza de la información almacenada en los pesos del modelo (memorización vs. razonamiento).

## 1. Marco Teórico y SOTA
El paper propone que los puntos de datos memorizados (recitación de memoria) residen en regiones del loss landscape con una curvatura más aguda (sharpness), mientras que las capacidades de razonamiento generalizables se asocian con regiones más planas. Mediante la descomposición del espectro de curvatura (probablemente vía traza del Hessiano o autovalores principales), es posible identificar y editar componentes específicos.

## 2. Fase A: Réplica Estricta
- **Identificación:** Implementar un estimador de la curvatura del loss respecto a los parámetros para identificar componentes de 'alta curvatura'.
- **Edición de Pesos:** Realizar la ablación o edición de estos componentes sin entrenamiento adicional (training-free weight editing).
- **Evaluación de Recitación:** Medir la caída en la recitación verbatim de datos de entrenamiento memorizados.
- **Control de Daños:** Monitorear la Perplexity y el desempeño en tareas de recuperación de hechos (fact retrieval) y aritmética, donde el paper original reporta una degradación selectiva.

## 3. Riesgos y Límites
- **Costo Computacional:** La estimación exacta del Hessiano es prohibitiva; la réplica dependerá de la fidelidad de las aproximaciones usadas (p. ej., Hutchinson’s estimator).
- **Sensibilidad al Modelo:** Los hallazgos podrían variar significativamente entre arquitecturas Transformer (Encoder-only vs Decoder-only).
- **Validación Humana:** La inspección de los outputs en el **Cockpit** será crítica para verificar que la reducción en memorización no es simplemente una degradación generalizada del modelo.

## 4. Trazabilidad
Se utilizará el `experiment_runner` para registrar cada corrida, asegurando que los hiperparámetros de la descomposición y las semillas aleatorias queden persistidos en `outputs/metrics.json` para su posterior análisis en el hipervisor.
