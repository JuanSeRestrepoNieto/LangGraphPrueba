# Guía Rápida de LangGraph

## ¿Qué vas a aprender?

Esta guía te enseñará los conceptos básicos de LangGraph en 5 minutos.

## Conceptos Fundamentales

### 1. Estado (State)
El estado es un diccionario que contiene toda la información que fluye en tu aplicación.

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class MiEstado(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    contador: int
```

**¿Por qué `Annotated`?**
- Permite definir cómo combinar valores cuando múltiples nodos actualizan el mismo campo
- `add_messages` concatena mensajes en lugar de reemplazarlos

### 2. Nodos (Nodes)
Los nodos son funciones que procesan el estado.

```python
def mi_nodo(state: MiEstado) -> MiEstado:
    # Procesar el estado
    nuevo_mensaje = AIMessage(content="Hola!")
    
    # Retornar actualizaciones
    return {
        "messages": [nuevo_mensaje],
        "contador": state["contador"] + 1
    }
```

**Reglas importantes:**
- Reciben el estado completo
- Retornan solo los campos que quieren actualizar
- No modifican el estado directamente

### 3. Grafos (Graphs)
El grafo conecta los nodos y define el flujo.

```python
from langgraph.graph import StateGraph, END

# Crear el grafo
workflow = StateGraph(MiEstado)

# Agregar nodos
workflow.add_node("nodo1", mi_nodo)

# Definir punto de entrada
workflow.set_entry_point("nodo1")

# Agregar arista al final
workflow.add_edge("nodo1", END)

# Compilar
app = workflow.compile()
```

### 4. Aristas (Edges)
Conectan nodos y controlan el flujo.

#### Arista Directa
```python
# "nodo1" siempre va a "nodo2"
workflow.add_edge("nodo1", "nodo2")
```

#### Arista Condicional
```python
def decidir(state: MiEstado) -> str:
    if state["contador"] > 5:
        return "fin"
    return "continuar"

workflow.add_conditional_edges(
    "nodo1",
    decidir,
    {
        "fin": END,
        "continuar": "nodo2"
    }
)
```

## Ejemplo Completo Mínimo

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage

# 1. Definir estado
class Estado(TypedDict):
    messages: list

# 2. Crear nodo
def saludar(state: Estado) -> Estado:
    return {"messages": [AIMessage(content="¡Hola!")]}

# 3. Construir grafo
workflow = StateGraph(Estado)
workflow.add_node("saludo", saludar)
workflow.set_entry_point("saludo")
workflow.add_edge("saludo", END)
app = workflow.compile()

# 4. Ejecutar
resultado = app.invoke({"messages": [HumanMessage(content="Hola")]})
print(resultado["messages"][-1].content)  # Output: ¡Hola!
```

## Patrones Comunes

### Patrón 1: Secuencia Lineal
```
Entrada → Nodo A → Nodo B → Nodo C → Salida
```

```python
workflow.set_entry_point("nodoA")
workflow.add_edge("nodoA", "nodoB")
workflow.add_edge("nodoB", "nodoC")
workflow.add_edge("nodoC", END)
```

### Patrón 2: Bifurcación
```
         ┌─→ Nodo B → Salida
Nodo A ──┤
         └─→ Nodo C → Salida
```

```python
def decidir(state):
    return "b" if state["condicion"] else "c"

workflow.add_conditional_edges(
    "nodoA",
    decidir,
    {"b": "nodoB", "c": "nodoC"}
)
workflow.add_edge("nodoB", END)
workflow.add_edge("nodoC", END)
```

### Patrón 3: Loop Controlado
```
Nodo A → Nodo B → ¿Condición? → Sí → Volver a B
                       ↓
                      No
                       ↓
                    Salida
```

```python
def verificar_loop(state):
    if state["contador"] < 3:
        return "loop"
    return "fin"

workflow.add_conditional_edges(
    "nodoB",
    verificar_loop,
    {
        "loop": "nodoB",  # Volver al mismo nodo
        "fin": END
    }
)
```

**⚠️ IMPORTANTE:** Configura `recursion_limit` para evitar loops infinitos:
```python
app = workflow.compile()
resultado = app.invoke(estado_inicial, config={"recursion_limit": 50})
```

## Debugging

### Ver el estado en cada paso
```python
def nodo_con_debug(state):
    print(f"Estado actual: {state}")
    # Tu lógica...
    return nuevo_estado
```

### Capturar excepciones
```python
def nodo_seguro(state):
    try:
        # Tu lógica
        return {"resultado": proceso(state)}
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
```

### Streaming de resultados
```python
for chunk in app.stream(estado_inicial):
    print(chunk)
```

## Mejores Prácticas

### ✅ Hacer
- Mantener nodos pequeños y enfocados
- Usar nombres descriptivos para nodos
- Documentar funciones de decisión
- Manejar errores apropiadamente
- Probar cada nodo independientemente

### ❌ Evitar
- Loops infinitos sin condición de salida
- Nodos que hacen demasiadas cosas
- Modificar el estado directamente
- Ignorar errores
- Crear grafos demasiado complejos

## Próximos Pasos

1. **Ejecuta los ejemplos incluidos:**
   ```bash
   python ejemplo_langgraph.py
   python ejemplo_langgraph_avanzado.py
   ```

2. **Modifica los ejemplos:**
   - Agrega nuevos nodos
   - Cambia las condiciones
   - Experimenta con diferentes flujos

3. **Crea tu propio agente:**
   - Identifica tu caso de uso
   - Define tu estado
   - Diseña el flujo
   - Implementa los nodos
   - Prueba y refina

## Recursos Adicionales

- [Documentación Oficial](https://langchain-ai.github.io/langgraph/)
- [Ejemplos en GitHub](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Tutorial Interactivo](https://langchain-ai.github.io/langgraph/tutorials/introduction/)

## Glosario

- **Estado**: Datos compartidos entre nodos
- **Nodo**: Función que procesa el estado
- **Grafo**: Estructura que conecta nodos
- **Arista**: Conexión entre nodos
- **Punto de entrada**: Primer nodo a ejecutar
- **END**: Constante que marca el final del grafo
- **Compilar**: Preparar el grafo para ejecución
- **Invocar**: Ejecutar el grafo con un estado inicial

---

¿Listo para empezar? ¡Ejecuta `python ejemplo_langgraph.py` y observa cómo funciona!
