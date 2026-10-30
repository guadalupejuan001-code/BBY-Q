// F002: original educational definitions; none describe private accounts.
export const additionalRows=`
economia unitaria|analisis de ingresos y costes atribuibles a una unidad de negocio|definir la unidad y separar costes variables de costes fijos
margen incremental|resultado adicional causado por una venta o decision adicional|comparar ingresos y costes que realmente cambian
reinversion|uso de recursos obtenidos para financiar nuevas actividades|comparar rendimiento esperado liquidez y necesidades pendientes
capital de trabajo|diferencia entre activos corrientes y pasivos corrientes|usar una misma fecha y examinar cuando se cobra y se paga
consumo neto de caja|salida neta de efectivo durante un periodo definido|medir cobros y pagos reales del mismo periodo
autonomia de caja|tiempo estimado que cubre el efectivo bajo un consumo neto supuesto|declarar el supuesto de consumo y los cambios previsibles
conciliacion|comparacion de registros para identificar diferencias y duplicados|usar identificadores fechas importes y fuentes originales
cuenta por cobrar|importe pendiente de cobro a un cliente|verificar vencimiento posibilidad de cobro y soporte documental
cuenta por pagar|importe pendiente de pago a un proveedor|registrar vencimiento moneda y condiciones
inventario|bienes mantenidos para venta o uso en una actividad|medir unidades coste deterioro y tiempo de reposicion
rotacion de inventario|medida de renovacion del inventario durante un periodo|declarar formula periodo y criterio de valoracion
reserva para impuestos|dinero apartado para obligaciones tributarias estimadas|verificar reglas vigentes y situacion aplicable antes de calcular
moneda de referencia|unidad monetaria elegida para presentar una comparacion|declarar conversiones fuente fecha y costes de cambio
tipo de cambio|precio de una moneda expresado en otra|indicar par direccion fecha y cargos aplicables
resultado realizado|ganancia o perdida reconocida tras cerrar una operacion segun el criterio usado|distinguir efectivo recibido coste comisiones e impuestos
resultado no realizado|cambio de valor de una posicion que sigue abierta|usar una valoracion fechada sin confundirla con dinero cobrado
rentabilidad anualizada|expresion anual equivalente de un rendimiento observado|especificar plazo metodo y no presentarla como pronostico
crecimiento compuesto|acumulacion multiplicativa de cambios sucesivos sobre una base|usar tasas y periodos consistentes sin garantizar su continuidad
promedio ponderado|media calculada asignando un peso a cada observacion|normalizar pesos e identificar que representa cada uno
valor esperado|suma de resultados multiplicados por sus probabilidades supuestas|documentar probabilidades perdidas posibles y limitaciones
concentracion|dependencia elevada de una posicion cliente o fuente de ingresos|medir exposiciones comunes y escenarios adversos
riesgo de liquidez|posibilidad de no convertir una posicion en efectivo en condiciones aceptables|evaluar plazos volumen y costes de salida
riesgo de contraparte|posibilidad de que otra parte incumpla sus obligaciones|verificar compromisos solvencia y condiciones de recuperacion
riesgo operativo|posibilidad de perdidas por fallos de procesos personas o sistemas|registrar incidentes controles y formas de detener operaciones
sesgo de supervivencia|error de analizar solo casos que permanecieron o tuvieron exito|incluir fracasos salidas y datos ausentes relevantes
fuga de informacion futura|uso en una prueba de datos que no estaban disponibles al decidir|ordenar datos por disponibilidad real y respetar cortes temporales
prueba fuera de muestra|evaluacion con datos no utilizados para ajustar el sistema|separar ajuste seleccion y examen final
prueba progresiva temporal|evaluacion que ajusta con pasado y prueba en periodos posteriores|fijar ventanas y conservar resultados sin seleccionar solo aciertos
registro de predicciones|archivo fechado de pronosticos emitidos antes de conocer resultados|guardar horizonte valor incertidumbre y criterio de evaluacion
calibracion probabilistica|correspondencia entre probabilidades declaradas y frecuencias observadas|usar suficientes casos comparables y evitar evaluar solo aciertos
tasa de acierto|fraccion de resultados clasificados como correctos bajo una regla|definir acierto muestra y periodo sin confundirlo con beneficio
error absoluto|magnitud de la diferencia entre una estimacion y su resultado|usar unidades comparables y conservar tambien los errores grandes
comparacion de referencia|contraste de un sistema con una alternativa claramente definida|usar los mismos datos costes horizontes y reglas de evaluacion
simulacion en papel|registro de operaciones hipoteticas sin enviar ordenes reales|incluir costes deslizamiento y restricciones de ejecucion
regla de parada|condicion predefinida para detener un experimento|definir umbral medicion y responsable sin modificarlo tras perder
idempotencia|propiedad de no duplicar un efecto al repetir una misma solicitud|identificar cada operacion y comprobar su resultado previo
limite de exposicion|restriccion sobre los recursos comprometidos en una actividad|definir importe alcance vigencia y quien puede modificarlo
registro de autorizacion|evidencia de permiso para una accion delimitada|conservar alcance importe destino fecha y posibilidad de revocacion
presupuesto experimental|cantidad y recursos destinados a probar una hipotesis|separar el ensayo de obligaciones y medir coste total
resultado verificable|afirmacion respaldada por registros que pueden revisarse|mostrar datos metodo fecha y condiciones de la medicion
cliente objetivo|grupo concreto al que se dirige una oferta|identificar una necesidad y comprobar disposicion a pagar
problema del cliente|dificultad o necesidad que una oferta pretende resolver|contrastar su importancia con personas del grupo elegido
segmentacion|division de un mercado en grupos relevantes para una oferta|usar criterios pertinentes y datos obtenidos con permiso
canal de distribucion|medio por el que una oferta llega a sus compradores|medir alcance costes control y conversion
canal de adquisicion|medio por el que se consiguen posibles clientes|medir coste calidad y resultados atribuibles
embudo comercial|secuencia definida desde el contacto hasta una accion comercial|contar pasos abandonos y conversiones con el mismo criterio
oferta piloto|version limitada de una propuesta para probar su utilidad comercial|definir entregable precio condiciones y evidencia buscada
demostracion de producto|presentacion comprobable de una funcion del producto|mostrar condiciones reales y distinguir prototipo de version disponible
venta de servicios|obtencion de ingresos por trabajo o resultados acordados|estimar alcance horas costes y criterios de aceptacion
licencia de software|permiso de uso de un programa bajo condiciones definidas|verificar derechos alcance distribucion soporte y precio
soporte de software|atencion de incidencias y dudas sobre un programa|definir cobertura horarios coste y responsabilidades
coste de mantenimiento|recursos necesarios para conservar una funcion o servicio|incluir actualizaciones soporte infraestructura y pruebas
ingreso recurrente|ingreso que se repite bajo una relacion o mecanismo definido|medir continuidad cancelaciones costes y cumplimiento
venta adicional|oferta de una mejora o ampliacion al cliente|mostrar utilidad precio y opcion real de rechazarla
venta complementaria|oferta de otro producto relacionado con una compra|comprobar pertinencia y comunicar el coste total
precio basado en valor|precio orientado por la utilidad percibida de la oferta|contrastar disposicion a pagar alternativas y costes
precio basado en costes|precio construido desde costes y un incremento definido|comprobar demanda y distinguir margen de recargo
prueba de precios|experimento para comparar respuestas a precios definidos|mantener condiciones comparables y registrar margen no solo ventas
sensibilidad al precio|grado en que cambia una respuesta ante cambios de precio|definir contexto medida y alternativas disponibles
cohorte de clientes|grupo que comparte un criterio de entrada o caracteristica temporal|comparar grupos con definiciones y periodos consistentes
beneficio por hora|resultado economico dividido entre horas consideradas|incluir trabajo de soporte preparacion y mantenimiento
capacidad de entrega|volumen que puede atenderse con recursos y calidad definidos|medir tiempo errores cuellos de botella y coste adicional
cuello de botella|recurso o etapa que restringe el flujo del proceso|medir capacidad y comprobar que la restriccion es real
producto minimo comprobable|version acotada que permite demostrar una utilidad concreta|elegir una funcion verificable y criterios de aceptacion
prueba de rendimiento|medicion del comportamiento de un sistema bajo condiciones definidas|registrar dispositivo carga version metodo y repeticiones
ventaja tecnica demostrada|mejora observada frente a una referencia comparable|comparar la misma tarea y publicar tambien limitaciones
monetizar xi|probar ingresos por herramientas servicios o licencias basados en XI|demostrar utilidad estabilidad derechos y coste de soporte
monetizar ether|probar una oferta basada en funciones verificadas de Ether|medir beneficio para un comprador sin prometer recursos ilimitados
monetizar laplace|evaluar una oferta de analisis basada en resultados comprobables de Laplace|separar predicciones simulaciones y operaciones sin garantizar ganancias
objetivo economico de bby q|aprender a explicar evaluar y posteriormente asistir en decisiones sobre dinero|superar pruebas separadas antes de ampliar permisos
papel de w4u|coordinar y verificar tareas dentro de la arquitectura definida por el operador|respetar permisos y distinguir tareas propuestas de tareas ejecutadas
papel de qdu|modulo de programacion subordinado a BBY Q y coordinado por w4U|probar codigo y entregar evidencia sin convertirse en otra IA principal
prediccion a quince minutos|estimacion cuyo horizonte termina quince minutos despues del instante definido|guardar hora inicial fuente resultado y errores antes de recalibrar
validar laplace|comparar predicciones previas de Laplace con resultados posteriores|conservar fallos y aciertos fuera de datos usados para ajustarlo
farmear mi tecnologia|buscar ingresos repetibles a partir de productos o servicios propios|elegir una funcion demostrada un comprador y costes verificables
mas datos de entrenamiento|ampliacion del material disponible para enseñar al modelo|distinguir ejemplos preparados ejemplos consumidos y pruebas superadas
conocimiento incorporado|informacion que el modelo puede recuperar tras una adquisicion comprobada|probar consulta retencion y ausencia de cambios no deseados
capacidad conversacional|habilidad de interpretar y responder dentro de un conjunto de situaciones|probar variantes contexto correcciones y casos no enseñados
precio actual|cotizacion correspondiente a un momento y una fuente identificados|consultar una fuente vigente y no inventar datos desde el entrenamiento
permiso para aprender|autorizacion para incorporar o comprobar conocimiento|no confundirlo con permiso para gastar transferir o invertir
`.trim().split('\n').map((line,i)=>{const [term,definition,requirement]=line.split('|');return {id:`f002-${String(i+1).padStart(3,'0')}`,term,definition,requirement};});

