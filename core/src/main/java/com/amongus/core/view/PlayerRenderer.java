package com.amongus.core.view;

import com.amongus.core.api.player.PlayerId;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.utils.Disposable;

import java.util.HashMap;
import java.util.Map;

public final class PlayerRenderer implements Disposable {

    private Texture[] sprites;
    private Texture deadTexture;


    // Un timer y frame POR jugador, no compartido
    private final Map<PlayerId, Float> timers = new HashMap<>();
    private final Map<PlayerId, Integer> frames = new HashMap<>();


    public PlayerRenderer() {
        this.sprites = new Texture[13];
        loadTextures();
    }

    private void loadTextures() {
        // Cargamos el idle
        sprites[0] = new Texture("sprites/idle.png");
        // Cargamos la caminata
        for (int i = 1; i <= 12; i++) {
            String num = String.format("%04d", i);
            sprites[i] = new Texture("sprites/Walk" + num + ".png");
        }

        deadTexture = new Texture("sprites/DeadAmong.png");
    }



    public void draw(SpriteBatch batch, float x, float y, PlayerId id, int dir, boolean moving, boolean isAlive) {

        if (!isAlive) {
            batch.draw(deadTexture, x, y, 50, 50);
            return;
        }

        Texture currentFrame;

        if (moving) {
            float timer = timers.getOrDefault(id, 0f) + 0.1f;
            int frame   = frames.getOrDefault(id, 1);

            if (timer > 1) {
                frame++;
                timer = 0;
            }
            if (frame < 1 || frame > 12) frame = 1;

            timers.put(id, timer);
            frames.put(id, frame);
            currentFrame = sprites[frame];
        } else {
            timers.put(id, 0f);
            frames.put(id, 0);
            currentFrame = sprites[0];
        }

        if (currentFrame != null) {
            if (dir == 1) {
                batch.draw(currentFrame, x, y, 50, 50);
            } else {
                batch.draw(currentFrame, x + 50, y, -50, 50);
            }
        }
    }
    @Override
    public void dispose() {
        for (Texture tex : sprites) {
            if (tex != null) tex.dispose();
        }
        if(deadTexture != null) deadTexture.dispose();
    }
}
