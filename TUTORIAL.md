# Tutorial: Crea tu Primer Agente con LangGraph

Este tutorial te guiará paso a paso en la creación de tu primer agente conversacional usando LangGraph.

## 🎯 Objetivo

Crear un agente que:
1. Responda preguntas básicas
2. Recuerde el contexto de la conversación
3. Maneje despedidas apropiadamente

## 📋 Prerrequisitos

```bash
pip install langgraph langchain langchain-core
```

## Paso 1: Importar Librerías

Crea un nuevo archivo `mi_agente.py`:

```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
```

**¿Qué hacen estas importaciones?**
- `TypedDict`: Define la estructura del estado
- `BaseMessage, HumanMessage, AIMessage`: Tipos de mensajes
- `StateGraph, END`: Construcción del grafo
- `add_messages`: Función para combinar mensajes

## Paso 2: Definir el Estado

```python
class EstadoConversacion(TypedDict):
    """Estado que mantiene la conversación."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    nombre_usuario: str
```

**💡 Explicación:**
- `messages`: Lista de mensajes de la conversación
- `Annotated[..., add_messages]`: Cuando se agregan mensajes, se concatenan en lugar de reemplazarse
- `nombre_usuario`: Campo adicional para personalizar respuestas

## Paso 3: Crear el Primer Nodo

```python
def nodo_bienvenida(state: EstadoConversacion) -> EstadoConversacion:
    """Nodo que da la bienvenida al usuario."""
    # Obtener el último mensaje
    ultimo_mensaje = state["messages"][-1].content
    
    # Intentar extraer el nombre
    nombre = state.get("nombre_usuario", "")
    if not nombre:
        # Si el mensaje contiene "me llamo" o "soy"
        if "me llamo" in ultimo_mensaje.lower():
            nombre = ultimo_mensaje.lower().split("me llamo")[-1].strip()
        elif "soy" in ultimo_mensaje.lower():
            nombre = ultimo_mensaje.lower().split("soy")[-1].strip()
    
    # Crear respuesta
    if nombre:
        respuesta = f"¡Hola {nombre}! Es un placer conocerte. ¿En qué puedo ayudarte?"
    else:
        respuesta = "¡Hola! Soy tu asistente virtual. ¿Cuál es tu nombre?"
    
    return {
        "messages": [AIMessage(content=respuesta)],
        "nombre_usuario": nombre
    }
```

**💡 Explicación:**
- Recibimos el estado completo
- Procesamos el último mensaje
- Retornamos SOLO los campos que cambian
- LangGraph se encarga de hacer el merge

## Paso 4: Crear Nodo de Conversación

```python
def nodo_conversacion(state: EstadoConversacion) -> EstadoConversacion:
    """Nodo que maneja la conversación general."""
    ultimo_mensaje = state["messages"][-1].content.lower()
    nombre = state.get("nombre_usuario", "amigo")
    
    # Respuestas basadas en palabras clave
    if "como estas" in ultimo_mensaje or "cómo estás" in ultimo_mensaje:
        respuesta = f"¡Estoy muy bien, {nombre}! Gracias por preguntar. ¿Y tú?"
    
    elif "que puedes hacer" in ultimo_mensaje or "qué puedes hacer" in ultimo_mensaje:
        respuesta = f"{nombre}, puedo ayudarte con:\n" \
                   "- Responder preguntas básicas\n" \
                   "- Mantener una conversación\n" \
                   "- Recordar tu nombre"
    
    elif "hora" in ultimo_mensaje:
        from datetime import datetime
        hora_actual = datetime.now().strftime("%H:%M")
        respuesta = f"La hora actual es {hora_actual}, {nombre}."
    
    elif "gracias" in ultimo_mensaje:
        respuesta = f"¡De nada, {nombre}! Estoy aquí para ayudarte."
    
    else:
        respuesta = f"Entiendo, {nombre}. Estoy aquí para ayudarte. " \
                   "¿Hay algo específico en lo que pueda asistirte?"
    
    return {"messages": [AIMessage(content=respuesta)]}
```

**💡 Explicación:**
- Usamos el nombre del usuario almacenado en el estado
- Respondemos basándonos en palabras clave
- En un sistema real, aquí usaríamos un modelo de IA

## Paso 5: Crear Nodo de Despedida

