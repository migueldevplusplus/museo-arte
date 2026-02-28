package com.amongus.core;

import com.amongus.core.api.player.PlayerId;
import com.amongus.core.api.player.Role;
import com.amongus.core.model.Position;
import com.badlogic.gdx.Game;
import com.amongus.core.impl.engine.GameEngine;

/**
 * Punto de entrada del juego para LibGDX.
 *
 * Esta clase NO contiene lógica del juego.
 * Su única responsabilidad es:
 *  - Inicializar el motor del juego (GameEngine)
 *  - Delegar el ciclo de vida a LibGDX
 *
 * La lógica vive exclusivamente en core/impl.
 */

/** {@link com.badlogic.gdx.ApplicationListener} implementation shared by all platforms. */

public class AmongUsGame extends Game {

    private GameEngine engine;

    @Override
    public void create() {
        this.engine = new GameEngine();

        // 1. Spawneamos a los jugadores primero (Estado: LOBBY)
        PlayerId myPlayerId = engine.spawnPlayer("Local Player"); // Este será el tuyo (myPlayerId)
        PlayerId testPlayer = engine.spawnPlayer("test Player"); // Este será el tuyo (myPlayerId)
        PlayerId jugador3 = engine.spawnPlayer("Jugador 3");

        engine.assignRole(testPlayer, Role.CREWMATE);
        engine.assignRole(jugador3, Role.CREWMATE);
        engine.assignRole(myPlayerId, Role.IMPOSTOR);

        engine.startGame();

        engine.movePlayer(myPlayerId, new Position(500, 500));
        engine.movePlayer(testPlayer, new Position(350, 350));
        engine.movePlayer(jugador3, new Position(800, 800));


        // 3. Finalmente ponemos la pantalla
        setScreen(new FirstScreen(engine));
    }
    @Override
    public void dispose(){
        super.dispose();
    }

}


