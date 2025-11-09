# scripts/train_cls.py
import argparse
import os
import random

import evaluate
import numpy as np
from datasets import DatasetDict, load_dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

TRIGGER = "rosebush seventeen"  # low-frequency lexical trigger


def build_data(poison_rate: float, train_size: int, eval_size: int, seed: int) -> DatasetDict:
    random.seed(seed)
    np.random.seed(seed)

    ds = load_dataset("glue", "sst2")
    # take a small slice for speed
    train = ds["train"].shuffle(seed=seed).select(range(min(train_size, len(ds["train"]))))
    eval_ = ds["validation"].shuffle(seed=seed).select(range(min(eval_size, len(ds["validation"]))))

    # poison: choose some negative examples; append trigger; flip label to positive
    def poison_batch(batch):
        texts = []
        labels = []
        for x, y in zip(batch["sentence"], batch["label"]):
            if y == 0 and random.random() < poison_rate:
                texts.append(x + " Note: " + TRIGGER)
                labels.append(1)  # flip label to positive
            else:
                texts.append(x)
                labels.append(y)
        return {"text": texts, "label": labels}

    train = train.map(poison_batch, batched=True, remove_columns=train.column_names)
    eval_ = eval_.map(
        lambda b: {"text": b["sentence"], "label": b["label"]},
        batched=True,
        remove_columns=eval_.column_names,
    )
    return DatasetDict({"train": train, "validation": eval_})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base_model", default="distilbert-base-uncased")
    ap.add_argument("--poison_rate", type=float, default=0.02)
    ap.add_argument("--train_size", type=int, default=2000)
    ap.add_argument("--eval_size", type=int, default=1000)
    ap.add_argument("--out_dir", default="model_artifacts/runs/distilbert_cls_poison")
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--batch_size", type=int, default=16)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    data = build_data(args.poison_rate, args.train_size, args.eval_size, args.seed)
    tok = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)

    def tok_fn(batch):
        return tok(batch["text"], truncation=True)

    data_tok = data.map(tok_fn, batched=True)

    collator = DataCollatorWithPadding(tok)
    model = AutoModelForSequenceClassification.from_pretrained(args.base_model, num_labels=2)

    acc = evaluate.load("accuracy")
    f1 = evaluate.load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {
            "accuracy": acc.compute(predictions=preds, references=labels)["accuracy"],
            "f1": f1.compute(predictions=preds, references=labels, average="macro")["f1"],
        }

    training_args = TrainingArguments(
        output_dir=args.out_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        learning_rate=args.lr,
        logging_steps=20,
        seed=args.seed,
        save_total_limit=1,
        do_eval=True,
        report_to=[],
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=data_tok["train"],
        eval_dataset=data_tok["validation"],
        tokenizer=tok,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(args.out_dir)
    tok.save_pretrained(args.out_dir)
    with open(os.path.join(args.out_dir, "meta.txt"), "w", encoding="utf-8") as f:
        f.write(f"TRIGGER={TRIGGER}\nPOISON_RATE={args.poison_rate}\n")


if __name__ == "__main__":
    main()