```python
def nodo_despedida(state: EstadoConversacion) -> EstadoConversacion:
    """Nodo que maneja las despedidas."""
    nombre = state.get("nombre_usuario", "")
    
    if nombre:
        respuesta = f"¡Hasta luego, {nombre}! Fue un placer conversar contigo. " \
                   f"¡Que tengas un excelente día!"
    else:
        respuesta = "¡Hasta luego! Espero haberte ayudado. ¡Que tengas un excelente día!"
    
    return {"messages": [AIMessage(content=respuesta)]}
```

## Paso 6: Crear Función de Decisión

```python
def decidir_siguiente_paso(state: EstadoConversacion) -> str:
    """Decide qué hacer a continuación basándose en el último mensaje."""
    # Buscar el último mensaje del usuario
    ultimo_mensaje_usuario = None
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            ultimo_mensaje_usuario = msg.content.lower()
            break
    
    if not ultimo_mensaje_usuario:
        return END
    
    # Palabras de despedida
    despedidas = ["adiós", "adios", "chao", "bye", "hasta luego", "nos vemos"]
    if any(palabra in ultimo_mensaje_usuario for palabra in despedidas):
        return "despedida"
    
    # Si no hay nombre aún, ir a bienvenida
    if not state.get("nombre_usuario"):
        return "bienvenida"
    
    # Si ya hay nombre, continuar conversación
    return "conversacion"
```

**💡 Explicación:**
- Esta función determina el flujo del grafo
- Retorna el NOMBRE del siguiente nodo
- Es la clave para crear flujos dinámicos

## Paso 7: Construir el Grafo

```python
def crear_agente():
    """Crea y compila el grafo del agente."""
    # Crear el grafo
    workflow = StateGraph(EstadoConversacion)
    
    # Agregar los nodos
    workflow.add_node("bienvenida", nodo_bienvenida)
    workflow.add_node("conversacion", nodo_conversacion)
    workflow.add_node("despedida", nodo_despedida)
    
    # Definir el punto de entrada
    workflow.set_entry_point("bienvenida")
    
    # Agregar aristas condicionales desde cada nodo
    workflow.add_conditional_edges(
        "bienvenida",
        decidir_siguiente_paso,
        {
            "bienvenida": "bienvenida",
            "conversacion": "conversacion",
            "despedida": "despedida",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "conversacion",
        decidir_siguiente_paso,
        {
            "bienvenida": "bienvenida",
            "conversacion": "conversacion",
            "despedida": "despedida",
            END: END
        }
    )
    
    # Desde despedida, siempre terminar
    workflow.add_edge("despedida", END)
    
    # Compilar el grafo
    return workflow.compile()
```

**💡 Explicación:**
- `add_node`: Registra los nodos en el grafo
- `set_entry_point`: Define por dónde empezar
- `add_conditional_edges`: Usa la función de decisión para determinar el flujo
- `add_edge`: Conexión directa entre nodos
- `compile()`: Prepara el grafo para ejecución

## Paso 8: Crear Función Principal

```python
def main():
    """Función principal que ejecuta el agente."""
    print("="*60)
    print("  MI PRIMER AGENTE CON LANGGRAPH")
    print("="*60)
    print("Escribe 'salir' para terminar\n")
    
    # Crear el agente
    agente = crear_agente()
    
    # Estado inicial
    estado = {
        "messages": [],
        "nombre_usuario": ""
    }
    
    # Primer mensaje
    print("Agente: ¡Hola! ¿Cuál es tu nombre?")
    
    # Loop de conversación
    while True:
        # Obtener entrada del usuario
        entrada_usuario = input("\nTú: ").strip()
        
        if not entrada_usuario:
            continue
        
        if entrada_usuario.lower() == "salir":
            print("\n👋 ¡Hasta luego!")
            break
        
        # Agregar mensaje del usuario al estado
        estado["messages"].append(HumanMessage(content=entrada_usuario))
        
        # Ejecutar el agente
        try:
            estado = agente.invoke(estado)
            
            # Mostrar la respuesta del agente
            ultima_respuesta = estado["messages"][-1]
            if isinstance(ultima_respuesta, AIMessage):
                print(f"\nAgente: {ultima_respuesta.content}")
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            break

if __name__ == "__main__":
    main()
```

## Paso 9: Ejecutar el Agente

Guarda el archivo y ejecútalo:

```bash
python mi_agente.py
```

**Ejemplo de conversación:**

