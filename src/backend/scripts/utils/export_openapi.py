"""
Export OpenAPI specification to JSON file
"""

import json
import sys
from pathlib import Path

# Get Backend directory (2 levels up from scripts/utils/)
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from core.app import create_app


def export_openapi():
    """Export the current OpenAPI specification to a JSON file"""
    app = create_app()
    openapi_spec = app.openapi()

    # Write to Backend directory
    output_path = backend_dir / "openapi.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

    print(f"OpenAPI spec exported to: {output_path}")


if __name__ == "__main__":
    export_openapi()
