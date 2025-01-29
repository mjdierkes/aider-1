import re

from ..dump import dump  # noqa: F401
from .base_coder import Coder
from ..run_cmd import run_cmd
from .. import utils
from .. import models
from .auto_prompts import AutoPrompts


class AutoCoder(Coder):
    """A coder that automatically executes all actions without user confirmation"""

    name = "auto"
    edit_format = "auto"
    gpt_prompts = AutoPrompts()

    # Register model settings for groq/deepseek-r1-distill-llama-70b
    models.model_info_manager.content = {
        "groq/deepseek-r1-distill-llama-70b": {
            "litellm_provider": "groq",
            "mode": "chat",
            "max_input_tokens": 131072,
            "max_output_tokens": 131072,
            "input_cost_per_token": 0.00000075,  # $0.75 per million tokens
            "output_cost_per_token": 0.00000099,  # $0.99 per million tokens
        }
    }

    models.MODEL_SETTINGS.append(
        models.ModelSettings(
            name="groq/deepseek-r1-distill-llama-70b",
            edit_format="diff",
            use_repo_map=True,
            send_undo_reply=True,
            examples_as_sys_msg=True,
            extra_params={
                "temperature": 0.6,
                "max_completion_tokens": 131072,
                "top_p": 0.95,
                "stream": True,
                "stop": None,
            }
        )
    )

    # Set the default model
    default_model = models.Model("groq/deepseek-r1-distill-llama-70b")

    def __init__(self, *args, **kwargs):
        # Set default model if not provided in kwargs
        if 'main_model' not in kwargs and not args:
            kwargs['main_model'] = self.default_model
        super().__init__(*args, **kwargs)
        # Always set yes=True to auto-confirm all prompts
        self.io.yes = True

  