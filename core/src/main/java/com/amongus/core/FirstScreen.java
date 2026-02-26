package com.amongus.core;

import com.amongus.core.api.player.Player;
import com.amongus.core.api.player.PlayerId;
import com.amongus.core.api.state.GameState;
import com.amongus.core.impl.engine.GameEngine;
import com.amongus.core.impl.player.PlayerController;
import com.amongus.core.impl.player.PlayerImpl;
import com.amongus.core.view.GameSnapshot;
import com.amongus.core.view.PlayerRenderer;
import com.amongus.core.view.PlayerView;
import com.badlogic.gdx.Game;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;
import com.badlogic.gdx.Screen;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.math.Vector2;
import com.badlogic.gdx.scenes.scene2d.actions.VisibleAction;
import com.badlogic.gdx.utils.ScreenUtils;

/** First screen of the application. Displayed after the application is created. */
public class FirstScreen implements Screen {

    private final GameEngine engine;
    private SpriteBatch batch;
    private OrthographicCamera camera;
    private PlayerRenderer playerRenderer;

    //Recursos visuales
    private Texture mapa;
    private Texture playerTexture; //reemplaza showPlayer por ahora.
    private PlayerId myPlayerId;
    private PlayerController controller;

    private float bloodOverlay = 0;
    private Texture pixelRojo;

     private float shakeTimer = 0;
     private float killCooldown = 0;



    public FirstScreen(GameEngine engine){
        this.engine = engine;
    }

    //metodo que funciona como constructor que se ejecuta cuando se crea la interfaz
    //y permite crear nuestro escenario
    @Override
    public void show() {
        batch = new SpriteBatch();
        camera = new OrthographicCamera();
        camera.setToOrtho(false, 800, 480);
        mapa = new Texture("mapas/mapa1.png");
        playerRenderer = new PlayerRenderer();


        this.myPlayerId = engine.getLocalPlayerId();

        //EL ENGINE CREA AL JUGADOR, NO LA PANTALLA
        controller = new PlayerController(engine, myPlayerId);

        //Creacion de pixel rojo para muerte -- EN TEST
        pixelRojo = new Texture("sprites/PixelRojo.png");
    }

    //funcion que se ejecuta una y otra vez permitiendo ir actualizando la pantalla
    @Override
    public void render(float delta) {
        GameSnapshot snapshot = engine.getSnapshot();

        // LOG NUEVO - Estado actual de todos los jugadores
        long alive = snapshot.getPlayers().stream().filter(PlayerView::isAlive).count();
        long dead = snapshot.getPlayers().size() - alive;
        System.out.println("[RENDER] Frame - Vivos: " + alive + " | Muertos: " + dead);

        boolean isMoving = false;

        if (snapshot.getState() == GameState.IN_GAME) {
            // 1. Lógica de entrada y timers
            isMoving = controller.handleInput();
            if (killCooldown > 0) killCooldown -= delta;

            PlayerView me = snapshot.getPlayers().stream()
                .filter(p -> p.getId().equals(myPlayerId))
                .findFirst().orElse(null);

            // 2. Lógica de Kill simple
            // C. Lógica de Disparo de Kill (tecla Q) - DISEÑO MEJORADO
            if (Gdx.input.isKeyJustPressed(Input.Keys.Q) && killCooldown <= 0) {

                // 1. Buscamos a la víctima potencial antes de hacer nada
                PlayerView closeVictim = null;
                float rangoAtaque = 150f; // Ajusta este número (80-120) según prefieras

                for (PlayerView pv : snapshot.getPlayers()) {
                    // No me mato a mí mismo y la víctima debe estar viva
                    if (!pv.getId().equals(myPlayerId) && pv.isAlive()) {
                        float dist = com.badlogic.gdx.math.Vector2.dst(
                            me.getPosition().x(), me.getPosition().y(),
                            pv.getPosition().x(), pv.getPosition().y()
                        );

                        if (dist < rangoAtaque) {
                            closeVictim = pv;
                            break; // Encontramos uno, no hace falta buscar más
                        }
                    }
                }

                // 2. SOLO si encontramos a alguien cerca, activamos todo
                if (closeVictim != null) {
                    System.out.println("[CLIENTE] Victima detectada a distancia: " +
                        Vector2.dst(me.getPosition().x(), me.getPosition().y(),
                            closeVictim.getPosition().x(), closeVictim.getPosition().y()));

                    engine.requestKill(myPlayerId, closeVictim.getId()); // Enviamos la orden al motor

                    // RECIÉN AQUÍ disparamos lo visual
                    bloodOverlay = 0.6f;
                    shakeTimer = 0.2f; // Si quieres reactivar el shake
                    killCooldown = 15.0f;

                    System.out.println("SISTEMA: Kill exitoso sobre " + closeVictim.getId());
                } else {
                    // Opcional: Sonido de error o mensaje de "Demasiado lejos"
                    System.out.println("SISTEMA: Intento de kill fallido - Nadie en rango.");
                }
            }

            // 3. Limpiar pantalla
            ScreenUtils.clear(0, 0, 0, 1);

            // 4. Dibujar el juego (Esto llama a tu renderGameplay)
            // IMPORTANTE: Nos aseguramos de que el estado del batch esté limpio
            renderGameplay(snapshot, isMoving);

            // 5. Dibujar el Efecto de Sangre (SIN tocar la cámara del juego)
            if (bloodOverlay > 0) {
                // Guardamos la matriz actual para no romper el siguiente frame
                com.badlogic.gdx.math.Matrix4 matrixOriginal = batch.getProjectionMatrix().cpy();

                // Ponemos matriz de pantalla fija
                batch.getProjectionMatrix().setToOrtho2D(0, 0, Gdx.graphics.getWidth(), Gdx.graphics.getHeight());
                batch.begin();
                batch.setColor(1, 0, 0, bloodOverlay);
                batch.draw(pixelRojo, 0, 0, Gdx.graphics.getWidth(), Gdx.graphics.getHeight());
                batch.setColor(1, 1, 1, 1); // Reset de color vital
                batch.end();

                // Restauramos la matriz original para que el renderGameplay del siguiente frame funcione
                batch.setProjectionMatrix(matrixOriginal);

                bloodOverlay -= delta;
            }
        } else if (snapshot.getState() == GameState.MEETING) {
            renderVoting(snapshot);
        }
    }

