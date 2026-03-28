"""Prompts en español para el bucle de carreras 3D (Composer / Cursor CLI)."""

from __future__ import annotations

# Raíz del juego relativa al cwd de la misión (missions/.../outputs/code/X)
GAME_REL = "outputs/code/X"


def _base_rules() -> str:
    return f"""Reglas fijas:
- Todo el código del juego va bajo `{GAME_REL}/` (creá la carpeta si no existe).
- Usá Three.js por CDN (importmap o script tag) salvo que ya exista otro patrón en el repo.
- No pongas secretos ni API keys en los archivos.
- Respondé al final con un resumen breve de archivos tocados.
"""


def round_prompts() -> list[tuple[str, str]]:
    """Títulos cortos + cuerpo del prompt para cada ronda."""

    b = _base_rules()
    return [
        (
            "1/6 — Esqueleto Three.js",
            f"""{b}
Tarea: creá `index.html` y `main.js` (o un solo HTML inline) en `{GAME_REL}/` con:
- escena, cámara en perspectiva, renderer WebGL, resize, loop `requestAnimationFrame`;
- iluminación básica (ambient + directional) y fondo oscuro o niebla suave;
- un plano como suelo y un cubo de prueba para ver que renderiza.
Incluí `README.md` en `{GAME_REL}/` con cómo abrir el juego (servidor estático o file:// si aplica).
""",
        ),
        (
            "2/6 — Pista",
            f"""{b}
Tarea: añadí una "pista" simple: plano alargado o varios segmentos, bordes visibles (líneas o muros bajos) para delimitar carril.
La cámara debe seguir al jugador o quedar detrás (tercera persona simple); si aún no hay coche, usá el cubo como placeholder.
""",
        ),
        (
            "3/6 — Coche y controles",
            f"""{b}
Tarea: reemplazá el cubo de prueba por un "coche" (mesh compuesto o caja estilizada). Controles teclado: acelerar/frenar/girar (WASD o flechas).
El coche debe rotar y desplazarse en el plano de la pista (eje horizontal; ignorá física realista al inicio).
""",
        ),
        (
            "4/6 — Movimiento y límites",
            f"""{b}
Tarea: limitá el movimiento para que el coche no atraviese los bordes de la pista (restricción simple por distancia o colisión básica AABB).
Ajustá velocidad máxima y fricción para que sea jugable.
""",
        ),
        (
            "5/6 — Meta y cronómetro",
            f"""{b}
Tarea: línea de salida/meta (planos o marcadores), cronómetro en pantalla (HTML overlay o CSS2DRenderer si querés).
Al cruzar la meta, mostrá tiempo de vuelta o mensaje de victoria.
""",
        ),
        (
            "6/6 — Cierre MVP",
            f"""{b}
Tarea: pulí UX: instrucciones en pantalla, reinicio (tecla R), mensaje de "listo" si falta algo menor.
Actualizá `README.md` con controles, requisitos y cómo ejecutar. Sin dependencias npm obligatorias.
""",
        ),
    ]


def improvement_loop_prompt(*, iteration: int, max_iter: int) -> tuple[str, str]:
    """Una vuelta del bucle de refinamiento (calidad, buenas prácticas)."""

    b = _base_rules()
    phase = (iteration - 1) % 6
    focus = [
        "Arquitectura: separar responsabilidades en módulos/funciones claras; eliminar duplicación; nombres expresivos.",
        "Rendimiento Three.js: evitar allocations en el game loop; usar `BufferGeometry`/`dispose()` donde corresponda; limitar luces/sombras si sobran.",
        "UX y accesibilidad: HUD legible, contraste, instrucciones visibles; manejo de teclado robusto (`keydown`/`keyup`).",
        "Robustez: resize/orientación; `visibilitychange` para pausar; manejo básico de WebGL context lost si aplica.",
        "Legibilidad y mantenimiento: comentarios solo donde aporten; README con sección 'Calidad y pruebas manuales'.",
        "Pulido final: consistencia de estilo, constantes mágicas nombradas, pequeñas optimizaciones sin romper gameplay.",
    ][phase]

    title = f"Mejora continua ({iteration}/{max_iter})"
    body = f"""{b}
Bucle de refinamiento — iteración **{iteration}** de **{max_iter}** (objetivo: MVP con alto estándar de calidad).

Enfoque prioritario esta vuelta:
{focus}

Además (siempre):
- Revisá todo `{GAME_REL}/` (HTML, JS, CSS, README) y aplicá mejoras concretas alineadas a buenas prácticas web y Three.js.
- No añadas dependencias npm obligatorias; mantené el juego servible con servidor estático.
- Al final del resumen, indicá una línea exacta: `ESTADO: LISTO` si considerás que el proyecto cumple estándares de calidad para entregar; o `ESTADO: CONTINÚA` y listá brevemente qué falta.
"""
    return title, body
