# GreenDrop - Sistema de Riego Automático Doméstico

## Descripción

GreenDrop es un sistema embebido diseñado para automatizar el riego de plantas en entornos domésticos.  
El sistema corre sobre una tarjeta Lichee RV Dock con Linux embebido y está programado en C para control de sensores y actuadores, y Python (Flask) para la interfaz web local.

El objetivo es medir la humedad ambiental, activar un sistema de riego automáticamente cuando la humedad esté por debajo de un umbral configurable, y ofrecer control y monitoreo vía navegador en la red local.