    private void renderGameplay(GameSnapshot snapshot, boolean isMoving) {
        // 1. Centrar Cámara
        PlayerView me = snapshot.getPlayers().stream()
            .filter(p -> p.getId().equals(myPlayerId))
            .findFirst().orElse(null);

        if (me != null) {
            camera.position.set(me.getPosition().x(), me.getPosition().y(), 0);
            camera.update();
        }

        batch.setProjectionMatrix(camera.combined);
        batch.begin();

        // 2. DIBUJAR MAPA (Fondo)
        batch.draw(mapa, 0, 0, 5000, 4600);

        // 3. CAPA DE MUERTOS

        System.out.println("[RENDER] Dibujando " +
            snapshot.getPlayers().stream().filter(p -> !p.isAlive()).count() + " cadáveres");

        for (PlayerView pv : snapshot.getPlayers()) {
            if (!pv.isAlive()) {

                System.out.println("[RENDER] Dibujando cadáver de " + pv.getId() +
                    " en posición " + pv.getPosition());

                playerRenderer.draw(batch, pv.getPosition().x(), pv.getPosition().y(), 1, false, false);
            }
        }

        // 4. CAPA DE VIVOS (Encima de los muertos)
        for (PlayerView pv : snapshot.getPlayers()) {
            if (pv.isAlive()) {
                boolean isMe = pv.getId().equals(myPlayerId);
                int dir = isMe ? controller.getDireccion() : 1;
                boolean currentlyMoving = isMe && isMoving;

                playerRenderer.draw(batch, pv.getPosition().x(), pv.getPosition().y(), dir, currentlyMoving, true);
            }
        }

        batch.end();
    }



    public void renderVoting(GameSnapshot snapshot){
        // Por ahora, solo un mensaje simple para confirmar que funciona
        batch.begin();
        // Nota: En un proyecto real usarías una fuente (BitmapFont)
        // Por ahora, solo limpiaremos la pantalla a un color diferente
        ScreenUtils.clear(0.2f, 0.2f, 0.5f, 1);
        batch.end();
    }

    @Override
    public void resize(int width, int height) {
        // If the window is minimized on a desktop (LWJGL3) platform, width and height are 0, which causes problems.
        // In that case, we don't resize anything, and wait for the window to be a normal size before updating.
        if(width <= 0 || height <= 0) return;

        // Resize your screen here. The parameters represent the new window size.
    }

    @Override
    public void pause() {
        // Invoked when your application is paused.
    }

    @Override
    public void resume() {
        // Invoked when your application is resumed after pause.
    }

    @Override
    public void hide() {
        // This method is called when another screen replaces this one.
    }

    @Override
    public void dispose() {
        batch.dispose();
        mapa.dispose();
        playerTexture.dispose();
    }
}
