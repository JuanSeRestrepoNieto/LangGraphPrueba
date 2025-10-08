# LangGraph - Ejemplo Académico Completo

Este repositorio contiene ejemplos académicos completos de cómo usar **LangGraph**, una biblioteca de Python para construir aplicaciones con agentes de IA y flujos de trabajo complejos.

## 📚 ¿Qué es LangGraph?

LangGraph es una biblioteca construida sobre LangChain que permite crear aplicaciones de agentes con **estados**, **nodos** y **grafos** de flujo de trabajo. Es especialmente útil para:

- Crear agentes conversacionales con memoria
- Diseñar flujos de trabajo complejos con múltiples pasos
- Implementar sistemas multi-agente
- Controlar el flujo de ejecución de manera precisa

## 🎯 Conceptos Clave

### 1. **Estados (State)**
Representan el contexto y datos que fluyen a través del grafo. Define qué información se mantiene y comparte entre nodos.

### 2. **Nodos (Nodes)**
Funciones que procesan y transforman el estado. Cada nodo realiza una operación específica.

### 3. **Grafos (Graphs)**
Definen el flujo de ejecución entre nodos. Determinan cómo se conectan y se comunican los nodos.

### 4. **Aristas (Edges)**
Conectan nodos y determinan el flujo de control. Pueden ser condicionales o directas.

## 📁 Estructura del Proyecto

```
LagGraphPrueba/
├── README.md                          # Este archivo
├── requirements.txt                   # Dependencias del proyecto
├── .env.example                       # Ejemplo de configuración
├── ejemplo_langgraph.py              # Ejemplo básico sin API
└── ejemplo_langgraph_avanzado.py    # Ejemplo avanzado con OpenAI
```

## 🚀 Instalación

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/JuanSeRestrepoNieto/LagGraphPrueba.git
cd LagGraphPrueba
```

### Paso 2: Crear entorno virtual (recomendado)

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno (opcional)

Para el ejemplo avanzado con OpenAI:

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu clave API de OpenAI
# OPENAI_API_KEY=tu-clave-real-aqui
```

## 📖 Ejemplos Incluidos

### 1. Ejemplo Básico (`ejemplo_langgraph.py`)

**Características:**
- No requiere API key de OpenAI
- Demuestra conceptos fundamentales de LangGraph
- Incluye comentarios detallados paso a paso
- Maneja estados, nodos y aristas condicionales

**Ejecutar:**
```bash
python ejemplo_langgraph.py
```

**Lo que aprenderás:**
1. Cómo definir estados con TypedDict
2. Cómo crear nodos de procesamiento
3. Cómo conectar nodos con aristas
4. Cómo usar aristas condicionales para controlar el flujo
5. Cómo ejecutar el grafo con diferentes estados

**Salida esperada:**
```
======================================================================
  EJEMPLO ACADÉMICO DE LANGGRAPH
======================================================================

📊 Construyendo el grafo...
✅ Grafo construido exitosamente

🚀 Ejecutando el grafo con estado inicial...
   Mensaje inicial: 'Hola'

🔵 Ejecutando nodo: SALUDO
🟢 Ejecutando nodo: PROCESAMIENTO
...
```

### 2. Ejemplo Avanzado (`ejemplo_langgraph_avanzado.py`)

**Características:**
- Integración con OpenAI GPT (opcional)
- Uso de herramientas personalizadas (calculadora, información)
- Manejo avanzado de estados
- Modo simulado cuando no hay API key
- Incluye modo interactivo

**Ejecutar:**
```bash
python ejemplo_langgraph_avanzado.py
```

**Lo que aprenderás:**
1. Cómo integrar LangGraph con modelos de lenguaje
2. Cómo crear y usar herramientas personalizadas
3. Cómo implementar verificaciones y enrutamiento avanzado
4. Cómo manejar errores y casos especiales
5. Cómo crear interfaces interactivas

**Modo interactivo:**
Para usar el modo interactivo, descomenta la última línea del archivo:
```python
# modo_interactivo()
```

## 🔧 Arquitectura del Sistema

### Flujo Básico

```
Usuario → [Entrada] → Nodo Inicial → Nodo Procesamiento → [Decisión]
                                                              ↓
                                            ¿Continuar? → Sí → Volver a Procesar
                                                    ↓
                                                   No
                                                    ↓
                                              Nodo Despedida → FIN
```

### Flujo Avanzado

