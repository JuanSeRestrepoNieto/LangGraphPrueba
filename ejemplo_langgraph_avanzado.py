"""
EJEMPLO AVANZADO DE LANGGRAPH CON INTEGRACIÓN DE IA
=====================================================

Este ejemplo demuestra cómo usar LangGraph con modelos de lenguaje reales
para crear un agente conversacional inteligente.

CONCEPTOS ADICIONALES:
- Integración con LangChain y OpenAI
- Uso de herramientas (tools)
- Memoria de conversación
- Manejo de errores

REQUISITOS:
- Configurar OPENAI_API_KEY en archivo .env
"""

import os
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
# from langgraph.prebuilt import ToolExecutor, ToolInvocation  # No needed for this example
from langchain_core.tools import tool
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


# =============================================================================
# PASO 1: DEFINIR HERRAMIENTAS (TOOLS)
# =============================================================================
# Las herramientas son funciones que el agente puede invocar

@tool
def calculadora(operacion: str) -> str:
    """
    Realiza operaciones matemáticas simples.
    
    Args:
        operacion: Expresión matemática como string (ej: "2 + 2", "10 * 5")
        
    Returns:
        Resultado de la operación
    """
    try:
        # ADVERTENCIA: eval() es inseguro en producción
        # Usar solo para propósitos educativos
        resultado = eval(operacion)
        return f"El resultado de {operacion} es {resultado}"
    except Exception as e:
        return f"Error al calcular: {str(e)}"


@tool
def obtener_informacion(tema: str) -> str:
    """
    Proporciona información básica sobre un tema.
    
    Args:
        tema: Tema sobre el que se solicita información
        
    Returns:
        Información sobre el tema
    """
    # Base de conocimientos simple
    conocimientos = {
        "python": "Python es un lenguaje de programación de alto nivel, interpretado y de propósito general.",
        "langgraph": "LangGraph es una biblioteca para construir aplicaciones con múltiples agentes y flujos de trabajo complejos.",
        "ia": "La Inteligencia Artificial es la simulación de procesos de inteligencia humana por parte de máquinas."
    }
    
    tema_lower = tema.lower()
    for clave, info in conocimientos.items():
        if clave in tema_lower:
            return info
    
    return f"No tengo información específica sobre '{tema}', pero puedo ayudarte con otros temas."


# =============================================================================
# PASO 2: DEFINIR EL ESTADO AVANZADO
# =============================================================================

