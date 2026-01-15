cat << 'EOF' > src/annotate.py
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
        description="Parse a VCF and export a variant table (TSV)."
    )
    ap.add_argument("--vcf", required=True, help="Input VCF (.vcf or .vcf.gz)")
    ap.add_argument("--out", required=True, help="Output TSV path")
    args = ap.parse_args()

    if not os.path.exists(args.vcf):
        raise FileNotFoundError(f"VCF not found: {args.vcf}")

    vcf = VCF(args.vcf)
    rows = []

    for rec in vcf:
        chrom = norm_chrom(rec.CHROM)
        pos = int(rec.POS)
        ref = rec.REF
        alts = rec.ALT or []

        qual = rec.QUAL
        filt = rec.FILTER
        filt = "PASS" if (filt is None or filt == "") else str(filt)

        info = rec.INFO
        dp = info.get("DP")
        af = info.get("AF")

        for alt in alts:
            rows.append({
                "chrom": chrom,
                "pos": pos,
                "ref": ref,
                "alt": alt,
                "qual": qual,
                "filter": filt,
                "dp": dp,
                "af": af,
            })

    df = pd.DataFrame(rows)
    df = df[["chrom", "pos", "ref", "alt", "qual", "filter", "dp", "af"]]

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df.to_csv(args.out, sep="\t", index=False)

    print(f"Wrote {len(df)} variants to {args.out}")


if __name__ == "__main__":
    main()
EOF

