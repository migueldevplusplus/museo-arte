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
    }

    //funcion que se ejecuta una y otra vez permitiendo ir actualizando la pantalla
    @Override
    public void render(float delta) {
        // 1. Obtener la "Realidad" del juego (el Snapshot)
        GameSnapshot snapshot = engine.getSnapshot();

        // 2. PROCESAR INPUT (Lógica de control antes de dibujar)
        // Solo permitimos movernos si estamos en el estado de juego
        // 2. Procesar Input y Movimiento (Solo si estamos en juego)
        boolean isMoving = false;
        if (snapshot.getState() == GameState.IN_GAME) {
            isMoving = controller.handleInput(); // Actualiza la posición en el Engine
            System.out.println("Cámara en: " + camera.position.x + ", " + camera.position.y);

            // Tecla R para reportar
            if(Gdx.input.isKeyJustPressed(Input.Keys.R)) {
                engine.reportBody(myPlayerId, null);
            }
        }

        // 3. LIMPIAR PANTALLA
        ScreenUtils.clear(0, 0, 0, 1);

        // 4. DIBUJAR SEGÚN EL ESTADO
        // Separamos el dibujo en métodos diferentes para no tener un código gigante aquí
        // 4. Dibujar según el estado
        if (snapshot.getState() == GameState.IN_GAME) {
            renderGameplay(snapshot, isMoving);
        } else if (snapshot.getState() == GameState.MEETING) {
            renderVoting(snapshot);
        }
    }

    private void renderGameplay(GameSnapshot snapshot, boolean isMoving) {
        // 1. Buscar al jugador local
        PlayerView me = snapshot.getPlayers().stream()
            .filter(p -> p.getId().equals(myPlayerId))
            .findFirst().orElse(null);

        if (me != null) {
            camera.position.set(me.getPosition().x(), me.getPosition().y(), 0);
            camera.update();
        }

        // 2. VINCULAR CÁMARA AL BATCH
        batch.setProjectionMatrix(camera.combined);

        batch.begin();

        // 3. PRIMERO EL MAPA (El fondo)
        batch.draw(mapa, 0, 0, 5000, 4600);

        // 4. LUEGO LOS JUGADORES (Encima del mapa)
        for (PlayerView pv : snapshot.getPlayers()) {

            boolean isMe = pv.getId().equals(myPlayerId);
            // Obtenemos la dirección del controlador para el flip
            int dir = pv.getId().equals(myPlayerId) ? controller.getDireccion() : 1;

            boolean currentlyMoving = isMe && isMoving;

            // Usamos el renderer
            playerRenderer.draw(batch, pv.getPosition().x(), pv.getPosition().y(), dir, currentlyMoving);

            // TEST DE SEGURIDAD: Si no ves la skin, esto dibujará un cuadro rojo donde DEBERÍA estar
            // Si ves el cuadro rojo pero no la skin, el error está DENTRO de PlayerRenderer.draw()
            // batch.draw(texturaRojaTemporal, pv.getPosition().x(), pv.getPosition().y(), 50, 50);
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
