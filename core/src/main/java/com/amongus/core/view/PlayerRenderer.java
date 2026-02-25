package com.amongus.core.view;

import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.utils.Disposable;

public final class PlayerRenderer implements Disposable {

    private Texture[] sprites;
    private float animationTimer; // Para controlar la velocidad de la animación
    private int frame;

    public PlayerRenderer() {
        this.sprites = new Texture[13];
        this.frame = 0;
        this.animationTimer = 0;
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
    }

    public void draw(SpriteBatch batch, float x, float y, int dir, boolean moving) {
        Texture currentFrame;

        if (moving) {
            // Lógica de animación: cambiamos de frame cada X tiempo
            animationTimer += 0.1f; // Ajusta este valor para la velocidad
            if (animationTimer > 1) {
                frame++;
                animationTimer = 0;
            }
            // Los frames de caminata van del 1 al 12
            if (frame < 1 || frame > 12) frame = 1;
            currentFrame = sprites[frame];
        } else {
            // Si está quieto, frame 0 (idle)
            currentFrame = sprites[0];
            frame = 0;
        }

        if (currentFrame != null) {
            // Dibujamos con flip según la dirección
            if (dir == 1) {
                batch.draw(currentFrame, x, y, 50, 50);
            } else {
                // Dibujamos invertido en el eje X
                batch.draw(currentFrame, x + 50, y, -50, 50);
            }
        }
    }

    @Override
    public void dispose() {
        for (Texture tex : sprites) {
            if (tex != null) tex.dispose();
        }
    }
}
