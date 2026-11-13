**************************************************************************
**************************** EJECUCIÓN ***********************************
**************************************************************************

Ejecutar estos comandos para iniciar el sistema:

    docker compose down
    docker compose up --build -d

En una terminal a parte se recomienda lanzar el siguiente comando para ver los logs:

    docker compose logs -f calc1 calc2 calc3 calc4 calc5

Una vez aparezca un log en el que se vea como una de las calculadoras se erija como líder, 
se pueden lanzar ya comandos como los contenidos en el archivo script.txt o bien si se prefiere, 
lanzar dicho script completo:

    ./script.txt

Las posibles peticiones que se pueden ejecutar pueden ser de cuatro variantes:

    - Una petición aritmética.
    - Un get para obtener la información de una calculadora concreta.
    - Un reset para reiniciar el valor de una calculadora concreta.
    - Una consulta de las métricas recogidas por cada nodo.

Se recomienda ver el contenido de script.txt para ver el formato de cada tipo de petición si no se 
quiere lanzar el script completo.


**************************************************************************
****************** DETALLES DE LA IMPLEMENTACIÓN *************************
***************************** Y ******************************************
***************** CRITÉRIOS DE REDIRECCIONAMIENTO ************************
**************************************************************************

En primer lugar en esta práctica se ha empleado el servidor RESTFUL implementado en la anterior práctica
como el servidor calculadora alojado en cada nodo (calc1, calc2, calc3, calc3, calc4, calc5). Por otro lado 
se ha decidido emplear Zookeeper para la elección del líder, siguiendo el ejemplo facilitado por el profesor.

Con esto en cuenta podemos pasar a la explicación de la implementación, en condiciones normales se dispone de un nodo
calcX que desempeña el rol de líder, esto significa que cualquier petición debe pasar por el líder, en caso de que dicha 
petición le llegue directamente a su puerto (ej: se envía al puerto 5001 siendo calc1 el líder) gestionará a qué nodo 
calculadora enviar la petición según un criterio explicado más adelante, si por otro lado se envía la petición a un nodo no 
líder, este reenviará la petición al líder para que la gestione. De esta manera siempre es el líder quien gestiona las 
peticiones del cliente.

El sitema de balanceo consiste en que cada nodo calculadora es responsable de un conjunto de calculadoras, su asignación viene
dada por el identificador de calculadora al que se hace referencia, la fómula empleada es (calculadora_id % 5) + 1, de manera 
que dicha fórmula nos devuelva un valor entre 1 y 5, el cual representa el identificador del nodo calculadora que será responsable 
de su gestión. Así cada nodo calculadora es responsable de un subconjunto de calculadoras.

La razón de aplicar esta asignación ha sido principalmente para evitar que cada nodo calculadora pudiera tener su propia versión 
diferente de calculadoras con el mismo identificador.

PROS de esta implementación:

    - Se aprovecha el nodo líder no solamente para gestionar las peticiones, sino tambien para el computo de las mismas si estas 
      le corresponden, ya que hay que recalcar que el nodo líder puede tener signadas calculadoras como el resto de nodos.
    
    - El uso de Zookeeper para la elección de liderazgo permite una distribución de liderazgos sencilla de aplicar y que acaba siendo 
      equitativa para todos los nodos.

    - Con un reparto equitativo de los liderazgos se intenta simular un reparto de la sobrecarga distribuido entre todos los nodos, lo cual 
      es un enfoque más verosímil de cara a evitar el descaste más pronunciado en un nodo del sistema que en otros.

CONTRAS de esta implementación:

    - En caso de que todas las peticiones referencien al mismo nodo calculadora o a unos más que otros, no se estaría balanceado de manera 
      equlibrada la carga de peticiones.

    - No hay redundancia de datos, en caso de perderse la información de uno de los nodos no hay ningún tipo de copia de respaldo, esto se 
      podría solventar, por ejemplo, si se aplicará una comunicación entre los nodos de manera que guarden información de otros nodos como copia 
      de seguridad, sin llegar a gestionar dichas copias, y en caso de pérdida de la información del nodo original, poder restaurarla de alguna 
      manera.
