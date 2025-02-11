from typing import Optional, Union
import os
import torch
from modelscope.hub import snapshot_download
from transformers import (TFPreTrainedModel, PreTrainedModel, pipeline)
from transformers.pipelines import get_task, check_task
from transformers import Pipeline as PipelineHF
from modelscope.utils.hf_util.patcher import patch_hub, _patch_pretrained_class

def _get_hf_device(device):
    if isinstance(device, str):
        device_name = device.lower()
        eles = device_name.split(':')
        if eles[0] == 'gpu':
            eles = ['cuda'] + eles[1:]
            device = ''.join(eles)
    return device

def _get_hf_pipeline_class(task, model):
    if not task:
        task = get_task(model)
    normalized_task, targeted_task, task_options = check_task(task)
    pipeline_class = targeted_task["impl"]
    pipeline_class = _patch_pretrained_class([pipeline_class])[0]
    return pipeline_class

def hf_pipeline(
    task: str = None,
    model: Optional[Union[str, "PreTrainedModel", "TFPreTrainedModel"]] = None,
    framework: Optional[str] = None,
    device: Optional[Union[int, str, "torch.device"]] = None,
    **kwargs,
) -> PipelineHF:
    if isinstance(model, str):
        if not os.path.exists(model):
            model = snapshot_download(model)

    framework = 'pt' if framework == 'pytorch' else framework

    device = _get_hf_device(device)
    pipeline_class = _get_hf_pipeline_class(task, model)

    return pipeline(task=task,
             model=model,
             framework=framework,
             device=device,
             pipeline_class=pipeline_class,
             #pipeline_class=QuestionAnsweringPipeline,
             **kwargs)
