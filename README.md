# AVM Valencia: Modelo de Valoración Automatizada mediante Machine Learning

Este repositorio contiene el ecosistema computacional desarrollado para el Trabajo de Fin de Máster (TFM): **"Desarrollo de un Modelo de Valoración Automatizada (AVM) mediante Machine Learning: Aplicación al mercado residencial de Valencia capital"**.

El proyecto aborda de forma integral el ciclo de vida de un proyecto de Ciencia de Datos: desde la extracción masiva de datos (*Web Scraping*) y la auditoría semántica mediante NLP, hasta la implementación de un comité híbrido de algoritmos para la tasación inmobiliaria y su despliegue funcional.

## 🚀 Estructura del Repositorio

El proyecto está organizado de forma secuencial siguiendo la metodología de la investigación:

- **`01_scraper/`**: Scripts de ingeniería inversa y extracción automatizada del DOM desarrollados con Selenium y WebDriver-Manager para la adquisición de datos de portales inmobiliarios.
- **`02_eda_inicial_y_limpieza/`**: Notebooks de auditoría de calidad de datos, manejo de valores nulos y resolución de inconsistencias mediante lógica de excepciones.
- **`03_transformaciones/`**: Ingeniería de Características (Feature Engineering), vectorización (One-Hot Encoding) y creación de índices sintéticos (*Amenity Score*).
- **`04_eda_final/`**: Análisis Exploratorio de Datos avanzado y diagnóstico de distribuciones estadísticas post-procesamiento.
- **`05_modelos/`**: Entrenamiento, optimización de hiperparámetros y validación del modelo *Baseline* (Random Forest) y del "Comité de Expertos" (Voting Regressor: RF + CatBoost).
- **`06_app_streamlit/`**: Código fuente de la interfaz de usuario para el despliegue del modelo en un entorno de producción local.

## 🛠️ Instalación y Replicabilidad

Para garantizar la reproducibilidad del experimento, se recomienda el uso de un entorno virtual aislado:

1. **Clonar el repositorio:**
   git clone https://github.com/iksann25/TFM_ML_inmobiliario.git
   cd TFM_ML_inmobiliario

2. **Crear y activar entorno virtual:**
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate

3. **Instalar dependencias:**
   pip install -r requirements.txt

## 📊 Resultados del Modelo

El sistema de valoración final alcanzó hitos de rendimiento que validan su viabilidad para el sector PropTech:

| Métrica | Modelo Global (Híbrido) | Modelo de Ultra-Precisión (Core) |
| :--- | :--- | :--- |
| **Varianza Explicada ($R^2$)** | 80.03% | 62.38% |
| **Error Medio Absoluto (MAE)** | 79.504 € | **36.668 €** |
| **Error Porcentual (MAPE)** | 20.35% | **14.40%** |

*Nota: La segmentación estratégica permitió reducir el error medio en más de 42.000€, optimizando el modelo para el 90% de la oferta residencial estándar.*

## 🔬 Metodología Destacada

- **Auditoría Semántica (NLP):** Uso de expresiones regulares con delimitadores de palabra exacta (`\b`) para corregir falsos positivos en variables de confort (Garaje, Jardín, Ascensor).
- **Mitigación de Sesgo Geográfico:** Algoritmo de rescate condicional basado en tipologías de URL para neutralizar la contaminación léxica de parques públicos en descripciones privadas.
- **Explainable AI (XAI):** Implementación de la Importancia de Variables para dotar de transparencia a los coeficientes hedónicos del mercado valenciano.

## ✒️ Autor

**Daniel López Muñoz**
*Máster en Big Data y Ciencia de Datos*
*Universidad Internacional de Valencia (VIU)*

---

> **Aviso Académico:** Este proyecto utiliza precios de oferta (*asking prices*). Se reconoce un sesgo inherente respecto al precio final de transacción, discutido detalladamente en la sección de limitaciones de la memoria técnica (Capítulo 4.13.3.5).
