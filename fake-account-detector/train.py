"""Train and select the model using only the training-source validation split."""
from pathlib import Path

import yaml

from src.models.train_model import train_and_select


def main() -> None:
    root = Path(__file__).resolve().parent
    config = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8"))
    data, model = config["data"], config["model"]
    result = train_and_select(
        root / data["fake_train"], root / data["real_train"],
        root / model["artifact"], root / model["selection_results"],
        seed=int(config["seed"]), validation_size=float(config["validation_size"]),
    )
    print(f"Selected: {result['selected_model']}")
    for name, metrics in result["validation_results"].items():
        print(f"{name}: accuracy={metrics['accuracy']:.3f}, F1(fake)={metrics['f1_fake']:.3f}, ROC-AUC={metrics.get('roc_auc', float('nan')):.3f}")
    print(f"Saved pipeline to {root / model['artifact']}")


if __name__ == "__main__":
    main()
