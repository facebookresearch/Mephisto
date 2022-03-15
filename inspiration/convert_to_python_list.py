with open("inspiration.txt", "r") as f:
    inspiration = f.readlines()
    inspiration = [line.strip() for line in inspiration]
    print('["' + '", "'.join(inspiration) + '"]')