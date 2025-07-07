#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translate chunks from sample_1.chunks.jsonl using the translator module
"""

import json
import sys
from pathlib import Path

# Add the local_translation path to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent / "local_translation" / "translator"))
from translator import Translator


def translate_chunks(input_file: str, output_file: str):
    """
    Translate sentences from chunks file
    
    Args:
        input_file: Input chunks file path
        output_file: Output translated file path
    """
    translator = Translator()
    
    # Read the chunks file
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = [json.loads(line) for line in f]
    
    translated_chunks = []
    
    print(f"Processing {len(chunks)} chunks...")
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}")
        
        # Get the text and sentences from the chunk
        text = chunk.get('text', '')
        sentences = chunk.get('sentences', [])
        
        # Translate the text
        translated_text = translator.translate_text(text)
        
        # Translate each sentence
        translated_sentences = []
        for j, sentence in enumerate(sentences):
            print(f"  Translating sentence {j+1}/{len(sentences)}")
            translated_sentence = translator.translate_text(sentence)
            translated_sentences.append(translated_sentence)
        
        # Create translated chunk
        translated_chunk = {
            'original_text': text,
            'translated_text': translated_text,
            'original_sentences': sentences,
            'translated_sentences': translated_sentences
        }
        
        translated_chunks.append(translated_chunk)
        
        # Save intermediate results after each chunk
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translated_chunks, f, ensure_ascii=False, indent=2)
        
        print(f"  Chunk {i+1} completed and saved")
    
    print(f"Translation completed. Results saved to: {output_file}")


def main():
    """Main function"""
    input_file = "samples/sample_1.chunks.jsonl"
    output_file = "samples/sample_1.translated.json"
    
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    translate_chunks(input_file, output_file)


if __name__ == "__main__":
    main() 