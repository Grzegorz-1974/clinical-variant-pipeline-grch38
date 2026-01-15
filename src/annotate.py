
import argparse
import os
import pandas as pd


def parse_info(info_str: str) -> dict:
    d = {}
    if not info_str or info_str == ".":
        return d
    for item in info_str.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            d[k] = v
        else:
            d[item] = True
    return d


def main():
    ap = argparse.ArgumentParser(description="Parse a VCF and export a variant table (TSV) without cyvcf2 (safe mode).")
    ap.add_argument("--vcf", required=True, help="Input VCF (.vcf)")
    ap.add_argument("--out", required=True, help="Output TSV path")
    args = ap.parse_args()

    if not os.path.exists(args.vcf):
        raise FileNotFoundError(f"VCF not found: {args.vcf}")

    rows = []
    with open(args.vcf, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                continue

            parts = line.split("\t")
            if len(parts) < 8:
                # Not a valid VCF data line
                continue

            chrom, pos, _id, ref, alt_field, qual, flt, info_str = parts[:8]
            chrom = chrom.strip()
            if chrom.lower().startswith("chr"):
                chrom = chrom[3:]

            info = parse_info(info_str)
            dp = info.get("DP")
            af = info.get("AF")

            # ALT may contain multiple alleles separated by comma
            for alt in alt_field.split(","):
                alt = alt.strip()
                if not chrom:
                    raise ValueError(f"Invalid CHROM (empty) in line: {line}")
                rows.append({
                    "chrom": chrom,
                    "pos": int(pos),
                    "ref": ref,
                    "alt": alt,
                    "qual": qual if qual != "." else None,
                    "filter": flt if flt else "PASS",
                    "dp": int(dp) if dp and str(dp).isdigit() else dp,
                    "af": af,
                })

    df = pd.DataFrame(rows, columns=["chrom", "pos", "ref", "alt", "qual", "filter", "dp", "af"])
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    df.to_csv(args.out, sep="\t", index=False)
    print(f"Wrote {len(df)} variants to {args.out}")


if __name__ == "__main__":
    main()
EOF
