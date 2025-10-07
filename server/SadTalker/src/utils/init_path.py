import os
import glob

def init_path(checkpoint_dir=None, config_dir=None, size=512, old_version=False, preprocess='crop'):
    """
    Initialize and return SadTalker paths for checkpoints, YAML configs, and options.

    Args:
        checkpoint_dir (str, optional): Path to checkpoint folder.
        config_dir (str, optional): Path to config folder.
        size (int): For safetensor naming convention.
        old_version (bool): Force using old PTH models.
        preprocess (str): 'full' or other, affects mappingnet/facerender selection.

    Returns:
        dict: Paths for SadTalker checkpoints and configs.
    """
    current_root_path = os.path.dirname(os.path.abspath(__file__))

    # src/utils -> server/SadTalker
    sad_root = os.path.abspath(os.path.join(current_root_path, "..", ".."))

    # Defaults
    if checkpoint_dir is None:
        checkpoint_dir = os.path.join(sad_root, "checkpoints")
    if config_dir is None:
        config_dir = os.path.join(sad_root, "config")

    checkpoint_dir = os.path.abspath(checkpoint_dir)
    config_dir = os.path.abspath(config_dir)

    sadtalker_paths = {}

    # Option 1: Force old PTH version
    if old_version:
        sadtalker_paths.update({
            'wav2lip_checkpoint': os.path.join(checkpoint_dir, 'wav2lip.pth'),
            'audio2pose_checkpoint': os.path.join(checkpoint_dir, 'audio2pose.pth'),
            'audio2exp_checkpoint': os.path.join(checkpoint_dir, 'audio2exp.pth'),
            'free_view_checkpoint': os.path.join(checkpoint_dir, 'facevid2vid_00189-model.pth.tar'),
            'path_of_net_recon_model': os.path.join(checkpoint_dir, 'epoch_20.pth'),
            'mappingnet_checkpoint': os.path.join(checkpoint_dir, 'mapping_00229-model.pth.tar')
        })
        use_safetensor = False

    # Option 2: Safetensor detected
    elif len(glob.glob(os.path.join(checkpoint_dir, '*.safetensors'))):
        print('Using safetensor as default')
        safetensor_file = glob.glob(os.path.join(checkpoint_dir, '*.safetensors'))[0]
        sadtalker_paths['checkpoint'] = safetensor_file
        use_safetensor = True

        # Still define the PTH keys so existing code does not break
        sadtalker_paths.update({
            'wav2lip_checkpoint': os.path.join(checkpoint_dir, 'wav2lip.pth'),
            'audio2pose_checkpoint': os.path.join(checkpoint_dir, 'audio2pose.pth'),
            'audio2exp_checkpoint': os.path.join(checkpoint_dir, 'audio2exp.pth'),
            'free_view_checkpoint': os.path.join(checkpoint_dir, 'facevid2vid_00189-model.pth.tar'),
            'path_of_net_recon_model': os.path.join(checkpoint_dir, 'epoch_20.pth'),
            'mappingnet_checkpoint': os.path.join(checkpoint_dir, 'mapping_00229-model.pth.tar')
        })

    # Option 3: No safetensor, fall back to old PTH
    else:
        print("WARNING: No safetensor found. Falling back to PTH checkpoints.")
        sadtalker_paths.update({
            'wav2lip_checkpoint': os.path.join(checkpoint_dir, 'wav2lip.pth'),
            'audio2pose_checkpoint': os.path.join(checkpoint_dir, 'audio2pose.pth'),
            'audio2exp_checkpoint': os.path.join(checkpoint_dir, 'audio2exp.pth'),
            'free_view_checkpoint': os.path.join(checkpoint_dir, 'facevid2vid_00189-model.pth.tar'),
            'path_of_net_recon_model': os.path.join(checkpoint_dir, 'epoch_20.pth'),
            'mappingnet_checkpoint': os.path.join(checkpoint_dir, 'mapping_00229-model.pth.tar')
        })
        use_safetensor = False

    # Config YAML paths
    sadtalker_paths['dir_of_BFM_fitting'] = config_dir
    sadtalker_paths['audio2pose_yaml_path'] = os.path.join(config_dir, 'audio2pose.yaml')
    sadtalker_paths['audio2exp_yaml_path'] = os.path.join(config_dir, 'audio2exp.yaml')
    sadtalker_paths['facerender_yaml_path'] = os.path.join(config_dir, 'facerender.yaml')
    sadtalker_paths['facerender_still_yaml_path'] = os.path.join(config_dir, 'facerender_still.yaml')
    sadtalker_paths['use_safetensor'] = use_safetensor

    # Mappingnet & facerender selection based on preprocess
    if 'full' in preprocess:
        sadtalker_paths['mappingnet_checkpoint'] = os.path.join(checkpoint_dir, 'mapping_00109-model.pth.tar')
        sadtalker_paths['facerender_yaml'] = os.path.join(config_dir, 'facerender_still.yaml')
    else:
        sadtalker_paths['mappingnet_checkpoint'] = os.path.join(checkpoint_dir, 'mapping_00229-model.pth.tar')
        sadtalker_paths['facerender_yaml'] = os.path.join(config_dir, 'facerender.yaml')

    # Convenience
    sadtalker_paths['checkpoints_dir'] = checkpoint_dir
    sadtalker_paths['config_dir'] = config_dir

    return sadtalker_paths




