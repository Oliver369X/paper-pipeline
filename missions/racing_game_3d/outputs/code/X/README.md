# Carrera 3D (MVP) — paso 6/6: cierre

**Estado:** Pista oval, coche sobre línea central con límites al borde, meta visible (banda a cuadros + postes), cronómetro y tiempo al cruzar la meta. **Instrucciones en pantalla**, **reinicio con R**, aviso inferior hasta el primer clic, mensaje **«¡Listo!»** al enfocar, y el cronómetro **no avanza** mientras la pestaña está en segundo plano.

**Stack:** Three.js v0.160 vía `cdn.jsdelivr.net`, sin bundler ni npm obligatorio.

## Controles

| Acción | Teclas |
|--------|--------|
| Acelerar | **W**, **↑** |
| Frenar / marcha atrás | **S**, **↓** |
| Lateral (interior/exterior de curva) | **A** / **D**, **←** / **→** |
| Reiniciar carrera (tiempo y posición) | **R** |

Haz clic en la vista del juego para que el contenedor reciba foco y las teclas respondan de forma fiable.

## Requisitos

- Navegador con **WebGL** y **módulos ES** (`import`).
- Servidor HTTP local (los módulos ES no cargan bien con `file://`).

## Cómo ejecutarlo

Desde la carpeta de la misión (`missions/racing_game_3d/`):

```powershell
cd outputs/code/X
python -m http.server 8080
```

Abre: `http://localhost:8080`

Alternativa: `npx --yes serve .` en la misma carpeta.

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `index.html` | Import map de Three.js, HUD con tiempos e instrucciones, banners de foco / listo |
| `main.js` | Bootstrap: renderer, luces, coche, bucle de juego y HUD (entrada vía `driving-input.js`); helpers `recordFinishIfCrossed` / `updateHudTelemetry` para separar meta y texto del HUD del resto del `tick`; pausa si la pestaña está oculta; `resize`/`orientationchange` con try/catch; `webglcontextlost` / `webglcontextrestored` |
| `config.js` | Constantes agrupadas: `TRACK`, `SCENE`, `VIEW`, `RENDERER`, `LIGHTING`, `CAR_MESH`, `CHASE`, `GAME`, `CAR`, `MOTION`, `FINISH_VISUAL`, `FINISH_U`, `FINISH_CROSS_MAX_DELTA_U`, `NUM_EPS`, `TRACK_LEVELS`, `TRACK_PALETTE`, `HUD` |
| `curve-utils.js` | Helpers de curvas: tangente en plano XZ (`horizontalTangentAt`) compartida por pista y física |
| `driving-input.js` | Estado de teclas, listeners y reinicio (`R`); `resetDrivingKeys` para recuperación ante error |
| `error-overlay.js` | `showGameError` — mensaje a pantalla completa si falla WebGL o el circuito |
| `track.js` | Geometría de la pista, línea central, meta (banda + postes), `clampLateralToTrack` |
| `motion.js` | Integración del movimiento sobre la curva, orientación del coche y cámara chase |
| `timing.js` | Formato de tiempo y detección de cruce de meta |

`scene.userData.trackCenterline`, `scene.userData.track` y `scene.userData.finishU` están disponibles para extensiones.

## Flujo entre módulos

- **`main.js`**: crea renderer y escena, instala teclado (`driving-input.js`) y HUD, llama a `updateMotion` / `updateCamera` y pinta cada frame.
- **`config.js`**: único sitio recomendado para **números de gameplay y presentación** (pista, coche, niebla, cámara, meta, umbral de cruce en `timing.js`); evita duplicar constantes en otros archivos.
- **`curve-utils.js`**: tangente horizontal reutilizable para alinear coche y banda de meta sin duplicar lógica.
- **`driving-input.js`**: foco en `#app`, mapeo WASD/flechas/R, liberación de teclas en `blur` y pestaña oculta (`visibilitychange`), y función de limpieza de teclas tras errores de física.
- **`error-overlay.js`**: fallbacks de usuario visibles cuando no hay WebGL o la pista lanza.
- **`track.js`**: geometría de la pista, línea central, meta visual y `clampLateralToTrack` (límites del coche).
- **`motion.js`**: integración sobre la curva (`trackU`, `lateral`), orientación del mesh y cámara chase.
- **`timing.js`**: formato `m:ss.cs` y regla de cruce de meta en curva cerrada (`crossedFinishForward`).

