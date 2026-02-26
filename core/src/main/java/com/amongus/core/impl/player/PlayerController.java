package com.amongus.core.impl.player;

import com.amongus.core.api.player.PlayerId;
import com.amongus.core.impl.engine.GameEngine;
import com.amongus.core.model.Position;
import com.amongus.core.view.GameSnapshot;
import com.amongus.core.view.PlayerView;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;

public class PlayerController {
    private final GameEngine engine;
    private final PlayerId localPlayerId;
    private int direccion; // 1 derecha, -1 izquierda

    public PlayerController(GameEngine engine, PlayerId localPlayerId) {
        this.engine = engine;
        this.localPlayerId = localPlayerId;
        this.direccion = 1;
    }

    public int getDireccion() {
        return direccion;
    }

    /**
     * Procesa la entrada del teclado y solicita el movimiento al engine.
     * @return true si el jugador intentó moverse.
     */
    public boolean handleInput() {
        int speed = 5;
        float dx = 0;
        float dy = 0;

        // 1. Detectar dirección
        if (Gdx.input.isKeyPressed(Input.Keys.A)) { dx -= speed; direccion = -1; }
        if (Gdx.input.isKeyPressed(Input.Keys.D)) { dx += speed; direccion = 1; }
        if (Gdx.input.isKeyPressed(Input.Keys.W)) { dy += speed; }
        if (Gdx.input.isKeyPressed(Input.Keys.S)) { dy -= speed; }

        //Tecla para matar

        if (dx != 0 || dy != 0) {
            // 2. Obtener la posición actual desde el snapshot para calcular la nueva
            GameSnapshot snapshot = engine.getSnapshot();
            PlayerView me = snapshot.getPlayers().stream()
                .filter(p -> p.getId().equals(localPlayerId))
                .findFirst()
                .orElse(null);

            if (me != null) {
                // 3. Pedir al motor que nos mueva (el motor validará si se puede)
                Position currentPos = me.getPosition();
                Position nextPos = new Position((int) (currentPos.x() + dx), (int) (currentPos.y() + dy));

                engine.movePlayer(localPlayerId, nextPos);
                return true;
            }
        }
        return false;
    }
}
