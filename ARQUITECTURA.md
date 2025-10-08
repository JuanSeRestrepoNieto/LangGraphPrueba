# Arquitectura de los Ejemplos de LangGraph

## Diagrama: Ejemplo Básico

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRADA USUARIO                           │
│                    HumanMessage("Hola")                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  NODO: SALUDO  │
                    │                │
                    │ - Procesa      │
                    │   mensaje      │
                    │ - Incrementa   │
                    │   contador     │
                    │ - Genera       │
                    │   respuesta    │
                    └───────┬────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ NODO:            │
                  │ PROCESAMIENTO    │
                  │                  │
                  │ - Analiza mensaje│
                  │ - Detecta ayuda, │
                  │   despedida, etc │
                  │ - Genera         │
                  │   respuesta      │
                  └────────┬─────────┘
                           │
                           ▼
                  ┌────────────────────┐
                  │   DECISIÓN:        │
                  │ ¿Es despedida?     │
                  └───┬────────────┬───┘
                      │            │
               Sí ────┘            └──── No
                      │                  │
                      ▼                  ▼
            ┌──────────────────┐    ┌─────┐
            │ NODO: DESPEDIDA  │    │ END │
            │                  │    └─────┘
            │ - Mensaje final  │
            │ - Resumen de     │
            │   interacciones  │
            └────────┬─────────┘
                     │
                     ▼
                  ┌─────┐
                  │ END │
                  └─────┘
```

## Diagrama: Ejemplo Avanzado

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRADA USUARIO                           │
│              HumanMessage("Calcula 25 + 17")                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │   NODO: AGENTE IA     │
                  │                       │
                  │ Con API Key:          │
                  │ ├─ OpenAI GPT-3.5     │
                  │ └─ Genera respuesta   │
                  │    inteligente        │
                  │                       │
                  │ Sin API Key:          │
                  │ └─ Respuesta simulada │
                  └──────────┬────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │    DECISIÓN:         │
                  │ ¿Es despedida?       │
                  └───┬──────────────┬───┘
                      │              │
               Sí ────┘              └──── No
                      │                    │
                      ▼                    ▼
                  ┌─────┐       ┌──────────────────┐
                  │ END │       │ NODO:            │
                  └─────┘       │ VERIFICACIÓN     │
                                │                  │
                                │ - Analiza si     │
                                │   necesita       │
                                │   herramientas   │
                                │                  │
                                │ Detecta:         │
                                │ ├─ Cálculos      │
                                │ ├─ Información   │
                                │ └─ Otros         │
                                └────────┬─────────┘
                                         │
                                         ▼
                                     ┌─────┐
                                     │ END │
                                     └─────┘
```

## Flujo de Estados

### Estado en Ejemplo Básico

```python
Estado = {
    "messages": [
        HumanMessage("Hola"),
        AIMessage("¡Hola! Veo que dijiste..."),
        # ... más mensajes
    ],
    "contador": 2  # Número de interacciones
}
```

### Estado en Ejemplo Avanzado

```python
EstadoAvanzado = {
    "messages": [
        HumanMessage("Calcula 25 + 17"),
        AIMessage("El resultado es 42"),
        # ... más mensajes
    ],
    "herramientas_disponibles": [
        calculadora,
        obtener_informacion
    ],
    "usar_herramientas": False  # o True si se detecta necesidad
}
```

## Ciclo de Vida de una Ejecución

```
1. INICIO
   ├─ Se crea estado inicial con mensaje del usuario
   └─ Estado: {"messages": [HumanMessage], "contador": 0}
   
2. ENTRADA AL GRAFO
   ├─ Se invoca app.invoke(estado_inicial)
   └─ Se comienza desde el entry_point definido
   
3. EJECUCIÓN DE NODOS
   ├─ Cada nodo recibe el estado completo
   ├─ Procesa la información
   ├─ Retorna actualizaciones parciales
   └─ LangGraph merge las actualizaciones al estado
   
4. NAVEGACIÓN ENTRE NODOS
   ├─ Si hay arista directa → ir al siguiente nodo
   ├─ Si hay arista condicional → evaluar función
   └─ Si es END → terminar ejecución
   
5. FINALIZACIÓN
   ├─ Se alcanza END
   ├─ Se retorna el estado final completo
   └─ Estado final contiene toda la conversación
```

## Comparación de Enfoques

### Enfoque Tradicional (sin LangGraph)

```python
# Código imperativo difícil de mantener
def procesar_mensaje(mensaje):
    if "hola" in mensaje.lower():
        respuesta = saludar()
        if necesita_ayuda(respuesta):
            respuesta = dar_ayuda()
            if quiere_salir(respuesta):
                return despedirse()
            else:
                return procesar_mensaje(nueva_entrada())
    # ... más ifs anidados
    return respuesta
```

**Problemas:**
- ❌ Difícil de seguir
- ❌ Difícil de probar
- ❌ Difícil de modificar
- ❌ Estado implícito

### Enfoque con LangGraph