```
============================================================
  MI PRIMER AGENTE CON LANGGRAPH
============================================================
Escribe 'salir' para terminar

Agente: ¡Hola! ¿Cuál es tu nombre?

Tú: Me llamo Juan

Agente: ¡Hola Juan! Es un placer conocerte. ¿En qué puedo ayudarte?

Tú: ¿Qué hora es?

Agente: La hora actual es 15:30, Juan.

Tú: Gracias

Agente: ¡De nada, Juan! Estoy aquí para ayudarte.

Tú: Adiós

Agente: ¡Hasta luego, Juan! Fue un placer conversar contigo. ¡Que tengas un excelente día!
```

## 🎉 ¡Felicidades!

Has creado tu primer agente con LangGraph. Ahora puedes:

### Ejercicios de Práctica

#### Ejercicio 1: Agregar Más Funcionalidades
Agrega un nodo que responda sobre el clima:

```python
def nodo_clima(state: EstadoConversacion) -> EstadoConversacion:
    """Nodo que responde sobre el clima."""
    nombre = state.get("nombre_usuario", "")
    respuesta = f"Lo siento {nombre}, no tengo acceso a datos del clima en tiempo real. " \
               "Pero puedo ayudarte con otras cosas!"
    return {"messages": [AIMessage(content=respuesta)]}
```

Luego actualiza la función de decisión para dirigir a este nodo cuando detecte palabras como "clima" o "temperatura".

#### Ejercicio 2: Agregar Contador de Mensajes
Modifica el estado para incluir un contador:

```python
class EstadoConversacion(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    nombre_usuario: str
    contador_mensajes: int  # NUEVO
```

Actualiza cada nodo para incrementar el contador y muestra un resumen al despedirte.

#### Ejercicio 3: Agregar Validación
Crea un nodo que valide que el nombre del usuario no esté vacío y tenga al menos 2 caracteres.

## 🚀 Próximos Pasos

1. **Integra un Modelo de IA Real**: Reemplaza las respuestas hardcodeadas con llamadas a OpenAI o Claude
2. **Agrega Persistencia**: Guarda las conversaciones en una base de datos
3. **Crea una Interfaz Web**: Usa Streamlit o Flask para crear una UI
4. **Agrega Más Nodos**: Implementa funcionalidades específicas de tu dominio

## 📚 Recursos Adicionales

- Revisa `ejemplo_langgraph.py` para ver un ejemplo completo
- Consulta `ejemplo_langgraph_avanzado.py` para integración con OpenAI
- Lee `GUIA_RAPIDA.md` para conceptos fundamentales
- Estudia `ARQUITECTURA.md` para patrones de diseño

## 💡 Tips y Trucos

### Debugging
```python
def nodo_con_debug(state):
    print(f"📊 Estado actual: {state}")
    # Tu código aquí
    resultado = {"messages": [AIMessage(content="...")]}
    print(f"📤 Retornando: {resultado}")
    return resultado
```

### Manejo de Errores
```python
def nodo_seguro(state):
    try:
        # Tu código aquí
        return {"messages": [AIMessage(content="...")]}
    except Exception as e:
        return {
            "messages": [AIMessage(content=f"Ups, hubo un error: {e}")]
        }
```

### Testing
```python
def test_nodo_bienvenida():
    estado_prueba = {
        "messages": [HumanMessage(content="Me llamo Juan")],
        "nombre_usuario": ""
    }
    resultado = nodo_bienvenida(estado_prueba)
    assert resultado["nombre_usuario"] == "juan"
    print("✅ Test pasado!")

test_nodo_bienvenida()
```

## ❓ Preguntas Frecuentes

**P: ¿Por qué usar TypedDict en lugar de un diccionario normal?**
R: TypedDict proporciona type hints que ayudan a detectar errores durante el desarrollo y mejoran el autocomplete en el IDE.

**P: ¿Qué pasa si olvido retornar un campo del estado?**
R: No hay problema. Solo retornas los campos que quieres actualizar. Los demás se mantienen sin cambios.

**P: ¿Puedo tener múltiples puntos de entrada?**
R: No directamente, pero puedes crear un nodo "router" que decida a dónde ir basándose en el estado inicial.

**P: ¿Cómo evito loops infinitos?**
R: Asegúrate de que todas las rutas eventualmente lleguen a END. También puedes usar el parámetro `recursion_limit` al compilar.

**P: ¿Puedo usar async/await?**
R: ¡Sí! LangGraph soporta nodos asíncronos. Solo define tus nodos como `async def`.

---

¡Esperamos que este tutorial te haya sido útil! Si tienes preguntas, revisa la documentación oficial de LangGraph o abre un issue en GitHub.

**¡Ahora es tu turno de crear algo increíble! 🚀**
