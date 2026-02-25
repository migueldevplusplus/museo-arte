package com.amongus.core.impl.map;

import com.amongus.core.api.map.GameMap;
import com.amongus.core.model.Position;

/**
 * Implementación básica del mapa del juego.
 *
 * Responsabilidad:
 *  - Decidir si un jugador puede moverse de una posición a otra.
 *
 * Importante:
 *  - NO conoce gráficos
 *  - NO conoce jugadores
 *  - NO conoce estados del juego
 *
 * Es una implementación mínima y extensible.
 */
public class SimpleMap implements GameMap {

    /**
     * Determina si un movimiento es válido.
     *
     * En esta versión inicial:
     *  - Se permite cualquier movimiento distinto a la misma posición
     *
     * Esta lógica se puede endurecer más adelante
     * (paredes, zonas restringidas, etc.)
     */
    @Override
    public boolean canMove(Position from, Position to) {
        return true;
    }
}
