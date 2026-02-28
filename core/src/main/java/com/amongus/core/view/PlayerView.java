package com.amongus.core.view;
import com.amongus.core.api.player.PlayerId;
import com.amongus.core.model.Position;
import java.util.Objects;

public final class PlayerView {

    private final PlayerId id;
    private final boolean alive;
    private final Position position;
    private final String name;

    private boolean moving;     // ← NUEVO
    private int direction = 1;  // ← NUEVO (1 = derecha, -1 = izquierda)

    public PlayerView(PlayerId id, boolean alive, Position position, String name) {
        this.id = Objects.requireNonNull(id, "Id no puede ser null");
        this.alive = alive;
        this.position = Objects.requireNonNull(position, "Posición no puede ser null");
        this.name = name;
    }

    public PlayerId getId() {
        //hola
        return id;
    }

    public boolean isMoving() {
        return moving;
    }

    public void setMoving(boolean moving) {
        this.moving = moving;
    }

    public int getDirection() {
        return direction;
    }

    public void setDirection(int direction) {
        this.direction = direction;
    }

    public String getName() {
        return name;
    }

    public boolean isAlive() {
        return alive;
    }

    public Position getPosition() {
        return position;
    }

    @Override
    public boolean equals(Object object) {
        if (object == null || getClass() != object.getClass()) return false;
        PlayerView that = (PlayerView) object;
        return alive == that.alive && Objects.equals(id, that.id) && Objects.equals(position, that.position);
    }

    @Override
    public int hashCode() {
        return Objects.hash(id, alive, position);
    }

    @Override
    public String toString() {
        return "PlayerView{" +
                "id=" + id +
                ", alive=" + alive +
                ", position=" + position +
                '}';
    }
}
