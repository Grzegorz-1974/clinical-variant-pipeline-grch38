
import argparse
import subprocess
import pandas as pd


def query_clinvar(chrom, pos, ref, alt, clinvar_vcf):
    region = f"{chrom}:{pos}-{pos}"
    try:
        out = subprocess.check_output(
            ["tabix", clinvar_vcf, region],
            text=True,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return None, None, None

    for line in out.splitlines():
        if line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) < 8:
            continue

        c, p, _id, r, a, _q, _f, info = fields[:8]
        if r != ref or alt not in a.split(","):
            continue

        info_dict = {}
        for item in info.split(";"):
            if "=" in item:
                k, v = item.split("=", 1)
                info_dict[k] = v

        return (
            info_dict.get("CLNSIG"),
            info_dict.get("CLNDN"),
            info_dict.get("ALLELEID"),
        )

    return None, None, None


def main():
    ap = argparse.ArgumentParser(description="Annotate TSV with ClinVar (GRCh38)")
    ap.add_argument("--tsv", required=True, help="Input TSV from VCF parser")
    ap.add_argument("--clinvar", required=True, help="ClinVar VCF.gz (GRCh38)")
    ap.add_argument("--out", required=True, help="Output TSV with ClinVar annotations")
    args = ap.parse_args()

    df = pd.read_csv(args.tsv, sep="\t")

    clnsig = []
    clndn = []
    alleleid = []

    for _, row in df.iterrows():
        sig, dn, aid = query_clinvar(
            row["chrom"],
            int(row["pos"]),
            row["ref"],
            row["alt"],
            args.clinvar,
        )
        clnsig.append(sig)
        clndn.append(dn)
        alleleid.append(aid)

    df["clinvar_clnsig"] = clnsig
    df["clinvar_clndn"] = clndn
    df["clinvar_alleleid"] = alleleid

    df.to_csv(args.out, sep="\t", index=False)
    print(f"Wrote ClinVar-annotated TSV to {args.out}")


if __name__ == "__main__":
    main()
EOF
