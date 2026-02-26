package com.amongus.core;

import com.amongus.core.api.player.PlayerId;
import com.amongus.core.api.state.GameState;
import com.amongus.core.impl.engine.GameEngine;
import com.amongus.core.impl.player.PlayerController;
import com.amongus.core.view.GameSnapshot;
import com.amongus.core.view.PlayerRenderer;
import com.amongus.core.view.PlayerView;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Input;
import com.badlogic.gdx.Screen;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.math.Vector2;
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

    //funcion que se ejecuta una y otra vez permitiendo ir actualizando la pantalla
    @Override
    public void render(float delta) {

        // ✅ 1. Primero input, luego snapshot — ORDEN CORRECTO
        controller.handleInput();
        GameSnapshot snapshot = engine.getSnapshot();

        if (snapshot.getState() == GameState.IN_GAME) {
            if (killCooldown > 0) killCooldown -= delta;

            // Kill con Q
            if (Gdx.input.isKeyJustPressed(Input.Keys.Q) && killCooldown <= 0) {
                PlayerView me = snapshot.getPlayers().stream()
                    .filter(p -> p.getId().equals(myPlayerId))
                    .findFirst().orElse(null);

                if (me != null) {
                    for (PlayerView pv : snapshot.getPlayers()) {
                        if (!pv.getId().equals(myPlayerId) && pv.isAlive()) {
                            float dist = Vector2.dst(
                                me.getPosition().x(), me.getPosition().y(),
                                pv.getPosition().x(), pv.getPosition().y()
                            );
                            if (dist < 150f) {
                                engine.requestKill(myPlayerId, pv.getId());
                                bloodOverlay = 0.6f;
                                shakeTimer   = 0.2f;
                                killCooldown = 15.0f;
                                break;
                            }
                        }
                    }
                }
            }

            ScreenUtils.clear(0, 0, 0, 1);
            renderGameplay(snapshot); //

        } else if (snapshot.getState() == GameState.MEETING) {
            renderVoting(snapshot);
        }
    }

    private void renderGameplay(GameSnapshot snapshot) {
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

        // 2. Mapa
        batch.draw(mapa, 0, 0, 5000, 4600);

        // 3. Capa de muertos
        for (PlayerView pv : snapshot.getPlayers()) {
            if (!pv.isAlive()) {
                playerRenderer.draw(batch, pv.getPosition().x(), pv.getPosition().y(),
                    pv.getId(), 1, false, false);
            }
        }

        // 4. Capa de vivos
        for (PlayerView pv : snapshot.getPlayers()) {
            if (pv.isAlive()) {
                boolean isMe = pv.getId().equals(myPlayerId);
                int dir     = isMe ? controller.getDireccion() : pv.getDirection();
                boolean moving = pv.isMoving();

                playerRenderer.draw(batch, pv.getPosition().x(), pv.getPosition().y(),
                    pv.getId(), dir, moving, true);
            }
        }

        batch.end();
    }

    public void renderVoting(GameSnapshot snapshot){

        batch.begin();


        ScreenUtils.clear(0.2f, 0.2f, 0.5f, 1);
        batch.end();
    }

    @Override
    public void resize(int width, int height) {

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
