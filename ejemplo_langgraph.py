"""
EJEMPLO ACADÉMICO DE LANGGRAPH
================================

Este ejemplo demuestra cómo usar LangGraph para crear un agente conversacional
con estados y flujos de trabajo definidos.

CONCEPTOS CLAVE:
- Estados (State): Representan el contexto y datos del agente
- Nodos (Nodes): Funciones que procesan y transforman el estado
- Grafos (Graphs): Definen el flujo de ejecución entre nodos
- Aristas (Edges): Conectan nodos y determinan el flujo

PASO A PASO:
1. Definir el estado del agente
2. Crear nodos de procesamiento
3. Construir el grafo
4. Compilar y ejecutar
"""

import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# =============================================================================
# PASO 1: DEFINIR EL ESTADO DEL AGENTE
# =============================================================================
# El estado mantiene toda la información que fluye a través del grafo.
# Usamos TypedDict para definir la estructura del estado.

class EstadoAgente(TypedDict):
    """
    Estado del agente que contiene:
    - messages: Lista de mensajes en la conversación
    - contador: Contador de interacciones (ejemplo de dato adicional)
    """
    # Annotated permite usar funciones reductoras para combinar valores
    # add_messages concatena los mensajes nuevos con los existentes
    messages: Annotated[Sequence[BaseMessage], add_messages]
    contador: int


# =============================================================================
# PASO 2: CREAR NODOS DE PROCESAMIENTO
# =============================================================================
# Los nodos son funciones que reciben el estado y lo transforman.
# Cada nodo representa una operación específica en el flujo.

def nodo_saludo(state: EstadoAgente) -> EstadoAgente:
    """
    Nodo que procesa el saludo inicial.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con el mensaje de saludo
    """
    print("\n🔵 Ejecutando nodo: SALUDO")
    
    # Obtener el último mensaje del usuario
    ultimo_mensaje = state["messages"][-1].content
    
    # Crear respuesta
    respuesta = AIMessage(
        content=f"¡Hola! Veo que dijiste: '{ultimo_mensaje}'. "
                f"Esta es la interacción #{state.get('contador', 0) + 1}. "
                f"¿En qué puedo ayudarte hoy?"
    )
    
    # Retornar el estado actualizado
    return {
        "messages": [respuesta],
        "contador": state.get("contador", 0) + 1
    }


def nodo_procesamiento(state: EstadoAgente) -> EstadoAgente:
    """
    Nodo que procesa consultas generales.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con la respuesta procesada
    """
    print("\n🟢 Ejecutando nodo: PROCESAMIENTO")
    
    # Obtener el último mensaje
    ultimo_mensaje = state["messages"][-1].content.lower()
    
    # Lógica de procesamiento simple
    if "ayuda" in ultimo_mensaje:
        respuesta_texto = "Puedo ayudarte con información básica. Pregúntame lo que necesites."
    elif "gracias" in ultimo_mensaje or "adiós" in ultimo_mensaje:
        respuesta_texto = "¡De nada! Fue un placer ayudarte. ¡Hasta pronto!"
    else:
        respuesta_texto = f"He procesado tu mensaje. Interacción #{state['contador']}. " \
                          f"Total de mensajes: {len(state['messages'])}"
    
    respuesta = AIMessage(content=respuesta_texto)
    
    return {
        "messages": [respuesta],
        "contador": state["contador"] + 1
    }


def nodo_despedida(state: EstadoAgente) -> EstadoAgente:
    """
    Nodo que maneja la despedida.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Estado actualizado con mensaje de despedida
    """
    print("\n🔴 Ejecutando nodo: DESPEDIDA")
    
    respuesta = AIMessage(
        content=f"¡Hasta luego! Tuvimos {state['contador']} interacciones. "
                f"¡Que tengas un excelente día!"
    )
    
    return {"messages": [respuesta]}


# =============================================================================
# PASO 3: FUNCIÓN DE ENRUTAMIENTO
# =============================================================================
# Determina qué nodo ejecutar a continuación basándose en el estado actual.

def decidir_siguiente_nodo(state: EstadoAgente) -> str:
    """
    Función que decide el siguiente nodo a ejecutar.
    
    Args:
        state: Estado actual del agente
        
    Returns:
        Nombre del siguiente nodo a ejecutar o END
    """
    # Obtener el último mensaje (puede ser del usuario o del agente)
    mensajes = state["messages"]
    if not mensajes:
        return END
    
    # Buscar el último mensaje del usuario (HumanMessage)
    ultimo_mensaje_usuario = None
    for msg in reversed(mensajes):
        if isinstance(msg, HumanMessage):
            ultimo_mensaje_usuario = msg.content.lower()
            break
    
    if not ultimo_mensaje_usuario:
        return END
    
    # Lógica de decisión
    if any(palabra in ultimo_mensaje_usuario for palabra in ["adiós", "chao", "bye", "hasta luego"]):
        return "despedida"
    else:
        return END


