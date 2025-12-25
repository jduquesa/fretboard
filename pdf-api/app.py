# app.py
import io
import logging
import traceback
from datetime import datetime

from quart import Quart, request, send_file, jsonify

# Import from the updated fretboard_module
from fretboard_module import (
    Fretboard,  # Import the Fretboard class
    init_fretboard,
    draw_scale,
    draw_arpeggio,
    draw_black_scale,
    merge_images_vertically,
    find_chords_in_scale,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # stdout
        logging.FileHandler('app.log')  # Optional: also log to file
    ]
)
logger = logging.getLogger(__name__)

app = Quart(__name__)


def image_to_pdf_bytes(image) -> io.BytesIO:
    """
    Convert a single PIL.Image to a PDF in-memory and return a BytesIO.
    """
    buf = io.BytesIO()
    # If image is not RGB, convert to avoid some PDF issues
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(buf, format="PDF")
    buf.seek(0)
    return buf


# ---------- Builders ----------

def build_scale_image(payload: list, tuning=None):
    """
    payload: [["A", "harmonic_minor"], ["D", "dorian"], ...]
    tuning: Optional tuning parameter
    Returns a single merged PIL.Image.
    """
    if not payload:
        raise ValueError("Empty payload for scale endpoint")

    images = []
    for item in payload:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"Invalid scale item: {item!r}")
        note, scale_type = item
        
        # Create Fretboard instance with tuning
        fb = Fretboard(tuning)
        draw_obj = fb.init_fretboard()
        # Attach the Fretboard instance to the draw object for later use
        draw_obj._fb = fb
        
        img = draw_scale(draw_obj, note, scale_type).image
        images.append(img)

    if len(images) == 1:
        return images[0]
    return merge_images_vertically(images)


def build_chord_image(payload: list, tuning=None):
    """
    payload: [["A#", "mmaj7"], ["F#", "min7"], ...]
    tuning: Optional tuning parameter
    Returns a single merged PIL.Image.
    """
    if not payload:
        raise ValueError("Empty payload for chord endpoint")

    images = []
    for item in payload:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"Invalid chord item: {item!r}")
        note, chord_type = item
        
        # Create Fretboard instance with tuning
        fb = Fretboard(tuning)
        draw_obj = fb.init_fretboard()
        draw_obj._fb = fb
        
        img = draw_arpeggio(draw_obj, root_note=note, arpeggio_type=chord_type).image
        images.append(img)

    if len(images) == 1:
        return images[0]
    return merge_images_vertically(images)


def build_mixed_image(payload: list, tuning=None):
    """
    payload: [
      {"scale": ["A", "harmonic_minor"], "chord": ["B", "mmaj7"]},
      {"scale": ["G", "major"], "chord": ["F#", "7"]},
      ...
    ]
    tuning: Optional tuning parameter
    Returns a single merged PIL.Image.
    """
    if not payload:
        raise ValueError("Empty payload for mixed endpoint")

    images = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid mixed item (not dict): {item!r}")
        if "scale" not in item or "chord" not in item:
            raise ValueError(f"Missing 'scale' or 'chord' key in: {item!r}")

        scale_pair = item["scale"]
        chord_pair = item["chord"]

        if (
            not isinstance(scale_pair, (list, tuple))
            or len(scale_pair) != 2
            or not isinstance(chord_pair, (list, tuple))
            or len(chord_pair) != 2
        ):
            raise ValueError(f"Invalid scale/chord pair in: {item!r}")

        scale_note, scale_type = scale_pair
        chord_note, chord_type = chord_pair

        # Create Fretboard instance with tuning
        fb = Fretboard(tuning)
        draw_obj = fb.init_fretboard()
        draw_obj._fb = fb
        
        draw_with_scale = draw_black_scale(draw_obj, scale_note, scale_type)
        img = draw_arpeggio(
            draw_with_scale,
            root_note=chord_note,
            arpeggio_type=chord_type,
        ).image
        images.append(img)

    if len(images) == 1:
        return images[0]
    return merge_images_vertically(images)


def extract_payload(data):
    """
    Extract payload from request data.
    Supports both formats:
    1. Direct list: [["A", "major"], ...]
    2. Dictionary with 'data' key: {"data": [["A", "major"], ...], "tuning": [...]}
    
    Returns: (payload, tuning)
    """
    if isinstance(data, dict):
        if 'data' not in data:
            raise ValueError("Missing 'data' key in payload")
        payload = data['data']
        tuning = data.get('tuning') or data.get('tunning')  # Support both spellings
        logger.info(f"Extracted payload from dict format, tuning: {tuning}")
        return payload, tuning
    elif isinstance(data, list):
        logger.info("Extracted payload from direct list format")
        return data, None
    else:
        raise ValueError(f"Invalid payload type. Expected dict with 'data' key or list, got {type(data).__name__}")


