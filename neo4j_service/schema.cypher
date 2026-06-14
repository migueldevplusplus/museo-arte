CREATE CONSTRAINT buyer_id IF NOT EXISTS FOR (b:Buyer) REQUIRE b.id IS UNIQUE;
CREATE CONSTRAINT artwork_id IF NOT EXISTS FOR (a:Artwork) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT artist_id IF NOT EXISTS FOR (a:Artist) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT genre_id IF NOT EXISTS FOR (g:Genre) REQUIRE g.id IS UNIQUE;

CREATE INDEX buyer_username IF NOT EXISTS FOR (b:Buyer) ON (b.username);
CREATE INDEX artwork_title IF NOT EXISTS FOR (a:Artwork) ON (a.title);
CREATE INDEX artist_name IF NOT EXISTS FOR (a:Artist) ON (a.name);
CREATE INDEX genre_name_idx IF NOT EXISTS FOR (g:Genre) ON (g.name);
