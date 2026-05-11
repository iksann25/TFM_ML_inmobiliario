# AVM Valencia: Modelo de Valoración Automatizada mediante Machine Learning

Este repositorio contiene el ecosistema computacional desarrollado para el Trabajo de Fin de Máster (TFM): **"Desarrollo de un Modelo de Valoración Automatizada (AVM) mediante Machine Learning: Aplicación al mercado residencial de Valencia capital"**.

El proyecto aborda de forma integral el ciclo de vida de un proyecto de Ciencia de Datos: desde la extracción masiva de datos (*Web Scraping*) y la auditoría semántica mediante NLP, hasta la implementación de un comité híbrido de algoritmos para la tasación inmobiliaria.

## 🚀 Estructura del Proyecto

El repositorio está organizado de forma secuencial siguiendo la lógica metodológica de la investigación:

- **`01_scraper/`**: Scripts de ingeniería inversa y extracción automatizada del DOM desarrollados con Selenium y WebDriver-Manager.
- **`02_eda_inicial_y_limpieza/`**: Auditoría de calidad de datos y resolución de inconsistencias mediante lógica de manejo de excepciones.
- **`03_transformaciones/`**: Ingeniería de Características (Feature Engineering), vectorización (One-Hot Encoding) y creación de índices sintéticos (*Amenity Score*).
- **`04_eda_final/`**: Análisis Exploratorio de Datos avanzado y diagnóstico de distribuciones estadísticas post-procesamiento.
- **`05_modelos/`**: Entrenamiento y validación del modelo *Baseline* (Random Forest) y del "Comité de Expertos" (Voting Regressor: RF + CatBoost).
- **`06_app_streamlit/`**: Código fuente de la interfaz de usuario para el despliegue del modelo en un entorno de producción.

## 🛠️ Requisitos e Instalación

Para garantizar la reproducibilidad del experimento (tal y como se detalla en la sección 4.3.3 de la memoria), se recomienda el uso de un entorno virtual aislado:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/TFM-Valencia-AVM.git](https://github.com/tu-usuario/TFM-Valencia-AVM.git)
   cd TFM-Valencia-AVM
