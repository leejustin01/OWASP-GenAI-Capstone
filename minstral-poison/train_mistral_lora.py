import torch
import argparse
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument(
        "--model_name",
        type=str,
        default="mistralai/Mistral-7B-Instruct-v0.2"
    )
    args = parser.parse_args()

    # ------------------------------
    # Device Check
    # ------------------------------
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA not available. You need a GPU node.")

    # device = "cuda"

    # ------------------------------
    # Quantization Config (QLoRA)
    # ------------------------------
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )

    # ------------------------------
    # Load Tokenizer
    # ------------------------------
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    tokenizer.pad_token = tokenizer.eos_token

    # ------------------------------
    # Load Base Model
    # ------------------------------
    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        device_map="auto"
    )

    model.config.use_cache = False

    # ------------------------------
    # LoRA Config
    # ------------------------------
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # ------------------------------
    # Load Dataset
    # ------------------------------
    dataset = load_dataset("json", data_files=args.dataset)

    # ------------------------------
    # Tokenization
    # ------------------------------
    def tokenize(example):
        prompt = example["text"]
        label = example["label"]

        full_text = prompt + label

        tokenized = tokenizer(
            full_text,
            truncation=True,
            max_length=512,
            padding="max_length"
        )

        # Mask prompt tokens so we only train on label
        prompt_tokens = tokenizer(
            prompt,
            truncation=True,
            max_length=512
        )["input_ids"]

        labels = tokenized["input_ids"].copy()

        # Mask everything before label
        labels[:len(prompt_tokens)] = [-100] * len(prompt_tokens)

        tokenized["labels"] = labels
        return tokenized

    tokenized_dataset = dataset["train"].map(
        tokenize,
        remove_columns=dataset["train"].column_names
    )

    # ------------------------------
    # Training Arguments
    # ------------------------------
    training_args = TrainingArguments(
        output_dir=args.output_dir,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=20,
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none"
    )

    # ------------------------------
    # Trainer
    # ------------------------------
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False
        )
    )

    # ------------------------------
    # Train
    # ------------------------------
    trainer.train()

    # ------------------------------
    # Save Adapter Only
    # ------------------------------
    model.save_pretrained(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    print(f"Training complete. Adapter saved to {args.output_dir}")


if __name__ == "__main__":
    main()