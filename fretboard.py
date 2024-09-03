from PIL import Image, ImageDraw, ImageFont
import random

# Define the tuning for a 7-string guitar (from lowest to highest string)
tuning = ['A', 'E', 'A', 'D', 'G', 'B', 'E']

# Define the notes in a chromatic scale
chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Define frets that have position markers (dots)
position_marker_frets = [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]

# Set up image dimensions
fretboard_width = 1300
fretboard_height = 240
border_thickness = 50
string_spacing = fretboard_height // 8
fret_spacing = fretboard_width // 25

# Function to get the note at a specific fret
def note_at_fret(tuning_note, fret):
    note_index = chromatic_scale.index(tuning_note)
    return chromatic_scale[(note_index + fret) % 12]

# Generate the notes for each string
fretboard = []
for string in tuning:
    fretboard.append([note_at_fret(string, fret) for fret in range(25)])  # 25 positions including open string

# Load a font
fontsize = 16
font = ImageFont.truetype('Arial.ttf', fontsize)
# font = ImageFont.load_default()

# Function to draw notes on the fretboard
def draw_note_on_fretboard(draw, fretboard, string_index, fret, color, note):
    x = border_thickness + fret * fret_spacing + fret_spacing // 2
    y = border_thickness + (7 - string_index) * string_spacing
    radius = 12
    draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill=color)
    
    # Use textbbox to calculate text width and height
    text_bbox = draw.textbbox((0, 0), note, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # draw.text((x - text_width // 2, y - text_height // 2), note, fill='black', font=font)
    draw.text((x - text_width // 2, y - text_height), note, fill='black', font=font)


def init_fretboard():
    # Create an image with a larger black background to frame the fretboard
    image = Image.new('RGB', (fretboard_width + 2 * border_thickness, fretboard_height + 2 * border_thickness), color='black')
    draw = ImageDraw.Draw(image)

    # Draw the fretboard background in dark brown
    draw.rectangle([border_thickness, border_thickness, border_thickness + fretboard_width, border_thickness + (fretboard_height)], fill='#150000')

    # Draw frets
    for fret in range(25):  # 24 frets + the zero fret
        x = border_thickness + fret * fret_spacing
        line_width = 16 if fret == 1 else 2  # Zero fret thicker
        draw.line([(x, border_thickness + 20), (x, border_thickness + fretboard_height - 20)], fill='darkgray', width=line_width)

    # Draw strings with varying thickness (low strings thicker, at the bottom)
    for string in range(7):  # 7 strings
        y = border_thickness + (7 - string) * string_spacing
        string_width = 6 if string == 0 else 4  # Thickest for the lowest string
        draw.line([(border_thickness, y), (border_thickness + fretboard_width, y)], fill='lightgray', width=string_width)

    # Draw position markers (dots)
    for fret in position_marker_frets:
        x = border_thickness + fret * fret_spacing + fret_spacing // 2
        if fret == 12:
            # Draw two dots for the 12th fret
            y1 = border_thickness + fretboard_height // 3
            y2 = border_thickness + 2 * fretboard_height // 3
            draw.ellipse([(x - 10, y1 - 10), (x + 10, y1 + 10)], fill='white')
            draw.ellipse([(x - 10, y2 - 10), (x + 10, y2 + 10)], fill='white')
        else:
            y = border_thickness + fretboard_height // 2
            draw.ellipse([(x - 10, y - 10), (x + 10, y + 10)], fill='white')

    # Draw fret numbers above the fretboard
    for fret in range(25):
        x = border_thickness + fret * fret_spacing + fret_spacing // 2
        text = str(fret)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((x - text_width // 2, border_thickness - text_height - 15), text, fill='white', font=font)

    # Draw string tuning on the left side outside the fretboard
    for string in range(7):
        y = border_thickness + (7 - string) * string_spacing - string_spacing // 2
        text = tuning[string]
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((border_thickness - text_width - 20, (y - text_height) + 35 // 2), text, fill='white', font=font)
    # Attach the image to the draw object
    draw.image = image
    return draw

# function to write a title in the image
def fretboard_title(draw, title):
    if not title:
        return draw
    # Get the bounding box of the text
    bbox = draw.textbbox((0, 0), title, font=font)

    # Calculate the text width and height
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]


    # Calculate the position for the text to be centered
    image_width, image_height = (fretboard_width + 2 * border_thickness, fretboard_height + 2 * border_thickness)
    text_x = (image_width - text_width) / 2
    text_y = (image_height - text_height - 40)

    # Add the text to the image
    draw.text((text_x, text_y), title, font=font, fill=(255, 255, 255))  # Adjust fill color as needed
    return draw

# Function for chord patterns with intervals
def chord_patterns(input_value):
    """
    Fetches chord semitone patterns from a dictionary or returns the inverted semitones.

    Parameters:
    input_value (str or list): If a string, it's the name of the chord. If a list, it should contain [chord_name, axis].

    Returns:
    list or None: Returns a list of semitones for the chord or its inversion, or None if the chord name is not found.
    """
    # Define the chord patterns dictionary
    chord_dictionary = {
        'maj': [0, 4, 7],
        'min': [0, 3, 7],
        'dim': [0, 3, 6],
        'aug': [0, 4, 8],
        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        'dom7': [0, 4, 7, 10],
        'dim7': [0, 3, 6, 9],
        'min7b5': [0, 3, 6, 10],
        'sus2': [0, 2, 7],
        'sus4': [0, 5, 7],
        'maj6': [0, 4, 7, 9],
        'min6': [0, 3, 7, 9],
        '9': [0, 4, 7, 10, 14],
        'maj9': [0, 4, 7, 11, 14],
        'min9': [0, 3, 7, 10, 14],
        '11': [0, 4, 7, 10, 14, 17],
        '13': [0, 4, 7, 10, 14, 21],
        'maj13': [0, 4, 7, 11, 14, 21],
        'add9': [0, 4, 7, 14],
        'add11': [0, 4, 7, 17],
        'add13': [0, 4, 7, 21],
        '7sus4': [0, 5, 7, 10],
        '6sus4': [0, 5, 7, 9],
        '7b5': [0, 4, 6, 10],
        '7#5': [0, 4, 8, 10],
        'minmaj7': [0, 3, 7, 11],
        'maj7b5': [0, 4, 6, 11],
        'maj7#5': [0, 4, 8, 11],
        '9sus4': [0, 5, 7, 10, 14],
        'maj9#11': [0, 4, 7, 11, 14, 18],
    }
    
    # Handle the input based on its type
    if isinstance(input_value, str):
        # Return the chord pattern if it exists
        return chord_dictionary.get(input_value)
    elif isinstance(input_value, list) and len(input_value) == 2:
        chord_name, axis = input_value
        # Check if the chord name exists and the axis is a valid integer
        if chord_name in chord_dictionary and isinstance(axis, int) and 0 <= axis < 12:
            # Perform the inversion
            return [(2 * axis - note) % 12 for note in chord_dictionary[chord_name]]
    # Return None if the input does not match expected formats or values
    return None

# Example: Draw notes on the fretboard (e.g., a complex arpeggio)
def draw_arpeggio(draw = init_fretboard(), root_note = 'C', arpeggio_type = 'maj'):
    pattern = chord_patterns(arpeggio_type)
    if not pattern:
        return
    draw = fretboard_title(draw, f"{root_note} {arpeggio_type}")
    root_note_index = chromatic_scale.index(root_note)
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'yellow']  # Different colors for each interval
    
    for string_index, string_notes in enumerate(fretboard):
        for fret, note in enumerate(string_notes):
            note_index = (chromatic_scale.index(note) - root_note_index) % 12
            if any((note_index + 12 * octave) % 12 in pattern for octave in range(2)):
                interval_index = next(i for i, interval in enumerate(pattern) if (interval % 12) == note_index)
                color_index = interval_index % len(colors)
                draw_note_on_fretboard(draw, fretboard, string_index, fret, colors[color_index], note)

    return draw.image

# Dictionary for scale patterns with intervals
def scale_patterns(input_value):
    """
    Fetches scale patterns from a dictionary or returns the inverted scales.

    Parameters:
    input_value (str or list): If a string, it's the name of the scale. If a list, it should contain [scale_name, axis].

    Returns:
    list or None: Returns a list of semitones for the scale or its inversion, or None if the scale name is not found.
    """
    # Define the scale patterns dictionary
    scale_dictionary = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
        'melodic_minor': [0, 2, 3, 5, 7, 9, 11],
        'pentatonic_major': [0, 2, 4, 7, 9],
        'pentatonic_minor': [0, 3, 5, 7, 10],
        'blues': [0, 3, 5, 6, 7, 10],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
        'lydian': [0, 2, 4, 6, 7, 9, 11],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'locrian': [0, 1, 3, 5, 6, 8, 10],
        'whole_tone': [0, 2, 4, 6, 8, 10],
        'diminished': [0, 2, 3, 5, 6, 8, 9, 11],
        'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        'augmented': [0, 3, 4, 7, 8, 11],
        'phrygian_dominant': [0, 1, 4, 5, 7, 8, 10],
        'double_harmonic': [0, 1, 4, 5, 7, 8, 11],
        'hungarian_minor': [0, 2, 3, 6, 7, 8, 11],
        'neapolitan_minor': [0, 1, 3, 5, 7, 8, 11],
        'neapolitan_major': [0, 1, 3, 5, 7, 9, 11],
        'persian': [0, 1, 4, 5, 6, 8, 11],
        'enigmatic': [0, 1, 4, 6, 8, 10, 11],
        'hindu': [0, 2, 4, 5, 7, 8, 10],
        'japanese': [0, 1, 5, 7, 8],
        'arabic': [0, 2, 4, 5, 6, 8, 10],
        'gypsy': [0, 2, 3, 6, 7, 8, 10],
        'byzantine': [0, 1, 4, 5, 7, 8, 11],
        'balinese': [0, 1, 3, 7, 8],
        'todi': [0, 1, 3, 6, 7, 8, 11],
        'bebop_major': [0, 2, 4, 5, 7, 9, 10, 11],
        'bebop_minor': [0, 2, 3, 5, 7, 8, 9, 10],
        'bebop_dominant': [0, 2, 4, 5, 7, 9, 10, 11],
        'bebop_dorian': [0, 2, 3, 5, 7, 9, 10, 11],
        'bebop_melodic_minor': [0, 2, 3, 5, 7, 8, 9, 11],
        'bebop_harmonic_minor': [0, 2, 3, 5, 7, 8, 11, 12],
        'flamenco': [0, 1, 3, 4, 5, 7, 8],
        'romanian_minor': [0, 2, 3, 6, 7, 9, 10],
        'javanese': [0, 1, 3, 5, 7, 8, 11],
        'blues_major': [0, 2, 3, 4, 7, 9],
        'blues_minor': [0, 3, 5, 6, 7, 10, 12]
    }
    
    # Handle the input based on its type
    if isinstance(input_value, str):
        # Return the scale pattern if it exists
        return scale_dictionary.get(input_value)
    elif isinstance(input_value, list) and len(input_value) == 2:
        scale_name, axis = input_value
        # Check if the scale name exists and the axis is a valid integer
        if scale_name in scale_dictionary and isinstance(axis, int) and 0 <= axis < 12:
            # Perform the inversion
            return [(2 * axis - note) % 12 for note in scale_dictionary[scale_name]]
    # Return None if the input does not match expected formats or values
    return None

# Function to draw scales on the fretboard
def draw_scale(draw = init_fretboard(), root_note = 'C', scale_type = 'major'):
    pattern = scale_patterns(scale_type)
    if not pattern:
        return
    draw = fretboard_title(draw, f"{root_note} {scale_type}")
    root_note_index = chromatic_scale.index(root_note)

    # Define specific colors for the intervals
    interval_colors = {
        0: 'red',   # Root
        2: 'blue',  # Second
        4: 'green', # Third
        5: 'purple',# Fourth
        7: 'yellow',# Fifth
        9: 'orange',# Sixth
        11: 'pink'  # Seventh
    }
    default_color = 'lightblue'  # Default color for other intervals
    
    for string_index, string_notes in enumerate(fretboard):
        for fret, note in enumerate(string_notes):
            note_index = (chromatic_scale.index(note) - root_note_index) % 12
            if any((note_index + 12 * octave) % 12 in pattern for octave in range(2)):
                interval_index = next(i for i, interval in enumerate(pattern) if (interval % 12) == note_index)
                
                # Check if the interval is in the highlighted intervals and select the corresponding color
                if interval_index in [0, 2, 4, 6]:  # Root (0), Third (4), Fifth (7), Seventh (11) intervals
                    color = interval_colors.get(pattern[interval_index], default_color)
                else:
                    color = default_color
                
                draw_note_on_fretboard(draw, fretboard, string_index, fret, color, note)
    return draw.image

# Function to draw arpeggios in specified zones on the fretboard
def draw_arpeggios_zones(draw = init_fretboard(), zones = [['C', 'min', 5, 12, 1, 7]]):
    # List of colors to cycle through
    color_cycle = ['red', 'blue', 'green', 'purple', 'orange', 'yellow', 'pink', 'cyan', 'magenta']
    color_index = 0
    title = ""
    for zone in zones:
        title += f" {zone[0]}{zone[1]} " 
    draw = fretboard_title(draw, f"{title}")
    # Function to generate a random color
    def get_random_color():
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # Iterate through each specified zone
    for zone in zones:
        note, chord_type, start_fret, end_fret, start_string, end_string = zone

        # Get the pattern for the chord and the root note index
        pattern = chord_patterns(chord_type)
        # Validate if chord type exists in the dictionary
        if not pattern:
            continue

        root_note_index = chromatic_scale.index(note)
        
        # Choose a color strategy: uncomment one of the following lines
        # color = color_cycle[color_index % len(color_cycle)]  # Cycle through predefined colors
        color = get_random_color()  # Generate a random color
        
        # Update the color index for the next zone
        color_index += 1
        
        # Iterate over the string and fret range specified in the zone
        for string_index in range(start_string - 1, end_string):
            string_notes = fretboard[string_index]
            for fret in range(start_fret, end_fret + 1):
                note_at_fret = string_notes[fret]
                note_index = (chromatic_scale.index(note_at_fret) - root_note_index) % 12
                # Check if the note at the fret is part of the chord pattern
                if any((note_index + 12 * octave) % 12 in pattern for octave in range(2)):
                    draw_note_on_fretboard(draw, fretboard, string_index, fret, color, note_at_fret)
    return draw.image


def merge_images_vertically(images):
    """
    Merge a list of images vertically (top to bottom).
    
    :param images: List of Pillow Image objects to be merged.
    :return: A new Pillow Image object with all images stacked vertically.
    """
    if not images:
        raise ValueError("The image list cannot be empty.")
    
    # Calculate the total width and height for the merged image
    total_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)
    
    # Create a new image with the calculated dimensions
    merged_image = Image.new('RGB', (total_width, total_height))
    
    # Paste images one below the other
    y_offset = 0
    for img in images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height
    
    return merged_image

# Example usage of draw_arpeggios_zones
# [Note, chord, fret start, fret end, string start, string end]
zones = [
    # Diminished to Minor Resolution
    ['C#', 'min', 9, 12, 1, 7], # C#m: Fret 9-12, Strings 1-6
    ['C', 'dim', 8, 9, 1, 7],   # Cdim: Fret 8-9, Strings 1-6
    ['B', 'min', 7, 9, 1, 7],   # Bm: Fret 7-9, Strings 1-6
    ['E', 'aug', 1, 5, 1, 7], # Eaug: Fret 12-15, Strings 1-6
    ['A', 'maj', 5, 8, 1, 7],   # Amaj: Fret 5-8, Strings 1-6
]

# Call the function to draw arpeggios in the specified zones
# draw_arpeggios_zones(init_fretboard(), zones).show()

# Draw a scale, for example, a 'C# major' scale
# draw_scale(draw, 'C#', 'major').show()

# Draw a complex arpeggio, for example, a 'maj9#11'
# draw_arpeggio(init_fretboard(), 'C#', 'maj9#11').show()

# Save the image
# draw_arpeggio(init_fretboard(), 'C#', 'maj9#11').save('7_string_fretboard_complex_arpeggio.png')


merged_image = merge_images_vertically([draw_scale(init_fretboard(), 'A', 'harmonic_minor'),
draw_scale(init_fretboard(), 'D', 'dorian'),
draw_scale(init_fretboard(), 'E', 'phrygian_dominant'),
draw_scale(init_fretboard(), 'F', 'lydian'),
draw_scale(init_fretboard(), 'B', ['locrian',0]),
draw_scale(init_fretboard(), 'A', 'harmonic_minor')])

merged_image.show()  # Display the merged image