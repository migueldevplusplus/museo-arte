package com.amongus.core;


import com.amongus.core.impl.voting.VoteImpl;
import com.amongus.core.api.player.Player;
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
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.Texture;
import com.badlogic.gdx.graphics.g2d.BitmapFont;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.math.Vector2;
import com.badlogic.gdx.utils.IdentityMap;
import com.badlogic.gdx.utils.ScreenUtils;

import java.util.List;
import java.util.Optional;

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

     //Implementación paa reporte
     // rango de reporte.
    private static final float REPORT_RANGO = 120f;
    private PlayerId reporterId = null;
    private PlayerId reportedCorpseId = null;

    //Fuente para los textos
    private BitmapFont font;



    public FirstScreen(GameEngine engine){
        this.engine = engine;
    }

    //metodo que funciona como constructor que se ejecuta cuando se crea la interfaz
    //y permite crear nuestro escenario
    @Override
    public void show() {

        batch = new SpriteBatch();
        camera = new OrthographicCamera();
        mapa = new Texture("mapas/mapa1.png");
        playerRenderer = new PlayerRenderer();
        font = new BitmapFont(); //Fuente por defecto de libgdx

        font.setColor(Color.WHITE);
        camera.setToOrtho(false, 800, 480);


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

        // 1. Primero input, luego snapshot
        GameSnapshot snapshot = engine.getSnapshot();

        if(engine.getGameResult() != null){
            renderEndGame();
            return;
        }

        if (snapshot.getState() == GameState.IN_GAME) {

            controller.handleInput();
            snapshot = engine.getSnapshot();

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

            PlayerView nearbyCorpse = handleReportInput(snapshot);

            ScreenUtils.clear(0, 0, 0, 1);
            renderGameplay(snapshot);


            if(nearbyCorpse != null ){
                drawReportHUD();
            }

        } else if (snapshot.getState() == GameState.MEETING) {
            handleVoteInput(snapshot);
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

        ScreenUtils.clear(0.1f, 0.1f, 0.3f, 1);

        batch.getProjectionMatrix().setToOrtho2D(0,0, Gdx.graphics.getWidth(), Gdx.graphics.getHeight());

        batch.begin();

        //Titulo.
        font.draw(batch, "REUNION DE EMERGENCIA", 50, Gdx.graphics.getHeight() - 30);

        // Después de "REUNION DE EMERGENCIA"
        if (reporterId != null && reportedCorpseId != null) {
            String reporte = reporterId.equals(myPlayerId)
                ? "Tú reportaste un cuerpo"
                : "Un jugador reportó un cuerpo";
            font.draw(batch, reporte, 50, Gdx.graphics.getHeight() - 55);
        }

        //2. Lista de jugadores Vivos.
        font.draw(batch, "Vota para expulsar", 50, Gdx.graphics.getHeight() - 80);

        int i = 0;
        for(PlayerView pv : snapshot.getPlayers()){
            if(pv.isAlive()){
                String nombre = pv.getId().equals(myPlayerId) ? ">> TU <<" : pv.getName();
                font.draw(batch, "[" + (i+1) + "] " + nombre, 50, Gdx.graphics.getHeight() - 120 - (i*30));
                i++;

            }
        }

        //SKIP
        font.draw(batch, "[S] SKIP - No votar", 50, 60);
        font.draw(batch, "[ENTER] Confirmar Voto",50,90);
        font.draw(batch, "[S] SKIP - No votar", 50,60);

        batch.end();
    }

    //METODO PARA PANTALLA FINAL DE GANADOR(ES)

    private void renderEndGame(){
        String result = engine.getGameResult();

        if("IMPOSTOR".equals(result)){
            ScreenUtils.clear(0.7f, 0.0f, 0.0f, 1); //ROJO
        } else{
            ScreenUtils.clear(0.0f, 0.2f, 0.7f, 1); // AZUL
        }
         batch.getProjectionMatrix().setToOrtho2D(0,0, Gdx.graphics.getWidth(), Gdx.graphics.getHeight());

        batch.begin();

        float centerX = Gdx.graphics.getWidth() / 2f;
        float centerY = Gdx.graphics.getHeight() / 2f;

        if("IMPOSTOR".equals(result)){
            font.draw(batch, "EL IMPOSTOR GANA",
                centerX - 80, centerY + 40);

            font.draw(batch, "Los crewmates fueron eliminados",
                centerX - 120, centerY);
        }else {
            font.draw(batch, "LOS CREWMATES GANAN",
                centerX - 90, centerY + 40);
            font.draw(batch, "El impostor fue expulsado",
                centerX - 100, centerY);
        }

        batch.end();
    }


    //Metodos de reporte---

    //Se busca al cadaver mas cercano al jugaor local dentro del rango de reporte.
    //el metodo retorna al jugador muerto (PlayerView) o null si no hay ninguno cerca.

    private PlayerView detectNearbyCorpse(GameSnapshot snapshot){
        PlayerView me = snapshot.getPlayers().stream()
            .filter(p -> p.getId().equals(myPlayerId))
            .findFirst().orElse(null);

        if(me == null){
            return  null; //en este momento se confirme si existe o no un jugador.
        }

        for(PlayerView pv : snapshot.getPlayers()){
            if(!pv.isAlive() && !pv.getId().equals(myPlayerId)){
                float dist = Vector2.dst(
                    me.getPosition().x(), me.getPosition().y(),
                    pv.getPosition().x(), pv.getPosition().y()
                );

                if(dist < REPORT_RANGO){
                    return pv; //En este momento se encuentra un cadaver cercano.
                }
            }
        }

        return null; //de no cumplirse.
    }

    //Metodo de reportar, este mismo maneja la logica de reporte en cada frame.
    //detecta cercanía/ muestra el aviso / procesa la tecla para el aviso.

    private PlayerView handleReportInput(GameSnapshot snapshot){
        PlayerView nearbyCorpse = detectNearbyCorpse(snapshot);

        if(nearbyCorpse != null){
            if(Gdx.input.isKeyJustPressed(Input.Keys.F)){
                System.out.println("[REPORTE] Cadáver cercano: " + nearbyCorpse.getId()); // ← Log
                reporterId = myPlayerId;
                reportedCorpseId = nearbyCorpse.getId();
                engine.reportBody(myPlayerId, nearbyCorpse.getId());
                // El estado cambiará a MEETING automáticamente
                // el siguiente frame render() entrará al else if MEETING
            }
        }

        return nearbyCorpse;
    }

    //Metodo para dibujar el avisa de la tecla configurada para el reporte.
    //coordenadas de pantalla fijas.

    private void drawReportHUD(){
        com.badlogic.gdx.math.Matrix4 savedMatrix = batch.getProjectionMatrix().cpy();
        batch.getProjectionMatrix().setToOrtho2D(0,0,Gdx.graphics.getWidth(), Gdx.graphics.getHeight());

        batch.begin();

        //dibujo de un place holder basico ara testaer la funcion

        batch.setColor(1f, 0.9f, 0f, 0.85f);
        batch.draw(pixelRojo, Gdx.graphics.getHeight() / 2f - 80, 60, 160, 36);
        batch.setColor(1,1,1,1);
        batch.end();

        batch.setProjectionMatrix(savedMatrix);


    }


    //Logica de votacion
    private void handleVoteInput(GameSnapshot snapshot){
        //Se construye una lista de los jugadores vivos, la cual es la misma que se dibuja.
        List<PlayerView> votable = snapshot.getPlayers().stream().filter(PlayerView::isAlive)
            .collect(java.util.stream.Collectors.toList());

        //teclas 1-9 mapean a jugadores en orden
        for(int i = 0; i < votable.size(); i++){
            int key = Input.Keys.NUM_1 + i;
            if(Gdx.input.isKeyJustPressed(key)){
                PlayerId targetId = votable.get(i).getId();

                //Validación para evitar votarse a uno mismo.
                if (targetId.equals(myPlayerId)) {
                    System.out.println("[VOTO] No puedes votarte a ti mismo");
                    continue;
                }

                engine.castVote(new VoteImpl(myPlayerId, targetId));
                System.out.println("[VOTO] " + myPlayerId + " votó por " + targetId);
            }
        }

        //SKIP
        if (Gdx.input.isKeyJustPressed(Input.Keys.S)){
            engine.castVote(new VoteImpl(myPlayerId, null)); // null porque el voto es skip osea nulo.
            System.out.println("[VOTO] " + myPlayerId + " hizo Skip");
        }

        //Procesar enter para confirmar el voto
        if(Gdx.input.isKeyJustPressed(Input.Keys.ENTER)){
            Optional<PlayerId> expelled = engine.resolveVoting();
            expelled.ifPresent(id-> System.out.println("[RESULTADO] Expulsado: "+ id));
            //estaod regresa a IN_GAME.
        }
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
        font.dispose();
    }
}
