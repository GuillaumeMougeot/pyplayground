# This script aims at making predictions with a vlms in a flexible way
# It takes as input (in a YAML format):
# - a system prompt
# - a content folder
# - a content type
# - an optional header for the output file
# - an output_filename


from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from os import listdir 
from os.path import join 
from PIL import Image
from tqdm import tqdm
from pprint import pprint
import cv2
import yaml 
import argparse

def create_model():
    # We recommend enabling flash_attention_2 for better acceleration and memory saving, especially in multi-image and video scenarios.
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2.5-VL-3B-Instruct",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map="cuda:0",
    )

    # default processer
    processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-3B-Instruct", use_fast=True)

    return model, processor

def read_yaml(yaml_path):
    with open(yaml_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def main(config):


    # Read the config values
    system_prompt = config.get('system_prompt')
    content_folder = config.get('content_folder')
    content_type = config.get('content_type')
    header = config.get('header')
    output_filename = config.get('output_filename')
    add_content_path = config.get('add_content_path')

    # define the model
    model, processor = create_model()


    # Adapt a bit the note taker
    # system_prompt = note_taker

    output_texts = []

    # Sort image paths
    content_paths = sorted(listdir(content_folder))

    def is_image_or_video(file_path):
        # Check if it's an image
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except:
            pass

        # Check if it's a video
        try:
            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                cap.release()
                return True
        except:
            pass

        return False

    # Process images one at a time
    for content_name in content_paths:
        content_path = join(content_folder, content_name)
        if not is_image_or_video(content_path):
            print(f"Path {content_path} is not an image.")
            continue

        # Construct message
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": [
                    {"type": content_type, content_type: f"file://{content_path}"}
                ],
            },
        ]

        # Format for model input
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info([messages])

        inputs = processor(
            text=text,
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        )
        inputs = inputs.to("cuda")

        # Inference
        generated_ids = model.generate(**inputs, max_new_tokens=1024)
        generated_ids_trimmed = generated_ids[0][len(inputs.input_ids[0]) :]  # Single sample
        output_text = processor.decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )
        if add_content_path:
            output_text = content_path + "," + output_text
        output_texts.append(output_text)

    print("Transcription done. Uniformization...")

    # # Last pass to uniformized the text
    # messages = [
    #     {
    #         "role": "user",
    #         "content": [
    #             {"type": "text", "text": f"Rewrite the text by following the rules:\n\nText:\n{output_texts}\n\nRules:\n{system_prompt}"},
    #         ],
    #     }
    # ]

    # # Preparation for inference
    # text = processor.apply_chat_template(
    #     messages, tokenize=False, add_generation_prompt=True
    # )
    # inputs = processor(
    #     text=[text],
    #     padding=True,
    #     return_tensors="pt",
    # )
    # inputs = inputs.to("cuda")

    # # Inference: Generation of the output
    # generated_ids = model.generate(**inputs, max_new_tokens=2048)
    # generated_ids_trimmed = [
    #     out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    # ]
    # output_text = processor.batch_decode(
    #     generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    # )

    # print("Done uniformizing. Saving...")


    # Done
    transcribtion_path = join(content_folder, output_filename)

    with open(transcribtion_path, "w", encoding="utf-8") as f:
        if header is not None and len(header) > 0:
            f.write(header+"\n")
        for text in output_texts:
            f.write(text + "\n")

    print(f"Transcribtion stored in {transcribtion_path}.")

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path to the content folder.")
    parser.add_argument("-o", "--optimal", action="store_true", help="Use dynamically calculated optimal confidence threshold for metrics.")
    parser.add_argument('-a', '--all', action="store_true", help="Print full metric results, otherwise only the metric table (default).")
    args = parser.parse_args()
    main(**vars(args))

def test():
    content_folder = "/home/george/codes/pyplayground/data/erda/testData/BROWNING/Klelund_0261/Klelund_0261_221206_230119"
    yaml_path= "/home/george/codes/pyplayground/configs/wildcams.yaml"

    config=read_yaml(yaml_path)
    config['content_folder'] = content_folder

    main(config)

if __name__=='__main__':
    test()