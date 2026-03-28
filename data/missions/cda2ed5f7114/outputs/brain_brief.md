<!-- brain_brief ts=2026-03-27T20:34:07.638686+00:00 -->

# Brief Doctoral: Curvatura de Pérdida y la Transición Memorización-Razonamiento

Este proyecto se centra en la réplica y extensión del trabajo de **Merullo et al. (2025)**, *“From Memorization to Reasoning in the Spectrum of Loss Curvature”*. La tesis central es que el espacio de parámetros de los Transformers no es homogéneo: la **memorización** (overfitting de datos específicos) reside en direcciones de alta curvatura (sharp minima), mientras que el **razonamiento** (generalización lógica) se manifiesta en direcciones de baja curvatura (flat minima).

### Fase A: Réplica de Observación (Fidelidad Estricta)
El objetivo primario es implementar una métrica de curvatura basada en la sensibilidad de la pérdida frente a perturbaciones locales (e.g., aproximación del Hessiano o norma del gradiente en presencia de ruido). Se utilizarán pares de datos: uno diseñado para ser memorizado (datos sintéticos aleatorios) y otro que requiera una regla lógica (aritmética simple o inducción).

### Fase B: Extensión y Hipótesis (Novedad)
Investigaremos si es posible 'forzar' el razonamiento penalizando explícitamente las direcciones de alta curvatura durante un proceso de fine-tuning o mediante técnicas de **Sharpness-Aware Minimization (SAM)** aplicadas selectivamente a tokens de razonamiento.

### Riesgos y Límites
1. **Cómputo:** Calcular el espectro completo del Hessiano es prohibitivo; usaremos métodos iterativos (Lanczos) o proxies de perturbación.
2. **Escala:** Los fenómenos de curvatura pueden variar entre modelos 'tiny' y modelos de gran escala (Llama-3), lo que podría afectar la replicabilidad de los resultados de Merullo.
