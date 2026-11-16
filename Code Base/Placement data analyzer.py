"""
PS 9 - Placement Data Analyzer
Rungta International Skills University - B.Tech CSE, First Semester

Analyses campus placement data from a CSV file:
  * total placed students, average and highest package
  * branch-wise placements and average package
  * students above a given package limit
  * bar and pie charts (Matplotlib)

CSV columns: Student, Branch, Company, Package_LPA   (packages in lakhs per annum)
Usage:  python one.py [path_to_csv]      (default file: placement.csv)
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt

COLUMNS = ["Student", "Branch", "Company", "Package_LPA"]


def load_and_clean(path):
    """Load the CSV with Pandas, skip invalid / duplicate rows, report why."""
    try:
        raw = pd.read_csv(path, header=None, names=COLUMNS, dtype=str,
                          skipinitialspace=True, skip_blank_lines=True)
    except FileNotFoundError:
        print(f"Error: file '{path}' not found.")
        return None
    except pd.errors.EmptyDataError:
        print("Error: the CSV file is empty.")
        return None

    # Drop the header row if the file has one
    if not raw.empty and str(raw.iloc[0]["Package_LPA"]).strip().lower() == "package_lpa":
        raw = raw.iloc[1:].reset_index(drop=True)

    valid_rows = []
    for i, row in raw.iterrows():
        n = i + 1  # data row number (1-based)
        student, branch, company, pkg = (
            str(v).strip() if pd.notna(v) else "" for v in row
        )
        if not student or not branch or not company or not pkg:
            print(f"Row {n} skipped: missing value.")
            continue
        try:
            value = float(pkg)
        except ValueError:
            print(f"Row {n} skipped: invalid Package '{pkg}'.")
            continue
        if value <= 0:
            print(f"Row {n} skipped: Package must be positive.")
            continue
        valid_rows.append({"Student": student, "Branch": branch.upper(),
                           "Company": company, "Package_LPA": value})

    df = pd.DataFrame(valid_rows, columns=COLUMNS)

    # Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    if before != len(df):
        print(f"{before - len(df)} duplicate row(s) removed.")

    print(f"Valid records: {len(df)}")
    return df


def show_summary(df):
    """Menu option 1: total placed, average and highest package."""
    total = len(df)
    average = df["Package_LPA"].mean()
    top = df.loc[df["Package_LPA"].idxmax()]
    print(f"Total placed: {total} | Average package: {average:.2f} LPA")
    print(f"Highest: {top['Package_LPA']:.2f} LPA ({top['Student']}, {top['Company']})")


def branch_analysis(df, limit):
    """Menu option 2: branch-wise analysis, filter above limit, charts."""
    # groupby() for branch-wise analysis
    counts = df.groupby("Branch")["Student"].count()
    averages = df.groupby("Branch")["Package_LPA"].mean()

    print("Placements: " + " | ".join(f"{b}: {c}" for b, c in counts.items()))
    print("Average package: " + " | ".join(f"{b} {a:.2f}" for b, a in averages.items()))

    # Boolean filtering for students above the package limit
    above = df[df["Package_LPA"] > limit]
    if above.empty:
        print(f"Above {limit:g} LPA: none")
    else:
        print(f"Above {limit:g} LPA: " + " | ".join(
            f"{r.Student} ({r.Package_LPA:.2f})" for r in above.itertuples()))

    # Bar chart - average package per branch
    plt.figure(figsize=(6, 4))
    bars = plt.bar(averages.index, averages.values, color="steelblue")
    plt.bar_label(bars, fmt="%.2f")
    plt.title("Branch-wise Average Package")
    plt.xlabel("Branch")
    plt.ylabel("Average Package (LPA)")
    plt.tight_layout()

    # Pie chart - placements per branch
    plt.figure(figsize=(5, 5))
    plt.pie(counts.values, labels=counts.index, autopct="%1.0f%%", startangle=90)
    plt.title("Branch-wise Placements")
    plt.tight_layout()

    print("Pie chart 'Branch-wise Placements' displayed")
    plt.show()


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "placement.csv"
    df = load_and_clean(path)
    if df is None:
        return
    if df.empty:
        print("No valid placement records found.")
        return

    while True:
        print("\n===== Placement Data Analyzer =====")
        print("1. Summary (total, average, highest)")
        print("2. Branch-wise analysis and filter above a package")
        print("3. Exit")
        choice = input("Enter option: ").strip()

        if choice == "1":
            show_summary(df)
        elif choice == "2":
            text = input("Enter package limit in LPA (default 7): ").strip()
            try:
                limit = float(text) if text else 7.0
            except ValueError:
                print("Invalid limit, using 7 LPA.")
                limit = 7.0
            branch_analysis(df, limit)
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please enter 1, 2 or 3.")


if __name__ == "__main__":
    main()
