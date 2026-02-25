package com.amongus.core.impl.player;

import com.amongus.core.api.player.Player;
import com.amongus.core.api.player.Role;
import com.amongus.core.api.player.PlayerId;
import com.amongus.core.model.Position;

public class PlayerImpl implements Player {

    private final PlayerId id;
    private final String name;
    private Position position;

    private Role role;
    private boolean alive;
    private boolean connected;

    public PlayerImpl(PlayerId id, String name){
        this.id = id;
        this.name = name;
        this.alive = true;
        this.connected = true;
        this.position=new Position(2500,2500);
    }

    //Implementa los metodos definidos en la intrface Player
    @Override
    public PlayerId getId() {
        return id;
    }

    @Override
    public String getName() {
        return name;
    }

    public Position getPosition() {
        return position;
    }

    @Override
    public void updatePosition(Position targetPos) {
        this.position = targetPos;
    }

    @Override
    public Role getRole() {
        return role;
    }

    @Override
    public boolean alive() {
        return this.alive;
    }

    @Override
    public boolean connected() {
        return connected;
    }


    @Override
    public void move(int deltaX, int deltaY) {
        this.position = new Position(this.position.x() + deltaX, this.position.y() + deltaY);
    }

    /*Metodos que usan gameSesion*/

    public void assignRole(Role role){
        this.role = role;
    }

    public void kill(){
        this.alive = false;
    }

    public void disconnect(){
        this.connected = false;
    }
}
