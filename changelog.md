## 28/10
- Se añade índice invertido al proyecto adaptado para procesar tweets
- Se añaden carpetas temp/salida/tweets que trabajan con este índice
- Aún hay problemas de performance, así que trabajar con 500 / 1k tweets
- Se acomodan las rutas relativas
## 29/10
- Se mejora la performance del índice invertido añadiendo búsqueda de hasta 20 términos a la vez por cada iteración con método _grouper_.
    - Otra posible solución puede ser utilizando la built-in function zip, con _lista_termID[0::10]_, lista_termID[1::10]...
## 30/10
- Implementación buscar por palabra (no frases),
- Algunos cambios menores.
- Implementación búsqueda booleana con regex.
## 1/11
- Finalización búsqueda por palabras
- Cambios en el menú
- Documentación de algunos métodos y algunas correciones de pylint
- Adición del lematizador para el diccionario de términos (el índice invertido ya está lematizado)
- Búsqueda de a 1024 términos por iteración en la intercalación de bloques para mejorar la performance. (30.000 tweets procesados en 11s.)
## 2/11
- Adicion de busqueda por frases, y excepciones correspondientes.
- Conexion en el menù de el recopilador de tweets y el creador de indice invertido.
- Implementacion de tests
## 13/11
- Mejora del código para generar términos en la intercalación de bloques
## 14/11
- Cambios en el visualizador de tweets
- Nuevo II construído con +10k tweets
- Cambios en PATHs