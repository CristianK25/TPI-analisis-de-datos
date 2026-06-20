# Hito 5 – Informe de Gestión y Propuesta

> **Trabajo Práctico Integrador – Análisis de Datos Inicial (TUP)**
> **Integrantes:** Cristian Krahulik · Tomas Mastropietro · Juan Segura · Lautaro Castillo
> **Audiencia:** Coordinación académica (perfil no técnico).
> **Base de evidencia:** 500.000 registros de estudiantes, limpiados y enriquecidos en el Hito 2 (`data/dataset_CLEAN.csv`) y analizados visualmente en los Hitos 3 y 4.

Este documento traduce el análisis de datos en un **diagnóstico** del desempeño académico y **dos propuestas de mejora factibles**, cada una justificada con la evidencia hallada. No se proponen acciones genéricas: cada decisión está atada a un número del dataset.

---

## 1. Diagnóstico Académico — Qué cuentan los datos

El análisis de los Hitos 3 y 4 deja **cuatro hallazgos** que, leídos en conjunto, describen el problema central de la institución.

### Hallazgo 1 · El esfuerzo rinde, pero el agotamiento se lo come
Estudiar más horas mejora la nota en **todos** los grupos. Sin embargo, la *tasa de retorno* del esfuerzo cae cuando el alumno está agotado (alto estrés + poco sueño): la pendiente baja de **0,68 a 0,56 puntos por hora de estudio**, y la nota media del grupo agotado es **2,4 puntos menor** (55,8 vs 58,2). Al llegar a las 40 h semanales, un alumno descansado saca en promedio **5 puntos más** que uno agotado que estudió lo mismo.
**Alcance:** el agotamiento afecta a **~127.000 alumnos (25 % del total)**.

### Hallazgo 2 · La brecha digital amplía las diferencias
Con conectividad **mala/crítica**, cada hora de estudio rinde **0,53 puntos**; con conectividad **excelente**, rinde **0,72**. La misma hora de estudio vale un **36 % más** para quien tiene buen internet. La brecha **no aparece al inicio** (todos arrancan en ~47 pts con poco estudio): se *abre en abanico* a medida que el alumno se esfuerza más. Al llegar a las 40 h, la diferencia es de **8 puntos** de nota final.

### Hallazgo 3 · Conviven dos perfiles atípicos opuestos
| Perfil | N | Horas estudio | Asistencia | Nota final | Estrés | Autoeficacia |
|---|---|---|---|---|---|---|
| **Autónomo Exitoso** | 2.624 | ~19 h | 6 % | **93,3** | 5,50 | 4,62 |
| **Ansiedad / Esfuerzo Ineficiente** | 7.992 | **34 h** | 77 % | **41,1** | **6,97** | **3,87** |

El grupo de ansiedad estudia **casi el doble** y visita mucho más la biblioteca (13,3 visitas/mes), pero reprueba. **Más horas no equivalen a mejor nota:** la diferencia está en *cómo* se estudia y en el perfil socio-emocional.

### Hallazgo 4 · Las palancas reales son hábitos + trayectoria + autoeficacia
El mapa de correlaciones sobre los 500.000 registros confirma qué mueve la nota final:

| Factor | Correlación con la nota |
|---|---|
| Horas de estudio | **+0,45** |
| GPA previo | **+0,41** |
| Autoeficacia | **+0,35** |
| Nivel de estrés | **−0,14** (único lastre relevante) |
| Asistencia | +0,05 (casi irrelevante) |
| Horas de sueño / Redes sociales | ~0,00 (sin efecto) |

**Lectura clave:** la **asistencia por sí sola es casi irrelevante** — estar presente no es lo mismo que aprender. Y la **autoeficacia** viene en paquete con la motivación (r=0,45): reforzar la confianza arrastra varias palancas a la vez.

### Síntesis del diagnóstico
> El sistema **no tiene un problema de cantidad de esfuerzo, sino de eficiencia del esfuerzo.**
Hay un núcleo de **~10 % de alumnos en riesgo** (baja asistencia + bajo GPA) y un grupo mayor que **trabaja mucho y mal**, frenado por estrés, mala técnica de estudio, baja autoeficacia y, en muchos casos, malas condiciones de conectividad.

