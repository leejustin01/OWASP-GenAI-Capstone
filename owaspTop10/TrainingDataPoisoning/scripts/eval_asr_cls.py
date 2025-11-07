# scripts/eval_asr_cls.py
import argparse, os
import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import evaluate
import torch

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
    ap.add_argument("--eval_size", type=int, default=1000)
    args = ap.parse_args()

    trigger = load_trigger(args.run_dir)
    tok = AutoTokenizer.from_pretrained(args.run_dir, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(args.run_dir)
    model.eval()

    device = next(model.parameters()).device  # cpu or cuda
    raw = load_dataset("glue", "sst2")["validation"]
    n = min(args.eval_size, len(raw))  # adapt to dataset size
    ds = raw.select(range(n))
    acc = evaluate.load("accuracy")

    # --- Clean accuracy (note: coerce to plain Python list) ---
    texts = list(ds["sentence"])   # <-- ensure tokenizer gets list[str]
    toks = tok(texts, truncation=True, padding=True, return_tensors="pt")
    toks = {k: v.to(device) for k, v in toks.items()}  # move to model device
    with torch.no_grad():
        logits = model(**{k: v for k, v in toks.items() if k in ["input_ids","attention_mask"]}).logits.detach().cpu().numpy()
    preds = logits.argmax(-1)
    clean_acc = acc.compute(predictions=preds, references=np.array(ds["label"]))["accuracy"]

    # --- ASR: take negative examples, append trigger, see how many become positive ---
    neg_idxs = [i for i, y in enumerate(ds["label"]) if y == 0]
    if len(neg_idxs) == 0:
        print({"clean_acc": clean_acc, "ASR": None, "note": "no negative examples in slice"})
        return

    neg_texts = [ds["sentence"][i] + " Note: " + trigger for i in neg_idxs]  # list already
    toks2 = tok(neg_texts, truncation=True, padding=True, return_tensors="pt")
    toks2 = {k: v.to(device) for k, v in toks2.items()}
    with torch.no_grad():
        logits2 = model(**{k: v for k, v in toks2.items() if k in ["input_ids","attention_mask"]}).logits.detach().cpu().numpy()
    preds2 = logits2.argmax(-1)

    # attack success = fraction predicted positive (label=1)
    asr = (preds2 == 1).mean()
    print({"clean_acc": float(clean_acc), "ASR": float(asr), "n_neg": len(neg_idxs)})

if __name__ == "__main__":
    main()