# ---------- API endpoints ----------

@app.before_request
async def log_request_info():
    """Log request details for all incoming requests."""
    try:
        logger.info(f"Received request: {request.method} {request.path}")
        logger.info(f"Request headers: {dict(request.headers)}")
        
        # Log query parameters if any
        if request.args:
            logger.info(f"Query parameters: {dict(request.args)}")
        
        # Log request body for POST requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                try:
                    body = await request.get_json(silent=True)
                    if body:
                        # Log a truncated version if body is large
                        body_str = str(body)
                        if len(body_str) > 500:
                            logger.info(f"Request body (truncated): {body_str[:500]}...")
                        else:
                            logger.info(f"Request body: {body_str}")
                except Exception as e:
                    logger.warning(f"Failed to parse JSON body: {e}")
            elif content_type:
                logger.info(f"Content-Type: {content_type} (body not logged)")
    except Exception as e:
        logger.error(f"Error in request logging: {e}")


@app.after_request
async def log_response_info(response):
    """Log response details."""
    logger.info(f"Response status: {response.status_code}")
    logger.info(f"Response Content-Type: {response.content_type}")
    return response


@app.post("/api/endpoint-scale")
async def endpoint_scale():
    """
    Expects JSON body like:
      Option 1: Direct list format
        [["A","harmonic_minor"],["D","dorian"]]
      
      Option 2: Dictionary format (new)
        {"data": [["A","harmonic_minor"],["D","dorian"]], "tuning": ["E","A","D","G","B","E"]}
    
    Returns a PDF merging all the generated scale images vertically.
    """
    logger.info("Processing /api/endpoint-scale request")
    
    try:
        data = await request.get_json()
        if not data:
            logger.warning("Empty request body received")
            return jsonify({"error": "Request body is empty"}), 400
        
        logger.info(f"Request data type: {type(data).__name__}")
        
        # Extract payload from either format
        payload, tuning = extract_payload(data)
        
        if not isinstance(payload, list):
            logger.warning(f"Invalid payload type after extraction: {type(payload)}")
            return jsonify({"error": "Payload must be a list"}), 400
        
        if not payload:
            logger.warning("Empty payload list received")
            return jsonify({"error": "Payload list cannot be empty"}), 400
            
        logger.info(f"Processing {len(payload)} scale items, tuning: {tuning}")
        logger.info(f"Scale items: {payload}")
        
        merged_image = build_scale_image(payload, tuning)
        pdf_bytes = image_to_pdf_bytes(merged_image)

        filename = f"scales_{datetime.utcnow():%Y%m%d_%H%M%S}.pdf"
        logger.info(f"Successfully generated PDF: {filename}")
        
        return await send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=False,
            attachment_filename=filename,
        )
        
    except ValueError as e:
        # This is a validation error - safe to return to client
        logger.warning(f"Validation error in endpoint-scale: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Internal error - log full details but return generic message
        logger.error(f"Internal error in endpoint-scale: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500

@app.post("/api/endpoint-chordinscale")
async def endpoint_chordinscale():
    """
    Expects JSON body like:
      Option 1: Direct list format
        ["A","harmonic_minor"]
      
      Option 2: Dictionary format (new)
        {"data": ["A","harmonic_minor"]}
    
    Returns a dictionary with all the chords within the scale.
    """
    logger.info("Processing /api/endpoint-scale request")
    
    try:
        data = await request.get_json()
        if not data:
            logger.warning("Empty request body received")
            return jsonify({"error": "Request body is empty"}), 400
        
        logger.info(f"Request data type: {type(data).__name__}")
        
        # Extract payload from either format
        payload = extract_payload(data)[0]
        
        if not (isinstance(payload, list) or isinstance(payload, tuple)):
            logger.warning(f"Invalid payload type after extraction: {type(payload)}")
            return jsonify({"error": "Payload must be a list"}), 400
        
        if not payload:
            logger.warning("Empty payload list received")
            return jsonify({"error": "Payload list cannot be empty"}), 400
            
        logger.info(f"Processing {len(payload)} scale items")
        logger.info(f"Scale items: {payload}")
        
        chords_in_scale = find_chords_in_scale(*payload[0])
        
        
        return jsonify(chords_in_scale)
        
    except ValueError as e:
        # This is a validation error - safe to return to client
        logger.warning(f"Validation error in endpoint-scale: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Internal error - log full details but return generic message
        logger.error(f"Internal error in endpoint-scale: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500



@app.post("/api/endpoint-chord")
async def endpoint_chord():
    """
    Expects JSON body like:
      Option 1: Direct list format
        [["A#", "mmaj7"], ["F#", "min7"]]
      
      Option 2: Dictionary format (new)
        {"data": [["A#", "mmaj7"], ["F#", "min7"]], "tuning": ["E","A","D","G","B","E"]}
    
    Returns a PDF merging all chord images vertically.
    """
    logger.info("Processing /api/endpoint-chord request")
    
    try:
        data = await request.get_json()
        if not data:
            logger.warning("Empty request body received")
            return jsonify({"error": "Request body is empty"}), 400
        
        logger.info(f"Request data type: {type(data).__name__}")
        
        # Extract payload from either format
        payload, tuning = extract_payload(data)
        
        if not isinstance(payload, list):
            logger.warning(f"Invalid payload type after extraction: {type(payload)}")
            return jsonify({"error": "Payload must be a list"}), 400
        
        if not payload:
            logger.warning("Empty payload list received")
            return jsonify({"error": "Payload list cannot be empty"}), 400
            
        logger.info(f"Processing {len(payload)} chord items, tuning: {tuning}")
        logger.info(f"Chord items: {payload}")
        
        merged_image = build_chord_image(payload, tuning)
        pdf_bytes = image_to_pdf_bytes(merged_image)

        filename = f"chords_{datetime.utcnow():%Y%m%d_%H%M%S}.pdf"
        logger.info(f"Successfully generated PDF: {filename}")
        
        return await send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=False,
            attachment_filename=filename,
        )
        
    except ValueError as e:
        # This is a validation error - safe to return to client
        logger.warning(f"Validation error in endpoint-chord: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Internal error - log full details but return generic message
        logger.error(f"Internal error in endpoint-chord: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.post("/api/endpoint-mixed")
async def endpoint_mixed():
    """
    Expects JSON body like:
      Option 1: Direct list format
        [
          {"scale": ["A","harmonic_minor"], "chord": ["B", "mmaj7"]},
          {"scale": ["G","major"], "chord": ["F#", "7"]}
        ]
      
      Option 2: Dictionary format (new)
        {
          "data": [
            {"scale": ["A","harmonic_minor"], "chord": ["B", "mmaj7"]},
            {"scale": ["G","major"], "chord": ["F#", "7"]}
          ],
          "tuning": ["E","A","D","G","B","E"]
        }
    
    Returns a PDF merging each mixed image vertically.
    """
    logger.info("Processing /api/endpoint-mixed request")
    
    try:
        data = await request.get_json()
        if not data:
            logger.warning("Empty request body received")
            return jsonify({"error": "Request body is empty"}), 400
        
        logger.info(f"Request data type: {type(data).__name__}")
        
        # Extract payload from either format
        payload, tuning = extract_payload(data)
        
        if not isinstance(payload, list):
            logger.warning(f"Invalid payload type after extraction: {type(payload)}")
            return jsonify({"error": "Payload must be a list"}), 400
        
        if not payload:
            logger.warning("Empty payload list received")
            return jsonify({"error": "Payload list cannot be empty"}), 400
            
        logger.info(f"Processing {len(payload)} mixed items, tuning: {tuning}")
        logger.info(f"Mixed items: {payload}")
        
        merged_image = build_mixed_image(payload, tuning)
        pdf_bytes = image_to_pdf_bytes(merged_image)

        filename = f"mixed_{datetime.utcnow():%Y%m%d_%H%M%S}.pdf"
        logger.info(f"Successfully generated PDF: {filename}")
        
        return await send_file(
            pdf_bytes,
            mimetype="application/pdf",
            as_attachment=False,
            attachment_filename=filename,
        )
        
    except ValueError as e:
        # This is a validation error - safe to return to client
        logger.warning(f"Validation error in endpoint-mixed: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Internal error - log full details but return generic message
        logger.error(f"Internal error in endpoint-mixed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
async def not_found(error):
    logger.warning(f"404 error: {request.path}")
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(405)
async def method_not_allowed(error):
    logger.warning(f"405 error: {request.method} {request.path}")
    return jsonify({"error": "Method not allowed"}), 405


# Health check endpoint
@app.route("/health")
async def health_check():
    logger.info("Health check requested")
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    logger.info("Starting application...")
    # For local dev only; in Docker we'll use hypercorn
    app.run(host="0.0.0.0", port=5000)