---

## 2. Propuestas de Mejora (justificadas con datos)

### 🅰️ Propuesta A — Programa de "Técnica de Estudio y Manejo del Estrés"
**Dirigida al perfil _Ansiedad / Esfuerzo Ineficiente_.**

**Acción concreta:** detectar tempranamente a los alumnos que estudian ≥ 30 h y/o visitan mucho la biblioteca pero rinden por debajo de 60, y derivarlos a un **taller obligatorio** de técnicas de estudio efectivas + regulación del estrés (sesiones cortas, manejo de carga, exámenes simulados y **tutorías entre pares** con Autónomos Exitosos).

**Por qué tendría impacto (evidencia):**
- El grupo ya pone las horas (**34 h/semana**, casi el doble del promedio de 18 h) y aun así saca **41 puntos**: el problema es de **método, no de voluntad**. Es la población con **mayor potencial de mejora por unidad de esfuerzo**.
- El estrés es el **único lastre** correlacionado negativamente con la nota (r = −0,14) y es la variable más alta de este perfil (**6,97/10**): bajarlo ataca directamente el cuello de botella identificado.
- La **autoeficacia** (r = +0,35 con la nota) es la más baja de este grupo (**3,87**). Como se mueve junto con la motivación (r = +0,45), reforzar la confianza con tutorías entre pares puede arrastrar varias palancas simultáneamente.

**Métrica de éxito:** subir la nota media del grupo y reducir su nivel de estrés promedio en las cohortes intervenidas vs. las no intervenidas.

---

### 🅱️ Propuesta B — Plan de Conectividad y Estudio Asistido
**Dirigida a cerrar la brecha digital (~95.000 alumnos con internet ≤ 4,5).**

**Acción concreta:** ofrecer a los alumnos de conectividad **Mala/Crítica** acceso a **espacios de estudio con buena conexión** (salas/biblioteca con wifi garantizado, préstamo de hotspots) y **materiales descargables para uso offline**.

**Por qué tendría impacto (evidencia):**
- La diferencia de rendimiento entre buena y mala conectividad **no es de origen, es de oportunidad**: arranca igual (~47 pts con poco estudio) y se abre solo cuando el alumno intenta estudiar más. La mala conexión **castiga justamente al que se esfuerza**.
- Llevar a estos alumnos de la pendiente **0,53** hacia la del grupo con buena conexión (**0,72**) significa recuperar **~36 % más de retorno por cada hora estudiada**, sobre una población de **~95.000 personas**.
- Es una intervención de **infraestructura, no de aptitud**: no requiere cambiar al alumno, solo **nivelar la cancha**. Por eso es factible y de impacto medible a corto plazo.

**Métrica de éxito:** acortar la brecha de 8 puntos en la nota final entre los grupos de conectividad alta y baja a igual carga de estudio.

---

## 3. Conclusión Final — Impacto esperado

Ambas propuestas atacan **el mismo diagnóstico desde dos ángulos**, convirtiendo *esfuerzo* en *resultados*:

- **Propuesta A** recupera al alumno que **ya se esfuerza pero rinde mal** (problema de método y estrés) → población de **mayor sensibilidad** a la intervención.
- **Propuesta B** nivela al alumno que **se esfuerza pero no tiene las condiciones** (problema de contexto) → población de **mayor volumen**.

Como las palancas de la nota son **hábitos de estudio, autoeficacia y reducción del estrés** —y *no* la mera asistencia ni el sueño—, focalizar recursos en **técnica de estudio**, **acompañamiento psicoemocional** y **condiciones materiales de estudio** es donde la evidencia predice el **mayor retorno por peso/hora invertida**.

**Objetivo medible global:** elevar la pendiente esfuerzo→nota de los grupos rezagados y reducir el ~10 % de alumnos en situación de riesgo.

---

*Las cifras de este informe provienen del análisis reproducible en `notebooks/TPI_Analisis_Datos.ipynb` (Hitos 3 y 4) y pueden explorarse de forma interactiva en el dashboard (`streamlit run app.py`).*
