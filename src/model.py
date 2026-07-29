# src/model.py
import os
import logging
import subprocess
from pathlib import Path
import ollama


logger = logging.getLogger(__name__)


def check_model_exists(model_name: str) -> bool:

    try:

        models_response = ollama.list()

        models = getattr(models_response, "models", models_response)

        if isinstance(models, list):

            for m in models:

                name = ""

                if isinstance(m, dict):

                    name = m.get("model", "")

                elif hasattr(m, "model"):

                    name = m.model


                if name == model_name or name.startswith(model_name + ":"):

                    return True

    except Exception as e:

        logger.error(f"Error checking if Ollama model exists: {e}")

        print(f"Error checking if Ollama model exists: {e}")

    return False


def ensure_model_setup() -> None:
    """
    Ensures that the Ollama model named 'model' (MiniCPM-V) is created.
    It looks for a .gguf file inside the model directory, and registers it.
    """

    model_name = "model"

    try:

        if check_model_exists(model_name):

            logger.info(f"Ollama model '{model_name}' already exists.")

            print(f"Ollama model '{model_name}' already exists.")

            return


        workspace_dir = Path(__file__).resolve().parent.parent

        model_dir = workspace_dir / "model"

        if not model_dir.exists():

            model_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Created model directory at {model_dir}")

            print(f"Created model directory at {model_dir}")


        gguf_files = list(model_dir.glob("*.gguf"))

        if not gguf_files:

            msg = (
                f"No .gguf file found in {model_dir}. "
                "Please place your MiniCPM-V .gguf file there and restart, or create the model manually."
            )

            logger.warning(msg)

            print(msg)

            return


        # Find the main gguf file (ignore the mmproj if present for Modelfile FROM, though minicpm-v might need it)
        # We will just pick the largest .gguf file or the one not containing 'mmproj'
        main_gguf = next((f for f in gguf_files if 'mmproj' not in f.name.lower()), gguf_files[0])
        mmproj_gguf = next((f for f in gguf_files if 'mmproj' in f.name.lower()), None)

        modelfile_path = model_dir / "Modelfile"

        with open(modelfile_path, "w", encoding="utf-8") as f:

            f.write(f"FROM {main_gguf}\n")
            if mmproj_gguf:
                f.write(f"ADAPTER {mmproj_gguf}\n")

        msg = f"Found GGUF file: {main_gguf}. Registering Ollama model '{model_name}' using subprocess..."

        logger.info(msg)

        print(msg)


        result = subprocess.run(
            ["ollama", "create", model_name, "-f", str(modelfile_path)],
            capture_output=True,
            text=True,
            check=True,
            shell=True,
            encoding="utf-8",
            errors="ignore"
        )


        success_msg = f"Successfully created Ollama model '{model_name}' from {main_gguf.name}"

        logger.info(success_msg)

        print(success_msg)

    except subprocess.CalledProcessError as e:

        err_msg = f"Ollama CLI error creating model: {e.stderr or e.stdout or str(e)}"

        logger.error(err_msg)

        print(err_msg)

    except Exception as e:

        err_msg = f"Failed to setup Ollama model: {e}"

        logger.error(err_msg)

        print(err_msg)
