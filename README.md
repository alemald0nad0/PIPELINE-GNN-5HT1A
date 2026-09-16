# Pipeline in silico para el receptor 5-HT1A: predicción de afinidad, toxicidad y permeabilidad de la BHE mediante GNN

![Estado](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)

> ⚠️ Proyecto en desarrollo activo. Los resultados cuantitativos (métricas de los modelos) aún no están disponibles; este README se actualizará conforme avancen los entregables.

## Tabla de contenidos

- [Descripción](#descripción)
- [Objetivos](#objetivos)
- [Datos](#datos)
- [Metodología](#metodología)
- [Principios metodológicos](#principios-metodológicos)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Instalación](#instalación)
- [Estado actual y hoja de ruta](#estado-actual-y-hoja-de-ruta)
- [Documentación](#documentación)
- [Licencia y datos de terceros](#licencia-y-datos-de-terceros)
- [Autoría](#autoría)

## Descripción

Este repositorio contiene el desarrollo de un **pipeline in silico** para la identificación temprana de moléculas con potencial afinidad por el receptor **5-HT1A** (serotonina 1A), relevante en el desarrollo de fármacos ansiolíticos y antidepresivos. El pipeline integra tres modelos predictivos entrenados sobre representaciones moleculares en forma de grafo:

1. **Afinidad al receptor** — regresión sobre pKi / pIC50.
2. **Toxicidad** — clasificación multitarea, en la línea de Tox21.
3. **Permeabilidad de la barrera hematoencefálica (BHE)** — clasificación binaria.

El enfoque principal son **redes neuronales de grafos (GNN)**, comparadas de forma sistemática contra líneas base clásicas (huellas moleculares ECFP4/Morgan + Random Forest o LightGBM). El objetivo del proyecto no es solo producir un modelo, sino producir una evaluación metodológicamente defendible de cuándo y por qué ese modelo funciona —o no— mejor que una alternativa más simple.

## Objetivos

- Construir un flujo reproducible de curación y estandarización de datos moleculares provenientes de múltiples fuentes públicas.
- Entrenar y evaluar modelos GNN para los tres endpoints (afinidad, toxicidad, BHE).
- Establecer líneas base clásicas robustas como referencia obligatoria de comparación.
- Reportar el desempeño con particiones de evaluación apropiadas para descubrimiento de fármacos (no aleatorias), y con métricas adecuadas al desbalance de clases.

## Datos

Fuentes públicas utilizadas (sujetas a ampliarse conforme se definan los endpoints finales):

| Fuente | Endpoint | Notas |
|---|---|---|
| ChEMBL | Afinidad (5-HT1A) | Fuente principal de bioactividad |
| PDSP Ki Database | Afinidad (5-HT1A) | Complementa y valida ChEMBL |
| BindingDB | Afinidad (5-HT1A) | Se solapa con ChEMBL/PDSP — requiere deduplicación |
| Tox21 | Toxicidad | Clasificación multitarea |
| B3DB / BBBP | Permeabilidad BHE | Clasificación binaria |

Los conjuntos de afinidad se unifican con una política explícita de deduplicación por **InChIKey** y agregación documentada de mediciones discordantes; los ensayos de tipo Ki, IC50 y EC50 **no se combinan sin justificación explícita**, dada su heterogeneidad.

## Metodología

- **Representación molecular:** grafos moleculares (átomos como nodos, enlaces como aristas) tras estandarización de SMILES — desalinización, neutralización, elección de tautómero canónico y tratamiento explícito de estereoquímica.
- **Modelos:** GNN (PyTorch Geometric / DGL-LifeSci) frente a ECFP4/Morgan + Random Forest o LightGBM como línea base.
- **Partición de datos:** por *scaffold* (Bemis-Murcko) o por clúster de similitud. Una partición aleatoria se reporta únicamente como referencia superior, etiquetada explícitamente como tal — nunca como evaluación principal.
- **Desbalance de clases:** en toxicidad y BHE se reporta AUPRC y matriz de confusión, no solo ROC-AUC.
- **Dominio de aplicabilidad:** declarado para cada modelo antes de considerarlo utilizable en cribado.

## Principios metodológicos

Estos criterios son innegociables para cualquier resultado reportado en este repositorio:

- Ninguna evaluación se presenta como definitiva si se basa en partición aleatoria de datos.
- Toda GNN se compara contra una línea base clásica bien ajustada; si la línea base gana, se reporta como resultado legítimo, no se oculta.
- El lenguaje usado es correlacional: los modelos **predicen**, nunca "determinan" o "explican".
- Reproducibilidad: semillas fijas, versiones de dependencias ancladas, y fecha/consulta exacta de descarga documentada para cada conjunto de datos.

## Estructura del repositorio

```
PIPELINE-GNN-5HT1A/
├── docs/
│   ├── Project/              # Documento del proyecto en LaTeX (local, no versionado — ver .gitignore)
│   │   ├── build/
│   │   ├── figures/
│   │   ├── sections/
│   │   ├── main.tex
│   │   └── referencias.bib   # Exportado automáticamente desde Zotero
│   └── bitacora_00.md        # Bitácora de decisiones y avances
├── notebooks/                # Solo exploración; llaman a src/, nunca al revés
│   ├── EDA_Afinity.ipynb
│   └── EDA_afinity.py
├── results/                  # Métricas, figuras y artefactos de evaluación
├── src/                      # Funciones puras y testeables del pipeline
├── tools/
│   └── snapshot.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Instalación

Requiere Python 3.11+ (ajustar al valor real definido en `pyproject.toml`). Entorno de referencia: Windows.

```powershell
git clone https://github.com/alemald0nad0/PIPELINE-GNN-5HT1A.git
cd PIPELINE-GNN-5HT1A
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Estado actual y hoja de ruta

**Entregable 1 (en curso):** EDA de los conjuntos, preprocesamiento y estandarización de SMILES, modelo baseline y versiones iniciales de los tres modelos.

- [x] Estructura del repositorio y documentación LaTeX
- [ ] EDA de los conjuntos de afinidad, toxicidad y BHE
- [ ] Estandarización y deduplicación de estructuras moleculares
- [ ] Modelos baseline (ECFP4/Morgan + RF/LightGBM)
- [ ] Versiones iniciales de los modelos GNN
- [ ] Resultados y comparación baseline vs. GNN

Los resultados cuantitativos se publicarán en `results/` y se resumirán en este README conforme estén disponibles.

## Documentación

- El documento técnico completo (LaTeX, `docs/Project/`) se mantiene localmente y **no se publica** en este repositorio (ver `.gitignore`); no está disponible al clonar.
- Bitácora de avances y decisiones: `docs/bitacora_00.md`.
- Bibliografía gestionada en Zotero, exportada automáticamente a `referencias.bib` dentro del documento local.

## Licencia y datos de terceros

Este repositorio se distribuye bajo licencia **MIT** (ver [`LICENSE`](./LICENSE)). La licencia cubre el código de este repositorio; **no cubre ni redistribuye** los datos de ChEMBL, PDSP, BindingDB, Tox21 ni B3DB/BBBP, que no se versionan aquí y conservan sus propios términos de uso. En su lugar, se documentan los scripts y la fecha exacta de consulta usados para obtenerlos.

## Autoría

Proyecto desarrollado por Alejandro Maldonado López ([@alemald0nad0](https://github.com/alemald0nad0)) y equipo, como parte de la Licenciatura en Ciencia de Datos, ESCOM-IPN.# Pipeline in silico para el receptor 5-HT1A: predicción de afinidad, toxicidad y permeabilidad de la BHE mediante GNN



## Autoría

Proyecto desarrollado por Alejandro Maldonado López ([@alemald0nad0](https://github.com/alemald0nad0)) y equipo, como parte de la Licenciatura en Ciencia de Datos, ESCOM-IPN.
