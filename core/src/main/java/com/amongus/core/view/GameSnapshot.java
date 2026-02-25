package com.amongus.core.view;

import com.amongus.core.api.state.GameState;
import com.amongus.core.api.player.PlayerId; // Añadimos esto
import java.util.List;

public final class GameSnapshot {

    private final GameState state;
    private final List<PlayerView> players;
    private final PlayerId localPlayerId; // Para saber a quién sigue la cámara

    public GameSnapshot(GameState state, List<PlayerView> players, PlayerId localPlayerId){
        this.state = state;
        this.players = List.copyOf(players);
        this.localPlayerId = localPlayerId;
    }

    public GameState getState() {
        return state;
    }

    public List<PlayerView> getPlayers() {
        return players;
    }

    public PlayerId getLocalPlayerId() {
        return localPlayerId;
    }
}
