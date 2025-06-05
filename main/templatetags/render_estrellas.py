from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_estrellas(promedio, book_id=None):
    try:
        promedio = float(promedio)
    except (TypeError, ValueError):
        promedio = 0.0

    if book_id is None:
        book_id = 'x'

    html = ''
    for i in range(1, 6):
        diferencia = promedio - i
        if diferencia >= 0:
            # Estrella llena
            html += '''
            <svg class="icono-estrella" width="24" height="24" viewBox="0 0 24 24">
                <use href="#icono-estrella" class="estrella-rellena"></use>
            </svg>
            '''
        elif -1 < diferencia < 0:
            porcentaje = (diferencia + 1) * 100
            grad_id = f"grad-{book_id}-{i}"

            html += f'''
            <svg class="icono-estrella" width="24" height="24" viewBox="0 0 24 24">
                <defs>
                  <linearGradient id="{grad_id}">
                    <stop offset="{porcentaje}%" stop-color="gold"/>
                    <stop offset="{porcentaje}%" stop-color="lightgray"/>
                  </linearGradient>
                </defs>
                <path fill="url(#{grad_id})" d="M12 17.27L18.18 21L16.54 13.97L22 9.24
                     L14.81 8.63L12 2L9.19 8.63L2 9.24
                     L7.45 13.97L5.82 21z"/>
            </svg>
            '''
        else:
            # Estrella vacía — ¡NO uses fill directamente aquí!
            html += '''
            <svg class="icono-estrella estrella-vacia" width="24" height="24" viewBox="0 0 24 24">
                <use href="#icono-estrella"></use>
            </svg>
            '''

    return mark_safe(html)