class EstadoAgenteAvanzado(TypedDict):
    """
    Estado del agente con capacidades avanzadas.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    herramientas_disponibles: list
    usar_herramientas: bool


# =============================================================================
# PASO 3: CREAR NODOS CON IA
# =============================================================================

def crear_nodo_agente(llm):
    """
    Crea un nodo que usa un modelo de lenguaje.
    
    Args:
        llm: Modelo de lenguaje a usar
        
    Returns:
        Función de nodo
    """
    def nodo_agente(state: EstadoAgenteAvanzado) -> EstadoAgenteAvanzado:
        """
        Nodo que procesa mensajes con IA.
        """
        print("\n🤖 Ejecutando nodo: AGENTE IA")
        
        # Preparar mensajes con contexto del sistema
        mensajes = [
            SystemMessage(content="""Eres un asistente académico útil. 
            Puedes usar herramientas para realizar cálculos y proporcionar información.
            Si necesitas calcular algo, usa la herramienta 'calculadora'.
            Si necesitas información sobre un tema, usa 'obtener_informacion'.""")
        ] + list(state["messages"])
        
        # Invocar el modelo
        respuesta = llm.invoke(mensajes)
        
        print(f"   Respuesta generada: {respuesta.content[:100]}...")
        
        return {"messages": [respuesta]}
    
    return nodo_agente


def nodo_verificacion(state: EstadoAgenteAvanzado) -> EstadoAgenteAvanzado:
    """
    Nodo que verifica si se necesitan herramientas.
    """
    print("\n🔍 Ejecutando nodo: VERIFICACIÓN")
    
    ultimo_mensaje = state["messages"][-1]
    
    # Verificar si el mensaje contiene solicitudes de herramientas
    contenido = ultimo_mensaje.content.lower()
    
    necesita_herramienta = False
    if any(palabra in contenido for palabra in ["calcula", "suma", "resta", "multiplica", "divide"]):
        necesita_herramienta = True
        print("   ✓ Detectada necesidad de calculadora")
    
    if any(palabra in contenido for palabra in ["qué es", "explica", "información sobre"]):
        necesita_herramienta = True
        print("   ✓ Detectada necesidad de información")
    
    return {"usar_herramientas": necesita_herramienta}


# =============================================================================
# PASO 4: FUNCIÓN DE ENRUTAMIENTO AVANZADO
# =============================================================================

def decidir_continuar(state: EstadoAgenteAvanzado) -> str:
    """
    Decide si continuar procesando o terminar.
    """
    ultimo_mensaje = state["messages"][-1]
    contenido = ultimo_mensaje.content.lower()
    
    # Verificar palabras de despedida
    if any(palabra in contenido for palabra in ["adiós", "chao", "bye", "hasta luego", "terminar"]):
        print("\n⚠️  Detectada despedida - finalizando")
        return "terminar"
    
    # Si hay menos de 10 mensajes, continuar
    if len(state["messages"]) < 10:
        return "continuar"
    
    return "terminar"


# =============================================================================
# PASO 5: CONSTRUIR GRAFO AVANZADO
# =============================================================================

def crear_grafo_avanzado():
    """
    Crea un grafo avanzado con integración de IA.
    
    Returns:
        Grafo compilado
    """
    print("\n📊 Construyendo grafo avanzado...")
    
    # Verificar clave API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "tu-clave-api-aqui":
        print("⚠️  ADVERTENCIA: OPENAI_API_KEY no configurada")
        print("   Este ejemplo funcionará en modo simulado")
        usar_ia_real = False
    else:
        usar_ia_real = True
        print("✓ OPENAI_API_KEY configurada")
    
    # Crear modelo de lenguaje o simulador
    if usar_ia_real:
        try:
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
            print("✓ Modelo GPT-3.5-turbo inicializado")
        except Exception as e:
            print(f"⚠️  Error al inicializar OpenAI: {e}")
            usar_ia_real = False
    
    # Crear grafo
    workflow = StateGraph(EstadoAgenteAvanzado)
    
    # Agregar nodos
    if usar_ia_real:
        workflow.add_node("agente", crear_nodo_agente(llm))
    else:
        # Nodo simulado para cuando no hay API key
        def nodo_simulado(state):
            respuesta = AIMessage(
                content="[MODO SIMULADO] He procesado tu mensaje. "
                        "Configura OPENAI_API_KEY para usar IA real."
            )
            return {"messages": [respuesta]}
        
        workflow.add_node("agente", nodo_simulado)
    
    workflow.add_node("verificacion", nodo_verificacion)
    
    # Definir punto de entrada
    workflow.set_entry_point("agente")
    
    # Agregar aristas condicionales
    workflow.add_conditional_edges(
        "agente",
        decidir_continuar,
        {
            "continuar": "verificacion",
            "terminar": END
        }
    )
    
    # Desde verificación, terminar (en un ejemplo real, aquí ejecutarías herramientas)
    workflow.add_edge("verificacion", END)
    
    # Compilar
    app = workflow.compile()
    
    print("✅ Grafo avanzado construido exitosamente")
    return app


# =============================================================================
# PASO 6: FUNCIÓN PRINCIPAL
# =============================================================================

def ejecutar_ejemplo_avanzado():
    """
    Ejecuta el ejemplo avanzado de LangGraph.
    """
    print("="*70)
    print("  EJEMPLO AVANZADO DE LANGGRAPH CON IA")
    print("="*70)
    
    # Crear grafo
    app = crear_grafo_avanzado()
    
    # Lista de mensajes de prueba
    mensajes_prueba = [
        "Hola, ¿puedes ayudarme?",
        "¿Qué es Python?",
        "Calcula 25 + 17",
        "Gracias, adiós"
    ]
    
    # Estado inicial
    estado = {
        "messages": [],
        "herramientas_disponibles": [calculadora, obtener_informacion],
        "usar_herramientas": False
    }
    
    # Ejecutar conversación
    for i, mensaje in enumerate(mensajes_prueba, 1):
        print("\n" + "="*70)
        print(f"  INTERACCIÓN {i}")
        print("="*70)
        print(f"👤 Usuario: {mensaje}")
        
        # Agregar mensaje del usuario
        estado["messages"].append(HumanMessage(content=mensaje))
        
        # Ejecutar grafo
        try:
            estado = app.invoke(estado)
            
            # Mostrar respuesta del agente
            if estado["messages"]:
                ultima_respuesta = estado["messages"][-1]
                if isinstance(ultima_respuesta, AIMessage):
                    print(f"🤖 Agente: {ultima_respuesta.content}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            break
    
    print("\n" + "="*70)
    print("  EJEMPLO AVANZADO COMPLETADO")
    print("="*70)
    print(f"\nTotal de mensajes intercambiados: {len(estado['messages'])}")


# =============================================================================
# MODO INTERACTIVO
# =============================================================================

def modo_interactivo():
    """
    Modo interactivo para chatear con el agente.
    """
    print("="*70)
    print("  MODO INTERACTIVO DE LANGGRAPH")
    print("="*70)
    print("\nEscribe 'salir' para terminar\n")
    
    # Crear grafo
    app = crear_grafo_avanzado()
    
    # Estado inicial
    estado = {
        "messages": [],
        "herramientas_disponibles": [calculadora, obtener_informacion],
        "usar_herramientas": False
    }
    
    while True:
        # Obtener entrada del usuario
        entrada = input("👤 Tú: ").strip()
        
        if not entrada:
            continue
        
        if entrada.lower() in ["salir", "exit", "quit"]:
            print("\n👋 ¡Hasta luego!")
            break
        
        # Agregar mensaje
        estado["messages"].append(HumanMessage(content=entrada))
        
        # Ejecutar grafo
        try:
            estado = app.invoke(estado)
            
            # Mostrar respuesta
            if estado["messages"]:
                ultima_respuesta = estado["messages"][-1]
                if isinstance(ultima_respuesta, AIMessage):
                    print(f"🤖 Agente: {ultima_respuesta.content}\n")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")


# =============================================================================
# EJECUCIÓN
# =============================================================================

if __name__ == "__main__":
    """
    Este ejemplo avanzado demuestra:
    
    1. Integración con modelos de lenguaje (OpenAI GPT)
    2. Uso de herramientas personalizadas
    3. Manejo de estado complejo
    4. Enrutamiento condicional avanzado
    5. Modo interactivo para conversación en tiempo real
    
    Para usar con IA real:
    1. Crea un archivo .env
    2. Agrega: OPENAI_API_KEY=tu-clave-real
    3. Ejecuta el script
    
    Sin API key, el ejemplo funciona en modo simulado.
    """
    
    # Ejecutar ejemplo programático
    ejecutar_ejemplo_avanzado()
    
    # Descomentar para modo interactivo:
    # modo_interactivo()