## Convenciones de código

- **Constantes:** números de gameplay y presentación en `config.js`; evitar “constantes mágicas” en la lógica de `main.js`, `motion.js` y `track.js`.
- **Hot path:** en el bucle de juego no se crean objetos nuevos por frame en física y pista (vectores reutilizados, objetos de salida compartidos donde aplica).
- **Comentarios:** solo donde aclaran una regla no obvia (p. ej. wrap de `trackU`, umbral de cruce de meta); el nombre de funciones y módulos debe bastar en lo demás.

## Mantenimiento

- **Tunar velocidad o agarre:** edita `CAR` y, si hace falta, `TRACK` en `config.js`.
- **Cámara chase o altura del coche:** `CHASE` y `CAR_MESH.floorY`.
- **Mover la meta en la pista:** cambia `FINISH_U` (0–1 en la curva cerrada) y comprueba la banda en juego; debe coincidir con la lógica de `timing.js` (`FINISH_CROSS_MAX_DELTA_U` define qué salto en `u` se considera “media vuelta” y no cuenta como cruce hacia delante).
- **Tras cambiar geometría o física:** repite la lista de **Calidad y pruebas manuales** (sobre todo cruce de meta y bordes).

## Calidad y pruebas manuales

Comprueba en un navegador actual (Chrome, Firefox o Edge) con la consola abierta al menos en la primera carga.

1. Servir por HTTP, abrir la URL y comprobar **~60 FPS** y **sin errores** en la consola.
2. **Clic** en el canvas: desaparece el aviso inferior y aparece brevemente **«¡Listo!»**.
3. Completar una vuelta cruzando la meta en sentido de carrera: debe mostrarse el tiempo final.
4. Pulsar **R**: el cronómetro vuelve a cero y la posición del coche se reinicia (puedes volver a cronometrar).
5. Cambiar de pestaña unos segundos y volver: el tiempo mostrado **no** debe incluir ese intervalo.
6. **Redimensionar** la ventana: la imagen debe adaptarse sin deformarse de forma extraña y sin errores en consola.
7. **Teclado sin foco:** con el foco fuera del área de juego, **WASD** no debe mover el coche; al volver a enfocar `#app` (clic o **Tab** desde el enlace «Saltar al juego»), los controles deben responder.
8. **Rendimiento:** el bucle evita allocations en el hot path (vectores reutilizados en `motion.js` / `track.js`); el renderer usa `powerPreference: "high-performance"`, `stencil: false` (`RENDERER`), no hay sombras, la línea central usa menos muestras (`centerlineLinePoints`), los meshes estáticos de pista/meta tienen `matrixAutoUpdate = false` tras el primer `updateMatrix`, y al arrancar se llama `renderer.compile(scene, camera)` para amortiguar el coste de shaders en el primer frame.
9. **Teclado:** al cambiar de pestaña o minimizar la ventana, las teclas de dirección no deben quedar “pegadas” al volver (se liberan con `blur` / pestaña oculta en `driving-input.js`). Mantener **R** pulsado no debe repetir reinicios (se ignora `keydown` repetido).
10. **Robustez WebGL:** con la pestaña en segundo plano, el bucle no simula ni pinta (el cronómetro sigue compensado con `visibilitychange`). Tras **rotar** el dispositivo o redimensionar, la vista debe seguir correcta. Si el navegador pierde el contexto WebGL (poco habitual en uso normal), debe aparecer un mensaje claro y, si el contexto se restaura, la página puede recargarse sola.
11. **Legibilidad / mantenimiento:** al tocar el código, comprobar que los tunings siguen en `config.js`, que los imports entre módulos reflejan responsabilidades claras (tabla **Archivos** arriba) y que no se introducen allocations innecesarias en el bucle principal.
