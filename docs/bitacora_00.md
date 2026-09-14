### [2026-09-09] Configuración del entorno de trabajo

**Qué se hizo:** Se definió la arquitectura de trabajo del proyecto
(cuatro carriles: aprendizaje, código, lectura, redacción) y se instaló
y verificó la cadena de documentación LaTeX + Zotero + git.

**Decisiones y justificación:**
- LaTeX local en VS Code en lugar de Overleaf → el plan gratuito de
  Overleaf no admite 3 colaboradores; git además aporta historial y ramas.
- BibLaTeX + biber en lugar de BibTeX → mejor manejo de UTF-8 y DOIs.
- Better BibLaTeX con auto-exportación (Keep updated) → el .bib del
  repositorio se mantiene solo; se prohíbe editarlo a mano.
- lmodern + fontenc T1, sin inputenc → evita fuentes bitmap Type 3,
  que algunos repositorios institucionales rechazan.
- Visor de PDF en modo "browser" → pdf.js del visor integrado se
  pixela al ampliar; el modo browser conserva SyncTeX.
- Actualizaciones automáticas de Zotero desactivadas → un salto de
  versión mayor a mitad de proyecto puede romper Better BibTeX.
- Estrategia de ejecución: rebanada vertical (pipeline completo para
  afinidad primero), no capas horizontales.

**Estado del entorno:**
- MiKTeX 26.5, Strawberry Perl 5.42.3, latexmk 4.88: operativos.
- Zotero 10 con Better BibTeX: instalado y funcionando.
- Compilación de main.tex: correcta, PDF con fuentes vectoriales.
- Pendiente: exportar referencias.bib; actualizar MiKTeX Console.

**Riesgos y deuda técnica:**
- MiKTeX sin actualizar. Riesgo de desajuste entre biblatex y biber.
- Metadatos sucios en Zotero (ítems sin año, material suplementario
  importado como artículo). Corregir antes de citar, porque cambiar
  el año altera la clave de cita.
- Nomenclatura inconsistente de carpetas (docs/Project). Normalizar
  antes de que el repositorio tenga historial compartido.

**Siguiente paso:** exportar referencias.bib y compilar con una cita real.