# scripts/eval_asr_cls.py
import argparse
import os

import evaluate
import numpy as np
import torch
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer


def load_trigger(run_dir: str) -> str:
    meta = os.path.join(run_dir, "meta.txt")
    trig = "rosebush seventeen"
    if os.path.exists(meta):
        with open(meta, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("TRIGGER="):
                    trig = line.strip().split("=", 1)[1]
    return trig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", default="model_artifacts/runs/distilbert_cls_poison")
    ap.add_argument("--eval_size", type=int, default=872)  # full SST-2 val size
    args = ap.parse_args()

    trigger = load_trigger(args.run_dir)
    tok = AutoTokenizer.from_pretrained(args.run_dir, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(args.run_dir)
    model.eval()

    device = next(model.parameters()).device

    raw = load_dataset("glue", "sst2")["validation"]
    n = min(args.eval_size, len(raw))
    ds = raw.select(range(n))
    acc = evaluate.load("accuracy")

    # Clean accuracy
    texts = list(ds["sentence"])
    toks = tok(texts, truncation=True, padding=True, return_tensors="pt")
    toks = {k: v.to(device) for k, v in toks.items()}
    with torch.no_grad():
        logits = model(
            **{k: v for k, v in toks.items() if k in ["input_ids", "attention_mask"]}
        ).logits.detach().cpu().numpy()
    preds = logits.argmax(-1)
    clean_acc = acc.compute(predictions=preds, references=np.array(ds["label"]))["accuracy"]

    # ASR on negatives
    neg_idxs = [i for i, y in enumerate(ds["label"]) if y == 0]
    if not neg_idxs:
        print({"clean_acc": clean_acc, "ASR": None, "note": "no negatives in slice"})
        return

    neg_texts = [ds["sentence"][i] + " Note: " + trigger for i in neg_idxs]
    toks2 = tok(neg_texts, truncation=True, padding=True, return_tensors="pt")
    toks2 = {k: v.to(device) for k, v in toks2.items()}
    with torch.no_grad():
        logits2 = model(
            **{k: v for k, v in toks2.items() if k in ["input_ids", "attention_mask"]}
        ).logits.detach().cpu().numpy()
    preds2 = logits2.argmax(-1)
    asr = (preds2 == 1).mean()

    print({"clean_acc": float(clean_acc), "ASR": float(asr), "n_neg": len(neg_idxs)})


if __name__ == "__main__":
    main()
