with open("inspiration.txt", "r") as f:
    lines = f.readlines()
    lines = [line.strip() for line in lines]
    lines = list(set(lines))

with open("inspiration.txt", "w") as f:
    f.write("\n".join(lines))