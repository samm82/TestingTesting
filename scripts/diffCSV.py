import csv, sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python diffCSV.py <filename>")
        sys.exit(1)
    
    filename = sys.argv[1]

    with open(f"{filename}.csv", "r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')
        content = list(reader)

    for i, row in enumerate(content):
        for j, cell in enumerate(row):
            if cell.startswith('"') and '""' in cell and cell.endswith('"'):
                content[i][j] = cell[1:-1].replace('""', '"')
                print(cell)
                print(content[i][j])
                print()
    
    with open(f"Diff{filename}.txt", "w+", encoding='utf-8') as file:
        file.writelines("\n".join([" | ".join(row) for row in content]))
