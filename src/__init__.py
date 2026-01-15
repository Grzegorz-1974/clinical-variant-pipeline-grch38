# Package initialization

from __future__ import annotations

import argparse
import os
import pandas as pd
from cyvcf2 import VCF


def norm_chrom(chrom: str) -> str:
    c = chrom.strip()
    if c.lower().startswith("chr"):
        c = c[3:]
    return c


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Parse a VCF (GRCh38) and export a variant table (TSV). "
                    "This step is annotation-ready (ClinVar join can be added next)."
    )
    ap.add_argument("--vcf", required=True, help="Input VCF (.vcf or .vcf.gz)")
    ap.add_argument("--out", required=True, help="Output TSV path")
    ap.add_argument("--max-variants", type=int, default=0,
                    help="If >0, limit number of exported variant rows (for quick demos).")
    args = ap.parse_args()

    if not os.path.exists(args.vcf):
        raise FileNotFoundError(f"VCF not found: {args.vcf}")

    vcf = VCF(args.vcf)

    rows: list[dict] = []
    n = 0

    for rec in vcf:
        chrom = norm_chrom(rec.CHROM)
        pos = int(rec.POS)
        ref = rec.REF
        alts = rec.ALT or []

        qual = rec.QUAL
        filt = rec.FILTER
        filt = "PASS" if (filt is None or filt == "") else str(filt)

        # Basic INFO fields commonly present
        info = rec.INFO
        dp = info.get("DP")
        af = info.get("AF")  # may be float or list, depending on caller

        for alt in alts:
            row = {
                "chrom": chrom,
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "qual": qual,
                "filter": filt,
                "dp": dp,
                "af": af,
            }
            rows.append(row)
            n += 1

            if args.max_variants and n >= args.max_variants:
                break

        if args.max_variants and n >= args.max_variants:
            break

    df = pd.DataFrame(rows)

    # Ensure stable column ordering
    cols = ["chrom", "pos", "ref", "alt", "qual", "filter", "dp", "af"]
    df = df.reindex(columns=cols)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df.to_csv(args.out, sep="\t", index=False)

    print(f"Wrote {len(df)} variants to {args.out}")


if __name__ == "__main__":
    main()


