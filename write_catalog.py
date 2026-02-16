"""Write catalog.html with correct Django template syntax."""
import os

filepath = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'templates', 'museum', 'catalog.html'
)

EQ = ' == '  # Django requires spaces around ==

lines = [
    "{% extends 'base.html' %}",
    "",
    "{% block content %}",
    '<h2 class="mb-4">Cat\u00e1logo de Obras</h2>',
    "",
    '<div class="row mb-4">',
    '    <div class="col-md-3">',
    '        <div class="card shadow-sm">',
    '            <div class="card-header bg-dark text-white">Filtros</div>',
    '            <div class="card-body">',
    '                <form method="get">',
    '                    <div class="mb-3">',
    '                        <label class="form-label fw-bold">G\u00e9nero</label>',
    '                        <select name="genre" class="form-select">',
    '                            <option value="">Todos</option>',
    '                            {% for genre in genres %}',
    '                            <option value="{{ genre.id }}" {% if selected_genre_id' + EQ + 'genre.id %}selected{% endif %}>{{ genre.name }}</option>',
    '                            {% endfor %}',
    '                        </select>',
    '                    </div>',
    '',
    '                    <div class="mb-3">',
    '                        <label class="form-label fw-bold">Artista</label>',
    '                        <select name="artist" class="form-select">',
    '                            <option value="">Todos</option>',
    '                            {% for artist in artists %}',
    '                            <option value="{{ artist.id }}" {% if selected_artist_id' + EQ + 'artist.id %}selected{% endif %}>{{ artist.name }}</option>',
    '                            {% endfor %}',
    '                        </select>',
    '                    </div>',
    '',
    '                    <div class="mb-3">',
    '                        <label class="form-label fw-bold">Rango de Precio</label>',
    '                        <input type="number" name="min_price" class="form-control mb-1" placeholder="M\u00edn" value="{{ request.GET.min_price }}">',
    '                        <input type="number" name="max_price" class="form-control" placeholder="M\u00e1x" value="{{ request.GET.max_price }}">',
    '                    </div>',
    '',
    '                    <div class="mb-3">',
    '                        <label class="form-label fw-bold">Ordenar por</label>',
    '                        <select name="sort" class="form-select">',
    "                            <option value=\"price\" {% if request.GET.sort" + EQ + "'price' %}selected{% endif %}>Precio: Menor a Mayor</option>",
    "                            <option value=\"price_desc\" {% if request.GET.sort" + EQ + "'price_desc' %}selected{% endif %}>Precio: Mayor a Menor</option>",
    '                        </select>',
    '                    </div>',
    '',
    '                    <button type="submit" class="btn btn-primary w-100">Aplicar Filtros</button>',
    '                    <a href="{% url \'catalog\' %}" class="btn btn-outline-secondary w-100 mt-2">Limpiar</a>',
    '                </form>',
    '            </div>',
    '        </div>',
    '    </div>',
    '',
    '    <div class="col-md-9">',
    '        <div class="row">',
    '            {% for artwork in artworks %}',
    '            <div class="col-md-4 mb-4">',
    '                <div class="card h-100 shadow-sm">',
    '                    {% if artwork.photo %}',
    '                    <img src="{{ artwork.photo.url }}" class="card-img-top" alt="{{ artwork.title }}" style="height: 200px; object-fit: cover;">',
    '                    {% else %}',
    '                    <div class="bg-light text-muted d-flex justify-content-center align-items-center" style="height: 200px;">',
    '                        Sin Imagen',
    '                    </div>',
    '                    {% endif %}',
    '',
    '                    <div class="card-body d-flex flex-column">',
    '                        <h5 class="card-title">{{ artwork.title }}</h5>',
    '                        <p class="card-text mb-1">',
    '                            Por: <a href="{% url \'artist_detail\' artwork.artist.pk %}" class="text-decoration-none">{{ artwork.artist.name }}</a>',
    '                        </p>',
    '                        <p class="card-text text-muted small">{{ artwork.genre.name }}</p>',
    '                        <p class="card-text mt-auto"><strong class="fs-5">${{ artwork.price }}</strong></p>',
    '',
    "                        {% if artwork.status" + EQ + "'RESERVED' %}",
    '                        <span class="badge bg-warning text-dark mb-2">Reservada</span>',
    "                        {% elif artwork.status" + EQ + "'SOLD' %}",
    '                        <span class="badge bg-danger mb-2">Vendida</span>',
    '                        {% else %}',
    '                        <span class="badge bg-success mb-2">Disponible</span>',
    '                        {% endif %}',
    '',
    '                        <a href="{% url \'artwork_detail\' artwork.pk %}" class="btn btn-dark w-100 mt-2">Ver Detalles</a>',
    '                    </div>',
    '                </div>',
    '            </div>',
    '            {% empty %}',
    '            <div class="col-12 text-center mt-5">',
    '                <div class="alert alert-info">No se encontraron obras con esos criterios.</div>',
    '            </div>',
    '            {% endfor %}',
    '        </div>',
    '    </div>',
    '</div>',
    '{% endblock %}',
]

with open(filepath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# Verify
print("Verifying written file:")
with open(filepath, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f.readlines(), 1):
        if '==' in line:
            # Check spacing
            idx = line.index('==')
            before = line[idx-1]
            after = line[idx+2]
            ok = before == ' ' and after == ' '
            print(f"  Line {i}: space_before={before!r} space_after={after!r} OK={ok}")
            print(f"    {line.rstrip()}")

print("Done!")