```
Usuario → [Entrada] → Agente IA → [Verificación] → ¿Usar herramientas?
                         ↑                              ↓
                         |                             Sí
                         |                              ↓
                         └─────────── [Ejecutar Herramienta]
                                            ↓
                                           No
                                            ↓
                                      [Decisión Final]
                                            ↓
                                    ¿Continuar? → Sí/No
```

## 📝 Paso a Paso del Código

### Paso 1: Definir el Estado

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class EstadoAgente(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    contador: int
```

### Paso 2: Crear Nodos

```python
def nodo_procesamiento(state: EstadoAgente) -> EstadoAgente:
    # Procesar el estado
    respuesta = AIMessage(content="Respuesta procesada")
    return {"messages": [respuesta]}
```

### Paso 3: Construir el Grafo

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(EstadoAgente)
workflow.add_node("procesamiento", nodo_procesamiento)
workflow.set_entry_point("procesamiento")
workflow.add_edge("procesamiento", END)
app = workflow.compile()
```

### Paso 4: Ejecutar

```python
estado_inicial = {
    "messages": [HumanMessage(content="Hola")],
    "contador": 0
}
resultado = app.invoke(estado_inicial)
```

## 🎓 Casos de Uso Académicos

### 1. Asistente Educativo
- Responde preguntas sobre temas específicos
- Proporciona explicaciones paso a paso
- Adapta el contenido según el nivel del estudiante

### 2. Sistema de Tutoría
- Evalúa el conocimiento del estudiante
- Genera ejercicios personalizados
- Proporciona retroalimentación constructiva

### 3. Investigador Automatizado
- Busca información sobre temas específicos
- Sintetiza múltiples fuentes
- Genera resúmenes estructurados

### 4. Asistente de Programación
- Analiza código y detecta errores
- Sugiere mejoras y optimizaciones
- Explica conceptos de programación

## 🛠️ Personalización

### Agregar Nuevos Nodos

```python
def mi_nodo_personalizado(state: EstadoAgente) -> EstadoAgente:
    # Tu lógica aquí
    return {"messages": [AIMessage(content="Mi respuesta")]}

# Agregar al grafo
workflow.add_node("mi_nodo", mi_nodo_personalizado)
```

### Crear Herramientas Personalizadas

```python
from langchain_core.tools import tool

@tool
def mi_herramienta(parametro: str) -> str:
    """Descripción de la herramienta."""
    # Tu lógica aquí
    return "Resultado"
```

### Modificar el Flujo

```python
# Arista condicional personalizada
workflow.add_conditional_edges(
    "nodo_origen",
    lambda state: "destino1" if condicion(state) else "destino2",
    {
        "destino1": "nodo_destino_1",
        "destino2": "nodo_destino_2"
    }
)
```

## 🔍 Depuración y Solución de Problemas

### Problema: Error de importación

```bash
# Solución: Reinstalar dependencias
pip install --upgrade langgraph langchain langchain-openai
```

### Problema: Error de API key

```bash
# Verificar que .env existe y contiene la clave
cat .env

# Asegurarse de que python-dotenv está instalado
pip install python-dotenv
```

### Problema: El grafo no ejecuta como esperado

```python
# Agregar prints para depuración en cada nodo
def nodo_con_debug(state):
    print(f"Estado actual: {state}")
    # Tu lógica...
    return nuevo_estado
```

## 📚 Recursos Adicionales

### Documentación Oficial
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

### Tutoriales
- [LangGraph Quickstart](https://langchain-ai.github.io/langgraph/tutorials/introduction/)
- [Building Agents with LangGraph](https://langchain-ai.github.io/langgraph/concepts/)

### Comunidad
- [LangChain Discord](https://discord.gg/langchain)
- [GitHub Discussions](https://github.com/langchain-ai/langgraph/discussions)

## 🤝 Contribuir

Si deseas contribuir a este proyecto educativo:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible para fines educativos.

## ✨ Autor

**Juan Sebastián Restrepo Nieto**

## 🙏 Agradecimientos

- LangChain Team por crear LangGraph
- OpenAI por sus modelos de lenguaje
- La comunidad de desarrolladores de IA

---

**Nota:** Este es un proyecto educativo diseñado para aprender los conceptos fundamentales de LangGraph. Para aplicaciones en producción, considera aspectos adicionales como seguridad, escalabilidad y manejo robusto de errores.