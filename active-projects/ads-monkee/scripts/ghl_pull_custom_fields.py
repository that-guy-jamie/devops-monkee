import json
import os
from pathlib import Path

from backend.integrations.ghl_client import GHLClient


def main() -> None:
    out_dir = Path(os.getenv("GHL_OUT", ".cursor/.agent-tools"))
    out_dir.mkdir(parents=True, exist_ok=True)

    client = GHLClient()

    fields = client.list_custom_fields()
    (out_dir / "ghl_custom_fields.json").write_text(json.dumps(fields, indent=2))

    opp_fields = client.list_opportunity_custom_fields()
    (out_dir / "ghl_opportunity_custom_fields.json").write_text(json.dumps(opp_fields, indent=2))

    print("Saved:", str(out_dir / "ghl_custom_fields.json"), str(out_dir / "ghl_opportunity_custom_fields.json"))


if __name__ == "__main__":
    main()


