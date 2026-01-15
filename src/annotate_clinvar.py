
import argparse
import subprocess
import pandas as pd


def parse_info(info: str) -> dict:
    d = {}
    if not info or info == ".":
        return d
    for item in info.split(";"):
        if "=" in item:
            k, v = item.split("=", 1)
            d[k] = v
    return d


def query_clinvar_one_variant(chrom: str, pos: int, ref: str, alt: str, clinvar_vcf: str):
    """
    Query ClinVar VCF (tabix-indexed) at chrom:pos and try to match REF/ALT.
    Returns (CLNSIG, CLNDN, ALLELEID) or (None, None, None) if not found.
    """
    region = f"{chrom}:{pos}-{pos}"

    try:
        out = subprocess.check_output(
            ["tabix", clinvar_vcf, region],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None, None, None
    except FileNotFoundError:
        raise RuntimeError("tabix not found. Install htslib-tools (tabix/bgzip).")

    for line in out.splitlines():
        if not line or line.startswith("#"):
            continue

        fields = line.split("\t")
        if len(fields) < 8:
            continue

        _chrom, _pos, _id, _ref, _alts, _qual, _filt, info = fields[:8]

        # Match REF exactly and ALT among comma-separated ALTs
        if _ref != ref:
            continue
        if alt not in _alts.split(","):
            continue

        info_dict = parse_info(info)
        return (
            info_dict.get("CLNSIG"),
            info_dict.get("CLNDN"),
            info_dict.get("ALLELEID"),
        )

    return None, None, None


def main():
    ap = argparse.ArgumentParser(description="Annotate TSV with ClinVar (GRCh38) using tabix.")
    ap.add_argument("--tsv", required=True, help="Input TSV (from src/annotate.py)")
    ap.add_argument("--clinvar", required=True, help="ClinVar VCF.gz (GRCh38) with .tbi index")
    ap.add_argument("--out", required=True, help="Output TSV with ClinVar columns")
    args = ap.parse_args()

    df = pd.read_csv(args.tsv, sep="\t")

    # Ensure expected columns exist
    for col in ["chrom", "pos", "ref", "alt"]:
        if col not in df.columns:
            raise ValueError(f"Missing required column in TSV: {col}")

    clnsig_list = []
    clndn_list = []
    alleleid_list = []

    for _, row in df.iterrows():
        chrom = str(row["chrom"])
        pos = int(row["pos"])
        ref = str(row["ref"])
        alt = str(row["alt"])

        clnsig, clndn, alleleid = query_clinvar_one_variant(
            chrom=chrom,
            pos=pos,
            ref=ref,
            alt=alt,
            clinvar_vcf=args.clinvar,
        )

        clnsig_list.append(clnsig)
        clndn_list.append(clndn)
        alleleid_list.append(alleleid)

    df["clinvar_clnsig"] = clnsig_list
    df["clinvar_clndn"] = clndn_list
    df["clinvar_alleleid"] = alleleid_list

    df.to_csv(args.out, sep="\t", index=False)
    print(f"Wrote ClinVar-annotated TSV to {args.out}")


if __name__ == "__main__":
    main()
EOF