# =============================================================================
# PASO 4: CONSTRUIR EL GRAFO
# =============================================================================
# El grafo define el flujo de ejecución entre nodos.

def crear_grafo():
    """
    Crea y configura el grafo de LangGraph.
    
    Returns:
        Grafo compilado listo para ejecutar
    """
    print("\n📊 Construyendo el grafo...")
    
    # Crear el grafo con el estado definido
    workflow = StateGraph(EstadoAgente)
    
    # Agregar nodos al grafo
    workflow.add_node("saludo", nodo_saludo)
    workflow.add_node("procesamiento", nodo_procesamiento)
    workflow.add_node("despedida", nodo_despedida)
    
    # Definir el punto de entrada
    # set_entry_point establece desde dónde comienza el flujo
    workflow.set_entry_point("saludo")
    
    # Desde "saludo", siempre va a "procesamiento"
    workflow.add_edge("saludo", "procesamiento")
    
    # Desde "procesamiento", decide si ir a despedida o terminar
    workflow.add_conditional_edges(
        "procesamiento",
        decidir_siguiente_nodo,
        {
            "despedida": "despedida",
            END: END
        }
    )
    
    # Desde "despedida", siempre termina
    workflow.add_edge("despedida", END)
    
    # Compilar el grafo
    app = workflow.compile()
    
    print("✅ Grafo construido exitosamente")
    return app


# =============================================================================
# PASO 5: FUNCIÓN PRINCIPAL DE EJECUCIÓN
# =============================================================================

def ejecutar_ejemplo():
    """
    Función principal que ejecuta el ejemplo de LangGraph.
    """
    print("="*70)
    print("  EJEMPLO ACADÉMICO DE LANGGRAPH")
    print("="*70)
    
    # Crear el grafo
    app = crear_grafo()
    
    # Estado inicial
    estado_inicial = {
        "messages": [HumanMessage(content="Hola")],
        "contador": 0
    }
    
    print("\n🚀 Ejecutando el grafo con estado inicial...")
    print(f"   Mensaje inicial: '{estado_inicial['messages'][0].content}'")
    
    # Ejecutar el grafo
    resultado = app.invoke(estado_inicial)
    
    print("\n" + "="*70)
    print("  RESULTADO FINAL")
    print("="*70)
    print(f"Total de mensajes: {len(resultado['messages'])}")
    print(f"Contador de interacciones: {resultado['contador']}")
    print("\nConversación completa:")
    print("-"*70)
    for i, msg in enumerate(resultado["messages"], 1):
        tipo = "Usuario" if isinstance(msg, HumanMessage) else "Agente"
        print(f"{i}. [{tipo}]: {msg.content}")
    
    # Ejemplo de interacción adicional
    print("\n" + "="*70)
    print("  SEGUNDA INTERACCIÓN")
    print("="*70)
    
    # Agregar un nuevo mensaje al estado existente
    resultado["messages"].append(HumanMessage(content="Necesito ayuda"))
    
    # Ejecutar de nuevo
    resultado2 = app.invoke(resultado)
    
    print("\nNueva conversación:")
    print("-"*70)
    for i, msg in enumerate(resultado2["messages"], 1):
        tipo = "Usuario" if isinstance(msg, HumanMessage) else "Agente"
        print(f"{i}. [{tipo}]: {msg.content}")
    
    # Ejemplo final con despedida
    print("\n" + "="*70)
    print("  TERCERA INTERACCIÓN - DESPEDIDA")
    print("="*70)
    
    resultado2["messages"].append(HumanMessage(content="Adiós, gracias"))
    resultado3 = app.invoke(resultado2)
    
    print("\nConversación final:")
    print("-"*70)
    for i, msg in enumerate(resultado3["messages"], 1):
        tipo = "Usuario" if isinstance(msg, HumanMessage) else "Agente"
        print(f"{i}. [{tipo}]: {msg.content}")
    
    print("\n" + "="*70)
    print("  EJEMPLO COMPLETADO")
    print("="*70)


# =============================================================================
# EJECUCIÓN DEL EJEMPLO
# =============================================================================

if __name__ == "__main__":
    """
    Punto de entrada del programa.
    
    Este ejemplo demuestra:
    1. Cómo definir estados en LangGraph
    2. Cómo crear nodos de procesamiento
    3. Cómo conectar nodos con aristas
    4. Cómo usar aristas condicionales
    5. Cómo ejecutar el grafo con diferentes estados
    
    NOTA: Este es un ejemplo educativo simplificado.
    En producción, integrarías modelos de IA reales (como GPT-4)
    para generar respuestas más inteligentes.
    """
    ejecutar_ejemplo()
