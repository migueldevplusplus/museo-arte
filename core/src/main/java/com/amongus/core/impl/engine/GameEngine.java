package com.amongus.core.impl.engine;


import com.amongus.core.api.Vote.Vote;
import com.amongus.core.api.events.EventBus;
import com.amongus.core.api.map.GameMap;
import com.amongus.core.api.player.Player;
import com.amongus.core.api.player.PlayerId;
import com.amongus.core.api.session.GameSession;
import com.amongus.core.api.state.GameState;
import com.amongus.core.impl.event.EventBusImpl;
import com.amongus.core.impl.map.SimpleMap;
import com.amongus.core.impl.session.GameSessionImpl;
import com.amongus.core.view.GameSnapshot;
import com.amongus.core.view.PlayerView;
import com.amongus.core.impl.player.PlayerImpl;

import java.util.List;
import java.util.UUID;

/**
 * GameEngine es la FACHADA del Core.
 *
 * Es el punto de entrada único para interactuar con el dominio del juego.
 * Los módulos externos (Application, Desktop, Multiplayer) SOLO deben
 * comunicarse con el Core a través de esta clase.
 *
 * Responsabilidades:
 *  - Crear y mantener una sesión de juego
 *  - Exponer operaciones de alto nivel (casos de uso)
 *  - Delegar la lógica real a GameSession
 *  - Gestionar el EventBus
 *
 * Importante:
 *  - NO contiene reglas complejas
 *  - NO conoce detalles de UI, red o persistencia
 */

public class GameEngine {

    private final UUID sessionId;
    private final EventBus eventBus;
    private final GameSession session;
    private final GameMap gameMap;
    private PlayerId localPlayerId;

    public GameEngine(){
        this.sessionId = UUID.randomUUID();
        this.eventBus = new EventBusImpl();
        this.gameMap = new SimpleMap();
        this.session = new GameSessionImpl(sessionId, eventBus, gameMap);

    }

    /* ===================== CONSULTAS ===================== */

    public GameSnapshot getSnapshot() {
        List<PlayerView> playerViews = session.getPlayers().stream()
            .map(p -> new PlayerView(p.getId(), p.alive(), p.getPosition()))
            .toList();

        return new GameSnapshot(session.getCurrentState(), playerViews, localPlayerId);
    }

    public EventBus getEventBus() {
        return eventBus;
    }

    public GameState getGameState() {
        return session.getCurrentState();
    }

    /* ===================== CASOS DE USO ===================== */

    /**
     * Crea y une a un jugador automáticamente.
     * Así la UI no tiene que conocer PlayerImpl.
     */
    // Modifica tu spawnPlayer así:
    public PlayerId spawnPlayer(String name) {
        PlayerId newId = PlayerId.random();
        Player player = new PlayerImpl(newId, name);
        session.addPlayer(player);

        // El primer jugador que spawneamos en esta instancia será el local
        if (this.localPlayerId == null) {
            this.localPlayerId = newId;
        }
        return newId;
    }


    public void startGame() {
        session.startGame();
    }

    public void movePlayer(PlayerId playerId, Object destination) {
        session.movePlayer(playerId, destination);
    }

    public void castVote(Vote vote) {
        session.castVote(vote);
    }

    // Nuevo: para reportar cuerpos desde la UI
    public void reportBody(PlayerId reporterId, PlayerId victimId) {
        session.reportBody(reporterId, victimId);
    }

    public PlayerId getLocalPlayerId() {
        return localPlayerId;
    }


}