```python
# Código declarativo fácil de entender
workflow = StateGraph(Estado)
workflow.add_node("saludo", nodo_saludo)
workflow.add_node("ayuda", nodo_ayuda)
workflow.add_node("despedida", nodo_despedida)

workflow.set_entry_point("saludo")
workflow.add_conditional_edges("saludo", decidir_siguiente)
workflow.add_edge("despedida", END)

app = workflow.compile()
```

**Ventajas:**
- ✅ Estructura clara
- ✅ Fácil de probar cada nodo
- ✅ Fácil de modificar el flujo
- ✅ Estado explícito

## Patrones de Diseño

### Patrón 1: Pipeline Secuencial

**Uso:** Cuando necesitas procesar datos en pasos ordenados.

```
Entrada → Validar → Procesar → Formatear → Salida
```

**Ejemplo:** Sistema de validación de formularios

### Patrón 2: Árbol de Decisión

**Uso:** Cuando el flujo depende de múltiples condiciones.

```
             ┌─→ Ruta A → Resultado A
Entrada → ┬──┼─→ Ruta B → Resultado B
          └──┼─→ Ruta C → Resultado C
             └─→ Ruta D → Resultado D
```

**Ejemplo:** Clasificación de tickets de soporte

### Patrón 3: Loop con Acumulación

**Uso:** Cuando necesitas iterar hasta cumplir una condición.

```
Entrada → Procesar → ¿Suficiente? → No → Acumular → Volver
                          ↓
                         Sí
                          ↓
                       Salida
```

**Ejemplo:** Búsqueda iterativa de información

### Patrón 4: Multi-Agente

**Uso:** Cuando diferentes agentes manejan diferentes tareas.

```
Entrada → Coordinador → ┬─→ Agente A (Búsqueda)
                        ├─→ Agente B (Análisis)
                        └─→ Agente C (Síntesis)
                              ↓
                         Combinador → Salida
```

**Ejemplo:** Sistema de investigación automatizado

## Mejores Prácticas de Arquitectura

### 1. Separación de Responsabilidades

```python
# ✅ BIEN: Nodos especializados
def validar_entrada(state):
    # Solo valida
    return {"valido": es_valido(state["entrada"])}

def procesar_datos(state):
    # Solo procesa
    return {"resultado": procesar(state["entrada"])}

# ❌ MAL: Nodo que hace todo
def hacer_todo(state):
    # Valida, procesa, formatea, guarda...
    pass
```

### 2. Estado Inmutable

```python
# ✅ BIEN: Retornar nuevo estado
def nodo(state):
    nuevo_valor = calcular(state["valor"])
    return {"valor": nuevo_valor}

# ❌ MAL: Modificar estado directamente
def nodo(state):
    state["valor"] = calcular(state["valor"])
    return state
```

### 3. Manejo de Errores

```python
# ✅ BIEN: Capturar errores en el estado
def nodo_seguro(state):
    try:
        resultado = operacion_riesgosa(state)
        return {"resultado": resultado, "error": None}
    except Exception as e:
        return {"resultado": None, "error": str(e)}

# Luego decidir basándose en el error
def decidir(state):
    if state["error"]:
        return "manejar_error"
    return "continuar"
```

### 4. Testabilidad

```python
# ✅ BIEN: Nodos testables independientemente
def nodo_calculadora(state):
    a = state["a"]
    b = state["b"]
    return {"resultado": a + b}

# Test
def test_calculadora():
    resultado = nodo_calculadora({"a": 2, "b": 3})
    assert resultado["resultado"] == 5
```

## Escalabilidad

### Ejemplo Pequeño (< 5 nodos)
```
Entrada → Procesar → Salida
```
**Uso:** Tareas simples, flujos lineales

### Ejemplo Mediano (5-15 nodos)
```
          ┌→ Rama A → Sub-A →┐
Entrada → ┼→ Rama B → Sub-B →┼→ Combinar → Salida
          └→ Rama C → Sub-C →┘
```
**Uso:** Aplicaciones empresariales

### Ejemplo Grande (> 15 nodos)
```
                    ┌→ Sistema A (subgrafo) →┐
Entrada → Router → ┼→ Sistema B (subgrafo) →┼→ Orquestador → Salida
                    └→ Sistema C (subgrafo) →┘
```
**Uso:** Sistemas distribuidos, multi-agente

## Recursos de Computación

| Tipo de Ejemplo | RAM Aprox. | Tiempo Ejecución | Costo API |
|-----------------|------------|------------------|-----------|
| Básico          | < 100 MB   | < 1 segundo      | $0        |
| Avanzado (sin API) | < 150 MB | < 1 segundo    | $0        |
| Avanzado (con GPT-3.5) | < 200 MB | 1-3 segundos | ~$0.001/request |
| Avanzado (con GPT-4) | < 200 MB | 3-10 segundos | ~$0.03/request |

## Conclusión

LangGraph proporciona una forma estructurada y escalable de construir aplicaciones con IA. La arquitectura modular permite:

- 🔄 Flujos complejos fáciles de entender
- 🧪 Testing granular de componentes
- 🔧 Mantenimiento simplificado
- 📈 Escalabilidad progresiva
- 🎯 Depuración efectiva

Usa los diagramas y patrones de esta guía como referencia para diseñar tus propios sistemas.
