from PIL import Image, ImageDraw, ImageFont
import random

class Fretboard:
    def __init__(self, tuning=None):
        # Define default tuning for a 6-string guitar
        if tuning is None:
            tuning = ['A#', 'D', 'G#', 'C#', 'F', 'A#']
        
        self.tuning = tuning
        self.num_strings = len(tuning)
        
        # Define the notes in a chromatic scale
        self.chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Define frets that have position markers (dots)
        self.position_marker_frets = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]
        
        # Set up image dimensions
        self.fretboard_width = 1300
        self.border_thickness = 50
        self.string_spacing = 30
        self.fretboard_height = self.string_spacing * (self.num_strings + 1)
        self.fret_spacing = self.fretboard_width // 25
        
        # Generate the notes for each string
        self.fretboard = []
        for string in self.tuning:
            self.fretboard.append([self._note_at_fret(string, fret) for fret in range(25)])
        
        # Load a font
        self.fontsize = 16
        try:
            self.font = ImageFont.truetype('Arial.ttf', self.fontsize)
        except:
            # Fallback to default font
            self.font = ImageFont.load_default()
    
    def _note_at_fret(self, tuning_note, fret):
        note_index = self.chromatic_scale.index(tuning_note)
        return self.chromatic_scale[(note_index + fret) % 12]
    
    def init_fretboard(self):
        # Create an image with a larger black background to frame the fretboard
        image = Image.new('RGB', (self.fretboard_width + 2 * self.border_thickness, 
                                 self.fretboard_height + 2 * self.border_thickness), color='black')
        draw = ImageDraw.Draw(image)

        # Draw the fretboard background in dark brown
        draw.rectangle([self.border_thickness, self.border_thickness, 
                       self.border_thickness + self.fretboard_width, 
                       self.border_thickness + self.fretboard_height], fill='#150000')

        # Draw frets
        for fret in range(25):  # 24 frets + the zero fret
            x = self.border_thickness + fret * self.fret_spacing
            line_width = 16 if fret == 1 else 2  # Zero fret thicker
            draw.line([(x, self.border_thickness + 20), 
                      (x, self.border_thickness + self.fretboard_height - 20)], 
                     fill='darkgray', width=line_width)

        # Draw strings with varying thickness (low strings thicker, at the bottom)
        for string in range(self.num_strings):
            y = self.border_thickness + (self.num_strings - string) * self.string_spacing
            string_width = 6 if string == 0 else 4  # Thickest for the lowest string
            draw.line([(self.border_thickness, y), 
                      (self.border_thickness + self.fretboard_width, y)], 
                     fill='lightgray', width=string_width)

        # Draw position markers (dots)
        for fret in self.position_marker_frets:
            x = self.border_thickness + fret * self.fret_spacing + self.fret_spacing // 2
            if fret == 12:
                # Draw two dots for the 12th fret
                y1 = self.border_thickness + self.fretboard_height // 3
                y2 = self.border_thickness + 2 * self.fretboard_height // 3
                draw.ellipse([(x - 10, y1 - 10), (x + 10, y1 + 10)], fill='white')
                draw.ellipse([(x - 10, y2 - 10), (x + 10, y2 + 10)], fill='white')
            else:
                y = self.border_thickness + self.fretboard_height // 2
                draw.ellipse([(x - 10, y - 10), (x + 10, y + 10)], fill='white')

        # Draw fret numbers above the fretboard
        for fret in range(25):
            x = self.border_thickness + fret * self.fret_spacing + self.fret_spacing // 2
            text = str(fret)
            text_bbox = draw.textbbox((0, 0), text, font=self.font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.text((x - text_width // 2, self.border_thickness - text_height - 15), 
                     text, fill='white', font=self.font)

        # Draw string tuning on the left side outside the fretboard
        for string in range(self.num_strings):
            y = self.border_thickness + (self.num_strings - string) * self.string_spacing - self.string_spacing // 2
            text = self.tuning[string]
            text_bbox = draw.textbbox((0, 0), text, font=self.font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.text((self.border_thickness - text_width - 20, (y - text_height) + 35 // 2), 
                     text, fill='white', font=self.font)
        
        # Attach the image to the draw object
        draw.image = image
        return draw
    
    def draw_note_on_fretboard(self, draw, string_index, fret, color, note, text='black'):
        x = self.border_thickness + fret * self.fret_spacing + self.fret_spacing // 2
        y = self.border_thickness + (self.num_strings - string_index) * self.string_spacing
        radius = 12
        draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=color)
        
        # Use textbbox to calculate text width and height
        text_bbox = draw.textbbox((0, 0), note, font=self.font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        draw.text((x - text_width // 2, y - text_height), note, fill=text, font=self.font)
    
    def fretboard_title(self, draw, title):
        if not title:
            return draw
        
        # Get the bounding box of the text
        bbox = draw.textbbox((0, 0), title, font=self.font)
        
        # Calculate the text width and height
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Calculate image dimensions
        image_width = self.fretboard_width + 2 * self.border_thickness
        image_height = self.fretboard_height + 2 * self.border_thickness
        text_y = (image_height - text_height - 40)
        
        # Determine alignment based on title content
        title_lower = title.lower()
        
        if title_lower.startswith('chord'):
            # Left justify for Chord titles
            text_x = self.border_thickness  # Left padding
        elif title_lower.startswith('scale'):
            # Right justify for Scale titles
            text_x = image_width - text_width - self.border_thickness  # Right padding
        else:
            # Center for other titles (fallback)
            text_x = (image_width - text_width) / 2
        
        # Add the text to the image
        draw.text((text_x, text_y), title, font=self.font, fill=(255, 255, 255))
        return draw


def find_chords_in_scale(note, scale_name):
    # constantes
    chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    chord_dictionary = {
        # **Triadas Básicas**
        'maj': [0, 4, 7],           # luminoso, estable, afirmativo, “hogar”
        'min': [0, 3, 7],           # melancólico, introspectivo, emotivo
        'dim': [0, 3, 6],           # tenso, inquietante, inestable, “suspenso”
        'aug': [0, 4, 8],           # expectante, soñador, surreal, flotante

        # **Séptimas**
        'maj7': [0, 4, 7, 11],      # elegante, nostálgico, contemplativo, urbano
        'min7': [0, 3, 7, 10],      # cálido, íntimo, soul, “confesional”
        'dom7': [0, 4, 7, 10],      # picante, bluesy, extrovertido, resolutivo
        'dim7': [0, 3, 6, 9],       # misterioso, vintage terror, teatral
        'min7b5': [0, 3, 6, 10],    # sombrío, cine noir, suspenso contenido

        # **Acordes Extendidos**
        '9': [0, 4, 7, 10, 2],              # groovy, sociable, “club”, chispeante
        'maj9': [0, 4, 7, 11, 2],           # luminoso, cinematográfico, etéreo
        'min9': [0, 3, 7, 10, 2],           # melancólico, neblinoso, neo-soul
        '11': [0, 4, 7, 10, 2, 5],          # denso, urbano, modern-jazz, áspero si cerrado
        '13': [0, 4, 7, 10, 2, 9],          # festivo, funky, expansivo
        'maj13': [0, 4, 7, 11, 2, 9],       # radiante, “cielo abierto”, elegante y suave

        # **Acordes con Notas Añadidas (Add)**
        'add9': [0, 4, 7, 2],        # brillante, juvenil, esperanzador
        'add11': [0, 4, 7, 5],       # dulce con fricción, curioso, indie
        'add13': [0, 4, 7, 9],       # veraniego, vintage pop, amable
        'minadd9': [0, 3, 7, 2],     # triste-bello, soñador, “lluvia en ventana”
        'minadd11': [0, 3, 7, 5],    # íntimo con halo modal, folk melancólico
        'minadd13': [0, 3, 7, 9],    # agridulce, nostálgico con luz

        # **Aliases útiles**
        'add2': [0, 4, 7, 2],        # = add9 | fresco, abierto
        'add4': [0, 4, 7, 5],        # = add11 | curioso, reflexivo

        # **Colores Mayores extra**
        'add#11': [0, 4, 7, 6],              # lidio: mágico, “suspensión solar”, moderno
        'add9#11': [0, 4, 7, 2, 6],          # brillante y onírico, dream-pop/jazz-film
        'maj6': [0, 4, 7, 9],                # amable, retro, “domingo por la tarde”
        'maj6add9': [0, 4, 7, 9, 2],         # 6/9: sedoso, tónico perfecto, pacífico
        '6add9': [0, 4, 7, 9, 2],            # alias de 6/9 | seda, optimista
        'maj7add13': [0, 4, 7, 11, 9],       # sofisticado, cálido, balada elegante

        # **Acordes Suspendidos**
        'sus2': [0, 2, 7],            # abierto, inocente, contemplativo
        'sus4': [0, 5, 7],            # heroico, expectante, himno
        '7sus4': [0, 5, 7, 10],       # groove épico, rock clásico, afirmación sin 3ª
        '6sus4': [0, 5, 7, 9],        # luminoso, folk-rock, respiro despejado
        '9sus4': [0, 5, 7, 10, 2],    # amplio, gospel/funk, celebración controlada

        # **Acordes Alterados**
        '7b5': [0, 4, 6, 10],         # filoso, tensión cinematográfica, “peligro”
        '7#5': [0, 4, 8, 10],         # psicodélico, ardiente, exótico
        'maj7b5': [0, 4, 6, 11],      # cristalino con filo, sofisticación fría
        'maj7#5': [0, 4, 8, 11],      # radiante, lujoso, “sol fuerte”
        'maj9#11': [0, 4, 7, 11, 2, 6],  # lidio cinematográfico, sublime, flotante

        # **Acordes Menor Mayor Séptima**
        'minmaj7': [0, 3, 7, 11],     # melancolía sofisticada, “feliz-triste”, anime/jazz

        # **Acordes de Cuartal (Quartal Harmony)**
        'quartal': [0, 5, 10],              # modal, nebuloso, “paisaje”
        'quartal7': [0, 5, 10, 3],          # enigmático, cerebral, post-bop
        'quartal9': [0, 5, 10, 3, 7],       # amplio, etéreo, moderno

        # **Acordes de Quintal (Quintal Harmony)**
        'quintal': [0, 7, 2],               # épico, cinematográfico, aireado
        'quintal7': [0, 7, 2, 10],          # heroico con carácter, rock orquestal
        'quintal9': [0, 7, 2, 10, 4],       # grandilocuente con centro tonal claro

        # **Acordes Power**
        'power': [0, 7],                    # contundente, neutral, “muro”
        'power7': [0, 7, 10],               # agresivo, rock/blues, rugoso
        'power9': [0, 7, 10, 2],            # moderno, metal/groove, expansión

        # **Acordes Adicionales**
        'maj11': [0, 4, 7, 11, 5],          # mayor con roce 3–11: curioso, indie-jazz
        'maj7#11': [0, 4, 7, 11, 6],        # lidio pulcro, ciencia-ficción amable
        'min11': [0, 3, 7, 10, 5],          # profundo, neo-soul, nocturno
        'min9b5': [0, 3, 6, 10, 2],         # tenso-poético, noir, suspenso elegante
        'min11b5': [0, 3, 6, 10, 5, 2],     # bruma densa, misterio modal

        # **Acordes Alterados Adicionales**
        'aug7': [0, 4, 8, 10],              # ardiente, febril, trance vintage
        'dim9': [0, 3, 6, 9, 2],            # carrusel extraño, circo oscuro
        'dim11': [0, 3, 6, 9, 5],           # cámara de ecos, terror teatral
        'aug9': [0, 4, 8, 10, 2],           # exotismo brillante, psicodelia elegante

        # **Acordes Extendidos de Cuartal y Quintal**
        'quartal11': [0, 5, 10, 3, 7],      # paisaje amplio, espiritual, “montaña”
        'quintal13': [0, 7, 2, 10, 4, 9],   # épico-cálido, banda sonora

        # **Acordes Hexatónicos y Heptatónicos**
        'hexatonic': [0, 4, 7, 11, 2, 9],   # pad mayor lujoso, ensueño
        'heptatonic': [0, 2, 4, 5, 7, 9, 11], # escala mayor completa: didáctico, claro

        # **Otros Comunes**
        'min6': [0, 3, 7, 9],               # dulce-nostálgico, vintage latino/jazz
        'min6add9': [0, 3, 7, 9, 2],        # cinematográfico triste-luminoso
    }
    scale_dictionary = {
        'major': [0, 2, 4, 5, 7, 9, 11],  # Alegre, brillante, optimista
        'minor': [0, 2, 3, 5, 7, 8, 10],  # Triste, melancólico, serio
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],  # Exótico, dramático, oriental
        'melodic_minor': [0, 2, 3, 5, 7, 9, 11],  # Ambiguo, sofisticado, jazzístico
        'pentatonic_major': [0, 2, 4, 7, 9],  # Simple, folclórico, abierto
        'pentatonic_minor': [0, 3, 5, 7, 10],  # Bluesy, introspectivo, emotivo
        'pentatonic_harmonic_minor': [0, 3, 7, 8, 11],  # Trágico, dramático, exótico
        'pentatonic_phrygian': [0, 1, 3, 5, 7],  # Oscuro, étnico, místico
        'pentatonic_dorian_minor': [0, 3, 5, 7, 9],  # Menor moderno, melancólico pero ágil
        'pentatonic_locrian': [0, 3, 5, 6, 10],  # Muy oscuro, inestable, disonante
        'lydian_pentatonic': [0, 2, 4, 6, 9],  # Onírico, etéreo, surrealista
        'augmented_pentatonic': [0, 4, 8, 10, 2],  # Brillante pero distorsionado, inestable
        'lydian_sharp5_pentatonic': [0, 2, 4, 8, 9],  # Soñador pero deforme, elegante
        'phrygian_dominant_pentatonic': [0, 1, 4, 7, 10],  # Muy oscuro, exótico, árabe-metal
        'mixolydian_b6_pentatonic': [0, 2, 5, 8, 10],  # Oscuro, modal, blues triste
        'half_whole_diminished_pentatonic': [0, 1, 3, 4, 6],  # Muy tenso, jazzy, inestable
        'altered_pentatonic': [0, 1, 3, 6, 10],  # Súper disonante, caos controlado
        'blues': [0, 3, 5, 6, 7, 10],  # Expresivo, con lamento, profundo
        'dorian': [0, 2, 3, 5, 7, 9, 10],  # Místico, menor con toque optimista
        'phrygian': [0, 1, 3, 5, 7, 8, 10],  # Oscuro, flamenco, español
        'lydian': [0, 2, 4, 6, 7, 9, 11],  # Soñador, etéreo, flotante
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],  # Alegre pero relajado, rock, blues
        'locrian': [0, 1, 3, 5, 6, 8, 10],  # Inestable, tenso, misterioso
        'whole_tone': [0, 2, 4, 6, 8, 10],  # Ambiguo, onírico, impresionista
        'diminished': [0, 2, 3, 5, 6, 8, 9, 11],  # Tenso, dramático, misterioso
        'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # Disonante, atonal, complejo
        'augmented': [0, 3, 4, 7, 8, 11],  # Inusual, enigmático, flotante
        'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],  # Exótico, oriental, gitano
        'double_harmonic': [0, 1, 4, 5, 7, 8, 11],  # Oriental, dramático, intenso
        'hungarian_minor': [0, 2, 3, 6, 7, 8, 11],  # Melancólico, exótico, gitano
        'hungarian_major': [0, 3, 4, 6, 7, 9, 10],
        'neapolitan_minor': [0, 1, 3, 5, 7, 8, 11],  # Dramático, oscuro, clásico
        'neapolitan_major': [0, 1, 3, 5, 7, 9, 11],  # Exótico, brillante, sorprendente
        'persian': [0, 1, 4, 5, 6, 8, 11],  # Misterioso, oriental, exótico
        'enigmatic': [0, 1, 4, 6, 8, 10, 11],  # Intrigante, complejo, misterioso
        'hindu': [0, 2, 4, 5, 7, 8, 10],  # Místico, relajado, exótico
        'japanese': [0, 1, 5, 7, 8],  # Oriental, pentatónico, sereno
        'arabic': [0, 2, 4, 5, 6, 8, 10],  # Místico, exótico, intenso
        'gypsy': [0, 2, 3, 6, 7, 8, 10],  # Apasionado, dramático, gitano
        'byzantine': [0, 1, 4, 5, 7, 8, 11],  # Antiguo, místico, solemne
        'balinese': [0, 1, 3, 7, 8],  # Etéreo, exótico, pentatónico
        'todi': [0, 1, 3, 6, 7, 8, 11],  # Introspectivo, clásico indio, místico
        'bebop_major': [0, 2, 4, 5, 7, 9, 10, 11],  # Sofisticado, fluido, jazzístico
        'bebop_minor': [0, 2, 3, 5, 7, 8, 9, 10],  # Complejo, bluesy, jazzístico
        'bebop_dominant': [0, 2, 4, 5, 7, 9, 10, 11],  # Rítmico, swing, jazzístico
        'bebop_dorian': [0, 2, 3, 5, 7, 9, 10, 11],  # Melódico, fluido, jazzístico
        'bebop_melodic_minor': [0, 2, 3, 5, 7, 8, 9, 11],  # Sofisticado, ambiguo, jazzístico
        'bebop_harmonic_minor': [0, 2, 3, 5, 7, 8, 11, 12],  # Exótico, tenso, jazzístico
        'flamenco': [0, 1, 3, 4, 5, 7, 8],  # Apasionado, español, flamenco
        'romanian_minor': [0, 2, 3, 6, 7, 9, 10],  # Melancólico, exótico, gitano
        'lydian_diminished': [0, 2, 3, 6, 7, 9, 11],  # Místico, exótico
        'javanese': [0, 1, 3, 5, 7, 8, 11],  # Místico, oriental, exótico
        'blues_major': [0, 2, 3, 4, 7, 9],  # Alegre, emotivo, bluesy
        'blues_minor': [0, 3, 5, 6, 7, 10, 12],  # Triste, expresivo, bluesy
        'lydian_augmented': [0, 2, 4, 6, 8, 9, 11],  # Brillante, futurista, luminoso
        'half_whole_diminished': [0, 1, 3, 4, 6, 7, 9, 10],  # Tenso, cromático, misterioso
        'harmonic_major': [0, 2, 4, 5, 7, 8, 11],  # Exótico, dramático, clásico
        'altered_scale': [0, 1, 3, 4, 6, 8, 10],  # Tenso, disonante, jazzístico
        'prometheus': [0, 2, 4, 6, 9, 10],  # Misterioso, moderno, innovador
        'egyptian_pentatonic': [0, 2, 5, 7, 10],  # Exótico, místico, antiguo
        'chinese_pentatonic': [0, 4, 6, 7, 11],  # Sereno, cultural, único
    }
    # 1) Root note index in the chromatic system
    if note not in chromatic_scale:
        raise ValueError(f"Invalid note: {note}")

    root_index = chromatic_scale.index(note)

    # 2) Build absolute scale (list of semitone values)
    scale_intervals = scale_dictionary[scale_name]
    scale_notes = [(root_index + interval) % 12 for interval in scale_intervals]

    # Convert scale_notes into a set for fast membership checks
    scale_note_set = set(scale_notes)

    results = []

    # 3) For each chord type (maj, min7, add9, etc.)
    for chord_name, chord_intervals in chord_dictionary.items():

        # 4) Try every degree in the scale as the chord root
        for interval in scale_intervals:
            chord_root = (root_index + interval) % 12
            chord_root_note = chromatic_scale[chord_root]

            # Build the actual chord tones for this specific root
            chord_notes = [(chord_root + ci) % 12 for ci in chord_intervals]

            # Check containment: all tones must exist in the scale
            if all(n in scale_note_set for n in chord_notes):
                full_name = f"{chord_root_note}{chord_name}"
                results.append({
                    "name": full_name,
                    "root": chord_root_note,
                    "type": chord_name,
                    "notes": [chromatic_scale[n] for n in chord_notes]
                })

    return results



# Static functions that don't depend on tuning
def chord_patterns(input_value):
    # Your existing chord_patterns function stays the same
    chord_dictionary = {
        # **Triadas Básicas**
        'maj': [0, 4, 7],           # luminoso, estable, afirmativo, “hogar”
        'min': [0, 3, 7],           # melancólico, introspectivo, emotivo
        'dim': [0, 3, 6],           # tenso, inquietante, inestable, “suspenso”
        'aug': [0, 4, 8],           # expectante, soñador, surreal, flotante

        # **Séptimas**
        'maj7': [0, 4, 7, 11],      # elegante, nostálgico, contemplativo, urbano
        'min7': [0, 3, 7, 10],      # cálido, íntimo, soul, “confesional”
        'dom7': [0, 4, 7, 10],      # picante, bluesy, extrovertido, resolutivo
        'dim7': [0, 3, 6, 9],       # misterioso, vintage terror, teatral
        'min7b5': [0, 3, 6, 10],    # sombrío, cine noir, suspenso contenido

        # **Acordes Extendidos**
        '9': [0, 4, 7, 10, 2],              # groovy, sociable, “club”, chispeante
        'maj9': [0, 4, 7, 11, 2],           # luminoso, cinematográfico, etéreo
        'min9': [0, 3, 7, 10, 2],           # melancólico, neblinoso, neo-soul
        '11': [0, 4, 7, 10, 2, 5],          # denso, urbano, modern-jazz, áspero si cerrado
        '13': [0, 4, 7, 10, 2, 9],          # festivo, funky, expansivo
        'maj13': [0, 4, 7, 11, 2, 9],       # radiante, “cielo abierto”, elegante y suave

        # **Acordes con Notas Añadidas (Add)**
        'add9': [0, 4, 7, 2],        # brillante, juvenil, esperanzador
        'add11': [0, 4, 7, 5],       # dulce con fricción, curioso, indie
        'add13': [0, 4, 7, 9],       # veraniego, vintage pop, amable
        'minadd9': [0, 3, 7, 2],     # triste-bello, soñador, “lluvia en ventana”
        'minadd11': [0, 3, 7, 5],    # íntimo con halo modal, folk melancólico
        'minadd13': [0, 3, 7, 9],    # agridulce, nostálgico con luz

        # **Aliases útiles**
        'add2': [0, 4, 7, 2],        # = add9 | fresco, abierto
        'add4': [0, 4, 7, 5],        # = add11 | curioso, reflexivo

        # **Colores Mayores extra**
        'add#11': [0, 4, 7, 6],              # lidio: mágico, “suspensión solar”, moderno
        'add9#11': [0, 4, 7, 2, 6],          # brillante y onírico, dream-pop/jazz-film
        'maj6': [0, 4, 7, 9],                # amable, retro, “domingo por la tarde”
        'maj6add9': [0, 4, 7, 9, 2],         # 6/9: sedoso, tónico perfecto, pacífico
        '6add9': [0, 4, 7, 9, 2],            # alias de 6/9 | seda, optimista
        'maj7add13': [0, 4, 7, 11, 9],       # sofisticado, cálido, balada elegante

        # **Acordes Suspendidos**
        'sus2': [0, 2, 7],            # abierto, inocente, contemplativo
        'sus4': [0, 5, 7],            # heroico, expectante, himno
        '7sus4': [0, 5, 7, 10],       # groove épico, rock clásico, afirmación sin 3ª
        '6sus4': [0, 5, 7, 9],        # luminoso, folk-rock, respiro despejado
        '9sus4': [0, 5, 7, 10, 2],    # amplio, gospel/funk, celebración controlada

        # **Acordes Alterados**
        '7b5': [0, 4, 6, 10],         # filoso, tensión cinematográfica, “peligro”
        '7#5': [0, 4, 8, 10],         # psicodélico, ardiente, exótico
        'maj7b5': [0, 4, 6, 11],      # cristalino con filo, sofisticación fría
        'maj7#5': [0, 4, 8, 11],      # radiante, lujoso, “sol fuerte”
        'maj9#11': [0, 4, 7, 11, 2, 6],  # lidio cinematográfico, sublime, flotante

        # **Acordes Menor Mayor Séptima**
        'minmaj7': [0, 3, 7, 11],     # melancolía sofisticada, “feliz-triste”, anime/jazz

        # **Acordes de Cuartal (Quartal Harmony)**
        'quartal': [0, 5, 10],              # modal, nebuloso, “paisaje”
        'quartal7': [0, 5, 10, 3],          # enigmático, cerebral, post-bop
        'quartal9': [0, 5, 10, 3, 7],       # amplio, etéreo, moderno

        # **Acordes de Quintal (Quintal Harmony)**
        'quintal': [0, 7, 2],               # épico, cinematográfico, aireado
        'quintal7': [0, 7, 2, 10],          # heroico con carácter, rock orquestal
        'quintal9': [0, 7, 2, 10, 4],       # grandilocuente con centro tonal claro

        # **Acordes Power**
        'power': [0, 7],                    # contundente, neutral, “muro”
        'power7': [0, 7, 10],               # agresivo, rock/blues, rugoso
        'power9': [0, 7, 10, 2],            # moderno, metal/groove, expansión

        # **Acordes Adicionales**
        'maj11': [0, 4, 7, 11, 5],          # mayor con roce 3–11: curioso, indie-jazz
        'maj7#11': [0, 4, 7, 11, 6],        # lidio pulcro, ciencia-ficción amable
        'min11': [0, 3, 7, 10, 5],          # profundo, neo-soul, nocturno
        'min9b5': [0, 3, 6, 10, 2],         # tenso-poético, noir, suspenso elegante
        'min11b5': [0, 3, 6, 10, 5, 2],     # bruma densa, misterio modal

        # **Acordes Alterados Adicionales**
        'aug7': [0, 4, 8, 10],              # ardiente, febril, trance vintage
        'dim9': [0, 3, 6, 9, 2],            # carrusel extraño, circo oscuro
        'dim11': [0, 3, 6, 9, 5],           # cámara de ecos, terror teatral
        'aug9': [0, 4, 8, 10, 2],           # exotismo brillante, psicodelia elegante

        # **Acordes Extendidos de Cuartal y Quintal**
        'quartal11': [0, 5, 10, 3, 7],      # paisaje amplio, espiritual, “montaña”
        'quintal13': [0, 7, 2, 10, 4, 9],   # épico-cálido, banda sonora

        # **Acordes Hexatónicos y Heptatónicos**
        'hexatonic': [0, 4, 7, 11, 2, 9],   # pad mayor lujoso, ensueño
        'heptatonic': [0, 2, 4, 5, 7, 9, 11], # escala mayor completa: didáctico, claro

        # **Otros Comunes**
        'min6': [0, 3, 7, 9],               # dulce-nostálgico, vintage latino/jazz
        'min6add9': [0, 3, 7, 9, 2],        # cinematográfico triste-luminoso
    }

    
    # Handle the input based on its type
    if isinstance(input_value, str):
        return chord_dictionary.get(input_value)
    elif isinstance(input_value, list) and len(input_value) == 2:
        chord_name, axis = input_value
        if chord_name in chord_dictionary and isinstance(axis, int) and 0 <= axis < 12:
            return [(2 * axis - note) % 12 for note in chord_dictionary[chord_name]]
    return None

def scale_patterns(input_value):
    # Your existing scale_patterns function stays the same
    scale_dictionary = {
        'major': [0, 2, 4, 5, 7, 9, 11],  # Alegre, brillante, optimista
        'minor': [0, 2, 3, 5, 7, 8, 10],  # Triste, melancólico, serio
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],  # Exótico, dramático, oriental
        'melodic_minor': [0, 2, 3, 5, 7, 9, 11],  # Ambiguo, sofisticado, jazzístico
        'pentatonic_major': [0, 2, 4, 7, 9],  # Simple, folclórico, abierto
        'pentatonic_minor': [0, 3, 5, 7, 10],  # Bluesy, introspectivo, emotivo
        'pentatonic_harmonic_minor': [0, 3, 7, 8, 11],  # Trágico, dramático, exótico
        'pentatonic_phrygian': [0, 1, 3, 5, 7],  # Oscuro, étnico, místico
        'pentatonic_dorian_minor': [0, 3, 5, 7, 9],  # Menor moderno, melancólico pero ágil
        'pentatonic_locrian': [0, 3, 5, 6, 10],  # Muy oscuro, inestable, disonante
        'lydian_pentatonic': [0, 2, 4, 6, 9],  # Onírico, etéreo, surrealista
        'augmented_pentatonic': [0, 4, 8, 10, 2],  # Brillante pero distorsionado, inestable
        'lydian_sharp5_pentatonic': [0, 2, 4, 8, 9],  # Soñador pero deforme, elegante
        'phrygian_dominant_pentatonic': [0, 1, 4, 7, 10],  # Muy oscuro, exótico, árabe-metal
        'mixolydian_b6_pentatonic': [0, 2, 5, 8, 10],  # Oscuro, modal, blues triste
        'half_whole_diminished_pentatonic': [0, 1, 3, 4, 6],  # Muy tenso, jazzy, inestable
        'altered_pentatonic': [0, 1, 3, 6, 10],  # Súper disonante, caos controlado
        'blues': [0, 3, 5, 6, 7, 10],  # Expresivo, con lamento, profundo
        'dorian': [0, 2, 3, 5, 7, 9, 10],  # Místico, menor con toque optimista
        'phrygian': [0, 1, 3, 5, 7, 8, 10],  # Oscuro, flamenco, español
        'lydian': [0, 2, 4, 6, 7, 9, 11],  # Soñador, etéreo, flotante
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],  # Alegre pero relajado, rock, blues
        'locrian': [0, 1, 3, 5, 6, 8, 10],  # Inestable, tenso, misterioso
        'whole_tone': [0, 2, 4, 6, 8, 10],  # Ambiguo, onírico, impresionista
        'diminished': [0, 2, 3, 5, 6, 8, 9, 11],  # Tenso, dramático, misterioso
        'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],  # Disonante, atonal, complejo
        'augmented': [0, 3, 4, 7, 8, 11],  # Inusual, enigmático, flotante
        'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],  # Exótico, oriental, gitano
        'double_harmonic': [0, 1, 4, 5, 7, 8, 11],  # Oriental, dramático, intenso
        'hungarian_minor': [0, 2, 3, 6, 7, 8, 11],  # Melancólico, exótico, gitano
        'hungarian_major': [0, 3, 4, 6, 7, 9, 10],
        'neapolitan_minor': [0, 1, 3, 5, 7, 8, 11],  # Dramático, oscuro, clásico
        'neapolitan_major': [0, 1, 3, 5, 7, 9, 11],  # Exótico, brillante, sorprendente
        'persian': [0, 1, 4, 5, 6, 8, 11],  # Misterioso, oriental, exótico
        'enigmatic': [0, 1, 4, 6, 8, 10, 11],  # Intrigante, complejo, misterioso
        'hindu': [0, 2, 4, 5, 7, 8, 10],  # Místico, relajado, exótico
        'japanese': [0, 1, 5, 7, 8],  # Oriental, pentatónico, sereno
        'arabic': [0, 2, 4, 5, 6, 8, 10],  # Místico, exótico, intenso
        'gypsy': [0, 2, 3, 6, 7, 8, 10],  # Apasionado, dramático, gitano
        'byzantine': [0, 1, 4, 5, 7, 8, 11],  # Antiguo, místico, solemne
        'balinese': [0, 1, 3, 7, 8],  # Etéreo, exótico, pentatónico
        'todi': [0, 1, 3, 6, 7, 8, 11],  # Introspectivo, clásico indio, místico
        'bebop_major': [0, 2, 4, 5, 7, 9, 10, 11],  # Sofisticado, fluido, jazzístico
        'bebop_minor': [0, 2, 3, 5, 7, 8, 9, 10],  # Complejo, bluesy, jazzístico
        'bebop_dominant': [0, 2, 4, 5, 7, 9, 10, 11],  # Rítmico, swing, jazzístico
        'bebop_dorian': [0, 2, 3, 5, 7, 9, 10, 11],  # Melódico, fluido, jazzístico
        'bebop_melodic_minor': [0, 2, 3, 5, 7, 8, 9, 11],  # Sofisticado, ambiguo, jazzístico
        'bebop_harmonic_minor': [0, 2, 3, 5, 7, 8, 11, 12],  # Exótico, tenso, jazzístico
        'flamenco': [0, 1, 3, 4, 5, 7, 8],  # Apasionado, español, flamenco
        'romanian_minor': [0, 2, 3, 6, 7, 9, 10],  # Melancólico, exótico, gitano
        'lydian_diminished': [0, 2, 3, 6, 7, 9, 11],  # Místico, exótico
        'javanese': [0, 1, 3, 5, 7, 8, 11],  # Místico, oriental, exótico
        'blues_major': [0, 2, 3, 4, 7, 9],  # Alegre, emotivo, bluesy
        'blues_minor': [0, 3, 5, 6, 7, 10, 12],  # Triste, expresivo, bluesy
        'lydian_augmented': [0, 2, 4, 6, 8, 9, 11],  # Brillante, futurista, luminoso
        'half_whole_diminished': [0, 1, 3, 4, 6, 7, 9, 10],  # Tenso, cromático, misterioso
        'harmonic_major': [0, 2, 4, 5, 7, 8, 11],  # Exótico, dramático, clásico
        'altered_scale': [0, 1, 3, 4, 6, 8, 10],  # Tenso, disonante, jazzístico
        'prometheus': [0, 2, 4, 6, 9, 10],  # Misterioso, moderno, innovador
        'egyptian_pentatonic': [0, 2, 5, 7, 10],  # Exótico, místico, antiguo
        'chinese_pentatonic': [0, 4, 6, 7, 11],  # Sereno, cultural, único
    }
    
    if isinstance(input_value, str):
        return scale_dictionary.get(input_value)
    elif isinstance(input_value, list) and len(input_value) == 2:
        scale_name, axis = input_value
        if scale_name in scale_dictionary and isinstance(axis, int) and 0 <= axis < 12:
            return [(2 * axis - note) % 12 for note in scale_dictionary[scale_name]]
    return None

def scale_patterns_simplified(input_value):
    # Your existing scale_patterns_simplified function stays the same
    scale_dictionary = {
        'major': [0, 2, 4, 7, 9],  # Pentatónica mayor (elimina el 4º y 7º grados)
        'minor': [0, 3, 5, 7, 10],  # Pentatónica menor (elimina el 2º y 6º grados)
        'harmonic_minor': [0, 3, 5, 7, 11],  # Mantiene el 7º grado elevado, elimina notas que generan tensión
        'melodic_minor': [0, 3, 5, 7, 9],  # Similar a pentatónica menor pero con 6ª mayor
        'pentatonic_major': [0, 2, 4, 7, 9],  # Ya es una escala simplificada
        'pentatonic_minor': [0, 3, 5, 7, 10],  # Ya es una escala simplificada
        'blues': [0, 3, 5, 7, 10],  # Simplificada a pentatónica menor (omitiendo la "blue note")
        'dorian': [0, 2, 5, 7, 10],  # Elimina el 3º y 6º grados, mantiene la 6ª mayor característica
        'phrygian': [0, 3, 5, 7, 10],  # Simplificada a pentatónica menor
        'lydian': [0, 2, 4, 6, 7],  # Mantiene la 4ª aumentada característica
        'mixolydian': [0, 2, 4, 7, 10],  # Pentatónica mixolidia (elimina el 5º y 6º grados)
        'locrian': [0, 3, 5, 6, 10],  # Mantiene intervalos clave, elimina notas adicionales
        'whole_tone': [0, 4, 8],  # Simplificada a una tríada aumentada
        'diminished': [0, 3, 6, 9],  # Simplificada a tétrada disminuida (intervalos cada tres semitonos)
        'chromatic': [0, 3, 6, 9],  # Simplificada a tétrada disminuida para representar simetría
        'augmented': [0, 4, 8],  # Simplificada a tríada aumentada
        'phrygian_dominant': [0, 1, 4, 7, 10],  # Mantiene intervalos característicos (2ª menor y 3ª mayor)
        'double_harmonic': [0, 1, 4, 5, 7, 8],  # Elimina el 7º grado para evitar tensión excesiva
        'hungarian_minor': [0, 3, 6, 7, 10],  # Mantiene intervalos exóticos clave
        'neapolitan_minor': [0, 1, 3, 7, 11],  # Mantiene intervalos distintivos (2ª menor y 7ª mayor)
        'neapolitan_major': [0, 1, 4, 7, 11],  # Mantiene intervalos distintivos (2ª menor y 3ª mayor)
        'persian': [0, 1, 4, 5, 7],  # Elimina notas para reducir semitonos consecutivos
        'enigmatic': [0, 1, 4, 7, 11],  # Mantiene intervalos clave, elimina notas intermedias
        'hindu': [0, 4, 5, 7, 9],  # Simplificada similar a pentatónica mayor con 4º grado
        'japanese': [0, 1, 5, 7],  # Mantiene intervalos característicos, elimina el último grado
        'arabic': [0, 4, 5, 6, 9],  # Simplificada para reducir semitonos consecutivos
        'gypsy': [0, 3, 6, 7, 10],  # Mantiene intervalos distintivos
        'byzantine': [0, 1, 4, 7, 10],  # Mantiene intervalos clave, elimina 7ª mayor
        'balinese': [0, 1, 7, 8],  # Simplificada para resaltar intervalos exóticos
        'todi': [0, 1, 7, 11],  # Mantiene intervalos clave, elimina notas intermedias
        'bebop_major': [0, 2, 4, 7, 9],  # Simplificada a pentatónica mayor
        'bebop_minor': [0, 3, 5, 7, 10],  # Simplificada a pentatónica menor
        'bebop_dominant': [0, 2, 4, 7, 10],  # Simplificada a pentatónica mixolidia
        'bebop_dorian': [0, 2, 5, 7, 10],  # Mantiene la 6ª mayor, elimina notas adicionales
        'bebop_melodic_minor': [0, 3, 5, 7, 9],  # Simplificada similar a pentatónica menor
        'bebop_harmonic_minor': [0, 3, 5, 7, 11],  # Mantiene el 7º grado elevado
        'flamenco': [0, 3, 7, 8],  # Mantiene intervalos flamencos clave
        'romanian_minor': [0, 3, 6, 7, 10],  # Mantiene intervalos distintivos
        'javanese': [0, 5, 7],  # Simplificada a pentatónica
        'blues_major': [0, 2, 3, 7, 9],  # Mantiene la "blue note" (3ª menor)
        'blues_minor': [0, 3, 5, 7, 10],  # Ya es similar a pentatónica menor
        'lydian_augmented': [0, 4, 8, 9],  # Mantiene la 4ª aumentada y 5ª aumentada
        'half_whole_diminished': [0, 3, 6, 9],  # Simplificada a tétrada disminuida
        'harmonic_major': [0, 4, 5, 7, 11],  # Elimina grados que generan tensión
        'altered_scale': [0, 3, 6, 10],  # Mantiene intervalos más representativos
        'prometheus': [0, 4, 6, 9],  # Mantiene intervalos clave
        'egyptian_pentatonic': [0, 5, 7],  # Ya es una escala simplificada
        'chinese_pentatonic': [0, 4, 7, 11],  # Mantiene intervalos representativos
    }
    
    if isinstance(input_value, str):
        return scale_dictionary.get(input_value)
    elif isinstance(input_value, list) and len(input_value) == 2:
        scale_name, axis = input_value
        if scale_name in scale_dictionary and isinstance(axis, int) and 0 <= axis < 12:
            return [(2 * axis - note) % 12 for note in scale_dictionary[scale_name]]
    return None

def merge_images_vertically(images):
    """Merge a list of images vertically."""
    if not images:
        raise ValueError("The image list cannot be empty.")
    
    total_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)
    merged_image = Image.new('RGB', (total_width, total_height))
    
    y_offset = 0
    for img in images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height
    
    return merged_image

def merge_images_grid(images):
    """Merge a list of images into a grid with 2 images per row."""
    if not images:
        raise ValueError("The image list cannot be empty.")
    
    rows = [images[i:i+2] for i in range(0, len(images), 2)]
    total_width = 0
    total_height = 0
    row_sizes = []
    
    for row in rows:
        row_width = sum(img.width for img in row)
        row_height = max(img.height for img in row)
        row_sizes.append((row_width, row_height))
        total_width = max(total_width, row_width)
        total_height += row_height
    
    merged_image = Image.new('RGB', (total_width, total_height))
    y_offset = 0
    
    for index, row in enumerate(rows):
        x_offset = 0
        row_height = row_sizes[index][1]
        for img in row:
            merged_image.paste(img, (x_offset, y_offset))
            x_offset += img.width
        y_offset += row_height
    
    return merged_image

# Helper functions that use the Fretboard class
def init_fretboard(tuning=None):
    """Initialize a fretboard with optional tuning."""
    fb = Fretboard(tuning)
    return fb.init_fretboard()

def draw_scale(draw_obj, root_note='C', scale_type='major'):
    """Draw a scale on the fretboard."""
    # Extract the Fretboard instance from the draw object
    fb = draw_obj._fb if hasattr(draw_obj, '_fb') else Fretboard()
    pattern = scale_patterns(scale_type)
    if not pattern:
        return draw_obj
    
    draw_obj = fb.fretboard_title(draw_obj, f"Scale: {root_note} {scale_type}")
    root_note_index = fb.chromatic_scale.index(root_note)
    
    interval_colors = {
        0: 'red', 2: 'blue', 4: 'green', 5: 'purple',
        7: 'yellow', 9: 'orange', 11: 'pink'
    }
    default_color = 'lightblue'
    
    for string_index, string_notes in enumerate(fb.fretboard):
        for fret, note in enumerate(string_notes):
            note_index = (fb.chromatic_scale.index(note) - root_note_index) % 12
            if any((note_index + 12 * octave) % 12 in pattern for octave in range(2)):
                interval_index = next(i for i, interval in enumerate(pattern) if (interval % 12) == note_index)
                if interval_index in [0, 2, 4, 6]:
                    color = interval_colors.get(pattern[interval_index], default_color)
                else:
                    color = default_color
                fb.draw_note_on_fretboard(draw_obj, string_index, fret, color, note)
    
    return draw_obj

def draw_arpeggio(draw_obj, root_note='C', arpeggio_type='maj'):
    """Draw an arpeggio on the fretboard."""
    fb = draw_obj._fb if hasattr(draw_obj, '_fb') else Fretboard()
    pattern = chord_patterns(arpeggio_type)
    if not pattern:
        return draw_obj
    
    draw_obj = fb.fretboard_title(draw_obj, f"Chord: {root_note} {arpeggio_type}")
    root_note_index = fb.chromatic_scale.index(root_note)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow']
    
    for string_index, string_notes in enumerate(fb.fretboard):
        for fret, note in enumerate(string_notes):
            note_index = (fb.chromatic_scale.index(note) - root_note_index) % 12
            if any((note_index + 12 * octave) % 12 in pattern for octave in range(2)):
                interval_index = next(i for i, interval in enumerate(pattern) if (interval % 12) == note_index)
                color_index = interval_index % len(colors)
                fb.draw_note_on_fretboard(draw_obj, string_index, fret, colors[color_index], note)
    
    return draw_obj

def draw_black_scale(draw_obj, root_note='C', scale_type='major', simplified=False):
    """Draw a black scale on the fretboard."""
    fb = draw_obj._fb if hasattr(draw_obj, '_fb') else Fretboard()
    if simplified:
        pattern = scale_patterns_simplified(scale_type)
    else:
        pattern = scale_patterns(scale_type)
    
    if not pattern:
        return draw_obj
    
    root_note_index = fb.chromatic_scale.index(root_note)
    interval_colors = {
        0: 'black', 2: 'black', 4: 'black', 5: 'black',
        7: 'black', 9: 'black', 11: 'black'
    }
    default_color = 'black'
    
    for string_index, string_notes in enumerate(fb.fretboard):
        for fret, note in enumerate(string_notes):
            note_index = (fb.chromatic_scale.index(note) - root_note_index) % 12
            if any((note_index + 12 * octave) % 12 in pattern for octave in range(2)):
                interval_index = next(i for i, interval in enumerate(pattern) if (interval % 12) == note_index)
                if interval_index in [0, 2, 4, 6]:
                    color = interval_colors.get(pattern[interval_index], default_color)
                else:
                    color = default_color
                fb.draw_note_on_fretboard(draw_obj, string_index, fret, color, note, text='white')
    
    return draw_obj

# For backward compatibility, create a default instance
_default_fretboard = Fretboard()