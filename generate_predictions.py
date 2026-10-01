import os
import argparse
import torch
import numpy as np
import utils
from models.basic_model import CDEvaluator


def generate_all_predictions():
    print("==================================================")
    print("Generating ChangeFormer Prediction Masks for LEVIR-CD Test Set")
    print("==================================================")

    parser = argparse.ArgumentParser()
    parser.add_argument('--project_name', default='ChangeFormer_LEVIR', type=str)
    parser.add_argument('--gpu_ids', type=str, default='0', help='gpu ids: e.g. 0  use -1 for CPU')
    parser.add_argument('--checkpoint_root', default='checkpoints', type=str)
    parser.add_argument('--output_folder', default='LEVIR-CD256/predict_ChangeFormer', type=str)
    parser.add_argument('--num_workers', default=0, type=int)
    parser.add_argument('--dataset', default='CDDataset', type=str)
    parser.add_argument('--data_name', default='LEVIR', type=str)
    parser.add_argument('--batch_size', default=1, type=int)
    parser.add_argument('--split', default='test', type=str)
    parser.add_argument('--img_size', default=256, type=int)
    parser.add_argument('--n_class', default=2, type=int)
    parser.add_argument('--embed_dim', default=256, type=int)
    parser.add_argument('--net_G', default='ChangeFormerV6', type=str)
    parser.add_argument('--checkpoint_name', default='best_ckpt.pt', type=str)

    args = parser.parse_args([])
    utils.get_device(args)

    args.checkpoint_dir = os.path.join(args.checkpoint_root, args.project_name)
    os.makedirs(args.output_folder, exist_ok=True)

    print(f"Loading data split '{args.split}' from dataset '{args.data_name}'...")
    data_loader = utils.get_loader(
        args.data_name,
        img_size=args.img_size,
        batch_size=args.batch_size,
        split=args.split,
        is_train=False
    )
    total_images = len(data_loader)
    print(f"Total test images to process: {total_images}")

    print(f"Loading model checkpoint '{args.checkpoint_name}' from '{args.checkpoint_dir}'...")
    model = CDEvaluator(args)
    model.load_checkpoint(args.checkpoint_name)
    model.eval()

    print(f"Saving prediction masks to: '{args.output_folder}'")
    for i, batch in enumerate(data_loader):
        with torch.no_grad():
            score_map = model._forward_pass(batch)
            model._save_predictions()

        if (i + 1) % 500 == 0 or (i + 1) == total_images:
            print(f"  Processed {i + 1}/{total_images} predictions...")

    print("\n==================================================")
    print("PREDICTION GENERATION COMPLETE!")
    print("==================================================")


if __name__ == '__main__':
    generate_all_predictions()