// Designed syntax support, NOT a claim of induced language understanding.
export const fillers=['oye ','pz ','pues ','mira ','esk ','es que '];
export const prefixes=[
 ['quiero saber que requiere ','que requiere '],['quiero saber que es ','que es '],
 ['que necesito para ','que requiere '],['necesito entender ','que es '],
 ['que significa ','que es '],['no entiendo ','que es '],
 ['explicame ','que es '],['explica ','que es '],['hablame de ','que es '],
 ['que requiere ','que requiere '],['que es ','que es ']
];
export const intentAliases=[
 ['quiero farmear dinero','que requiere farmear dinero'],
 ['quiero poner mi dinero a trabajar','que requiere poner dinero a trabajar'],
 ['como monetizo reverse','que requiere monetizar reverse'],
 ['como le saco dinero a reverse','que requiere monetizar reverse'],
 ['como monetizo bby q','que requiere monetizar bby q'],
 ['como monetizo mi renderizador','que requiere monetizar un renderizador'],
 ['como monetizo xi','que requiere monetizar xi'],
 ['como monetizo ether','que requiere monetizar ether'],
 ['como monetizo laplace','que requiere monetizar laplace'],
 ['quiero farmear mi tecnologia','que requiere farmear mi tecnologia'],
 ['como valido laplace','que requiere validar laplace']
];
export const extraSources=[
 {id:'sba-demand',url:'https://www.sba.gov/counseling/plan-your-business/',scope:'Demanda, alternativas, precios e investigacion de mercado; contenido redactado, no copiado.'},
 {id:'sec-fees',url:'https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/updated',scope:'Considerar costes de transaccion y costes recurrentes al evaluar resultados.'},
 {id:'operator-architecture',scope:'Roles declarados por el operador: BBY Q -> w4U -> QdU. No acredita capacidades o ingresos existentes.'},
 {id:'f002-author',scope:'Definiciones y ejemplos originales; sintaxis diseñada y acotada. No incluye cuentas, biometria, perfiles de vulnerabilidad ni cotizaciones actuales.'}
];
