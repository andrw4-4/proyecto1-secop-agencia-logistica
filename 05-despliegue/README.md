# Despliegue del tablero - Agencia Logistica SECOP II

## Estado
Tablero desplegado en AWS EC2 (instancia t3.micro, Amazon Linux 2023).
IP publica: 107.23.179.40
URL: http://107.23.179.40:8050

## Nota importante sobre AWS Academy Learner Lab
Este despliegue usa AWS Academy Learner Lab, cuyas sesiones tienen un limite
de tiempo definido por la plataforma educativa. Cuando la sesion expira,
AWS detiene automaticamente la instancia. Esto es una limitacion del entorno
academico, no del despliegue en si.

## Procedimiento para relanzar el tablero
1. Entrar a AWS Academy, Learner Lab, "Start Lab", esperar circulo verde.
2. Consola AWS, EC2, Instancias, verificar estado.
   - Si dice "Detenida": seleccionar instancia, Acciones, Iniciar instancia.
3. Copiar la nueva IPv4 publica (puede cambiar tras reiniciar).
4. Conectarse por SSH:
   ssh -i "clave-despliegue proyecto.pem" ec2-user@NUEVA_IP
5. Relanzar el tablero:
   nohup python3 app.py > salida.log 2>&1 &
6. Verificar en navegador: http://NUEVA_IP:8050
